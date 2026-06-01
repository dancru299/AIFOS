import asyncio
import imaplib
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email import message_from_bytes, policy
from email.header import decode_header, make_header
from email.message import Message
from email.utils import parsedate_to_datetime
from html import unescape
from urllib.parse import parse_qs, parse_qsl, quote, unquote, urlencode, urlparse, urlunparse

from bs4 import BeautifulSoup

from app.services.scouts.types import ScoutJob, ScoutSource


@dataclass(frozen=True)
class EmailJobLink:
    url: str
    text: str
    context: str


class GmailInboxScout:
    def __init__(
        self,
        *,
        email_address: str,
        app_password: str,
        host: str = "imap.gmail.com",
        port: int = 993,
        mailbox: str = "INBOX",
        subject_filters: Iterable[str] = ("Upwork Job Alert", "LinkedIn Job Alert"),
        search_window_days: int = 2,
        limit: int = 25,
        mark_seen: bool = False,
    ) -> None:
        self.email_address = email_address.strip()
        self.app_password = app_password
        self.host = host.strip() or "imap.gmail.com"
        self.port = port
        self.mailbox = mailbox.strip() or "INBOX"
        self.subject_filters = [item.strip() for item in subject_filters if item.strip()]
        self.search_window_days = max(search_window_days, 1)
        self.limit = limit
        self.mark_seen = mark_seen

    async def fetch_jobs(self) -> list[ScoutJob]:
        return await asyncio.to_thread(self._fetch_jobs_sync)

    def _fetch_jobs_sync(self) -> list[ScoutJob]:
        if not self.email_address or not self.app_password:
            return []

        jobs: list[ScoutJob] = []
        mail = imaplib.IMAP4_SSL(self.host, self.port)
        try:
            mail.login(self.email_address, self.app_password)
            status, _ = mail.select(self.mailbox, readonly=not self.mark_seen)
            if status != "OK":
                raise RuntimeError(f"Unable to select Gmail mailbox: {self.mailbox}")

            since_date = (datetime.now(UTC) - timedelta(days=self.search_window_days)).strftime("%d-%b-%Y")
            message_ids = _search_message_ids(mail, since_date, self.subject_filters)
            if not message_ids:
                return []

            for message_id in reversed(message_ids[-self.limit * 10 :]):
                status, message_data = mail.fetch(message_id, "(RFC822)")
                if status != "OK":
                    continue

                raw_message = _first_message_payload(message_data)
                if not raw_message:
                    continue

                message = message_from_bytes(raw_message, policy=policy.default)
                message_jobs = parse_job_alert_email(
                    message,
                    subject_filters=self.subject_filters,
                    source_email=self.email_address,
                )
                if not message_jobs:
                    continue

                jobs.extend(message_jobs)
                if self.mark_seen:
                    mail.store(message_id, "+FLAGS", "\\Seen")
                if len(jobs) >= self.limit:
                    break

            return jobs[: self.limit]
        finally:
            try:
                mail.logout()
            except Exception:
                pass


def parse_job_alert_email(
    message: Message,
    *,
    subject_filters: Iterable[str] = ("Upwork Job Alert", "LinkedIn Job Alert"),
    source_email: str | None = None,
) -> list[ScoutJob]:
    subject = _decode_header_value(message.get("subject", ""))
    filters = [item.strip().lower() for item in subject_filters if item.strip()]
    if filters and not any(item in subject.lower() for item in filters):
        return []

    html_body, text_body = _extract_message_bodies(message)
    body_text = _html_to_text(html_body) if html_body else _clean_text(text_body)
    links = _extract_job_links(html_body, text_body)
    if not links:
        return []

    jobs: list[ScoutJob] = []
    seen: set[str] = set()
    for link in links:
        if link.url in seen:
            continue
        seen.add(link.url)

        source = _source_from_url(link.url)
        description = _description_for_link(link.context, body_text)
        title = _title_for_link(link.text, description, subject)
        if not title or not description:
            continue

        jobs.append(
            ScoutJob(
                source=source,
                external_url=link.url,
                title=title,
                description_raw=description,
                budget_raw=_extract_budget(f"{title}\n{description}"),
                client_location=_extract_location(f"{title}\n{description}"),
                client_metadata={
                    "collector": "gmail_inbox",
                    "email_subject": subject,
                    "email_date": _message_date(message),
                    "message_id": message.get("Message-ID"),
                    "source_email": source_email,
                    "link_text": link.text,
                },
            )
        )
    return jobs


def _first_message_payload(message_data) -> bytes | None:
    for item in message_data:
        if isinstance(item, tuple) and isinstance(item[1], bytes):
            return item[1]
    return None


def _search_message_ids(mail: imaplib.IMAP4_SSL, since_date: str, subject_filters: list[str]) -> list[str]:
    message_ids: set[bytes] = set()
    search_failed = False

    for subject in subject_filters:
        status, data = mail.search(None, "SINCE", since_date, "SUBJECT", f'"{subject}"')
        if status != "OK":
            search_failed = True
            continue
        if data:
            message_ids.update(data[0].split())

    if message_ids or not search_failed:
        return _sorted_decoded(message_ids)

    status, data = mail.search(None, "SINCE", since_date)
    if status != "OK" or not data:
        return []
    return _sorted_decoded(set(data[0].split()))


def _sorted_decoded(message_ids: set[bytes]) -> list[str]:
    return [value.decode() for value in sorted(message_ids, key=lambda value: int(value))]


def _decode_header_value(value: str) -> str:
    try:
        return str(make_header(decode_header(value))).strip()
    except Exception:
        return str(value or "").strip()


def _extract_message_bodies(message: Message) -> tuple[str, str]:
    html_parts: list[str] = []
    text_parts: list[str] = []

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            disposition = str(part.get("Content-Disposition", "")).lower()
            if "attachment" in disposition:
                continue
            _append_body_part(part, html_parts, text_parts)
    else:
        _append_body_part(message, html_parts, text_parts)

    return "\n".join(html_parts), "\n".join(text_parts)


def _append_body_part(part: Message, html_parts: list[str], text_parts: list[str]) -> None:
    content_type = part.get_content_type()
    payload = _decode_part_payload(part)

    if content_type == "text/html":
        html_parts.append(payload)
    elif content_type == "text/plain":
        text_parts.append(payload)


def _decode_part_payload(part: Message) -> str:
    get_content = getattr(part, "get_content", None)
    if callable(get_content):
        try:
            return str(get_content())
        except Exception:
            pass
    raw_payload = part.get_payload(decode=True)
    if isinstance(raw_payload, bytes):
        charset = part.get_content_charset() or "utf-8"
        return raw_payload.decode(charset, errors="replace")
    return str(raw_payload or "")


def _extract_job_links(html_body: str, text_body: str) -> list[EmailJobLink]:
    candidates: list[EmailJobLink] = []

    if html_body:
        soup = BeautifulSoup(html_body, "html.parser")
        for anchor in soup.find_all("a", href=True):
            url = _canonicalize_job_url(str(anchor.get("href") or ""))
            if not url or not _is_supported_job_url(url):
                continue
            link_text = _clean_text(anchor.get_text(" ", strip=True))
            context_node = anchor.find_parent(["tr", "table", "td", "div", "li", "p"]) or anchor.parent
            context = _clean_text(context_node.get_text(" ", strip=True)) if context_node else link_text
            candidates.append(EmailJobLink(url=url, text=link_text, context=context))

    for raw_url in re.findall(r"https?://[^\s<>\"]+", text_body or ""):
        url = _canonicalize_job_url(raw_url)
        if url and _is_supported_job_url(url):
            candidates.append(EmailJobLink(url=url, text="", context=_near_text_url_context(text_body, raw_url)))

    return candidates


def _canonicalize_job_url(raw_url: str) -> str | None:
    if not raw_url:
        return None

    url = unescape(raw_url).strip().strip(").,;\"'")
    url = _unwrap_redirect_url(url)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None

    host = parsed.netloc.lower()
    path = unquote(parsed.path)
    if "linkedin.com" in host:
        match = re.search(r"/jobs/view/(\d+)", path)
        if match:
            return f"https://www.linkedin.com/jobs/view/{match.group(1)}/"
    if "upwork.com" in host and "/jobs/" in path:
        safe_path = quote(path, safe="/~_-")
        return urlunparse(("https", parsed.netloc, safe_path, "", "", ""))

    query = urlencode(
        [
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if not key.lower().startswith("utm_") and key.lower() not in {"trk", "trackingid", "refid"}
        ]
    )
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", query, ""))


def _unwrap_redirect_url(url: str) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    for key in ("url", "u", "q"):
        value = query.get(key)
        if value and value[0].startswith("http"):
            return unquote(value[0])
    return url


def _is_supported_job_url(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    return ("upwork.com" in host and "/jobs/" in path) or ("linkedin.com" in host and "/jobs/view" in path)


def _source_from_url(url: str) -> ScoutSource:
    host = urlparse(url).netloc.lower()
    if "linkedin.com" in host:
        return "linkedin"
    if "upwork.com" in host:
        return "upwork"
    return "rss"


def _description_for_link(context: str, body_text: str) -> str:
    description = context if len(context) >= 40 else body_text
    return description[:4000].strip()


def _title_for_link(link_text: str, description: str, subject: str) -> str:
    generic_text = {
        "apply",
        "apply now",
        "view job",
        "view details",
        "see job",
        "see details",
        "learn more",
    }
    clean_link_text = _clean_text(link_text)
    if clean_link_text and clean_link_text.lower() not in generic_text and len(clean_link_text) <= 160:
        return clean_link_text

    for line in re.split(r"[\n|•]+", description):
        candidate = _clean_text(line)
        if not candidate or candidate.lower() in generic_text:
            continue
        if candidate.startswith("http") or len(candidate) < 6 or len(candidate) > 160:
            continue
        if re.fullmatch(r"[\$,\d\s./hrkK+-]+", candidate):
            continue
        return candidate

    fallback = re.sub(r"(?i)\b(?:upwork|linkedin)\s+job\s+alert\b\s*:?", "", subject).strip(" -:")
    return fallback or "Job alert opportunity"


def _near_text_url_context(text: str, raw_url: str) -> str:
    index = text.find(raw_url)
    if index < 0:
        return _clean_text(text)
    start = max(index - 700, 0)
    end = min(index + len(raw_url) + 700, len(text))
    return _clean_text(text[start:end].replace(raw_url, " "))


def _html_to_text(html_body: str) -> str:
    soup = BeautifulSoup(unescape(html_body), "html.parser")
    return _clean_text(soup.get_text("\n", strip=True))


def _clean_text(value: str) -> str:
    compact = re.sub(r"\s+", " ", unescape(value or ""))
    return compact.strip()


def _extract_budget(text: str) -> str | None:
    patterns = (
        r"Budget\s*:?\s*(\$[\d,]+(?:\s*(?:-|to)\s*\$?[\d,]+)?(?:\s*/\s*(?:hr|hour))?)",
        r"Fixed(?:-price)?\s*:?\s*(\$[\d,]+(?:\s*(?:-|to)\s*\$?[\d,]+)?)",
        r"Hourly\s*:?\s*(\$[\d,]+(?:\s*(?:-|to)\s*\$?[\d,]+)?(?:\s*/\s*(?:hr|hour))?)",
        r"((?:USD|US\$)\s*[\d,]+(?:\s*(?:-|to)\s*[\d,]+)?)",
        r"(\$[\d,]+(?:\s*(?:-|to)\s*\$?[\d,]+)?(?:\s*/\s*(?:hr|hour))?)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_location(text: str) -> str | None:
    lower_text = text.lower()
    known_locations = {
        "united states": "United States",
        "usa": "United States",
        "us only": "United States",
        "canada": "Canada",
        "united kingdom": "United Kingdom",
        "uk": "United Kingdom",
        "australia": "Australia",
        "europe": "Europe",
        "eu": "Europe",
        "remote": "Remote",
    }
    for token, location in known_locations.items():
        if re.search(rf"\b{re.escape(token)}\b", lower_text):
            return location
    return None


def _message_date(message: Message) -> str | None:
    raw_date = message.get("date")
    if not raw_date:
        return None
    try:
        return parsedate_to_datetime(raw_date).isoformat()
    except Exception:
        return raw_date
