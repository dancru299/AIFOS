import re
from collections.abc import Iterable
from html import unescape
from urllib.parse import urlparse

import feedparser
import httpx
from bs4 import BeautifulSoup

from app.services.scouts.types import ScoutJob, ScoutSource


class RssScout:
    def __init__(self, rss_urls: Iterable[str], limit_per_feed: int = 25) -> None:
        self.rss_urls = [url.strip() for url in rss_urls if url.strip()]
        self.limit_per_feed = limit_per_feed

    async def fetch_jobs(self) -> list[ScoutJob]:
        jobs: list[ScoutJob] = []
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for rss_url in self.rss_urls:
                response = await client.get(rss_url, headers={"User-Agent": "AI-Freelancer-OS/0.1"})
                response.raise_for_status()
                parsed = feedparser.parse(response.text)
                for entry in parsed.entries[: self.limit_per_feed]:
                    job = parse_rss_entry(entry, rss_url)
                    if job:
                        jobs.append(job)
        return jobs


def parse_rss_entry(entry, rss_url: str = "", source: ScoutSource | None = None) -> ScoutJob | None:
    title = _clean_text(getattr(entry, "title", ""))
    external_url = getattr(entry, "link", "") or getattr(entry, "id", "")
    description = _entry_description(entry)

    if not title or not external_url or not description:
        return None

    detected_source = source or _detect_source(rss_url, external_url)
    return ScoutJob(
        source=detected_source,
        external_url=external_url,
        title=title,
        description_raw=description,
        budget_raw=_extract_budget(f"{title}\n{description}"),
        client_location=_extract_location(f"{title}\n{description}"),
        client_metadata={
            "rss_url": rss_url,
            "published": getattr(entry, "published", None),
            "entry_id": getattr(entry, "id", None),
        },
    )


def _detect_source(rss_url: str, entry_url: str = "") -> ScoutSource:
    combined_hosts = " ".join(
        urlparse(value).netloc.lower()
        for value in (rss_url, entry_url)
        if value
    )
    if "weworkremotely.com" in combined_hosts:
        return "weworkremotely"
    if "remoteok.com" in combined_hosts:
        return "remoteok"
    if "news.ycombinator.com" in combined_hosts or "hackernews" in combined_hosts or "hnrss" in combined_hosts:
        return "hackernews"
    if "upwork.com" in combined_hosts:
        return "upwork"
    if "linkedin.com" in combined_hosts:
        return "linkedin"
    return "rss"


def _entry_description(entry) -> str:
    parts: list[str] = []
    for attr in ("summary", "description"):
        value = getattr(entry, attr, None)
        if value:
            parts.append(str(value))
    for content_item in getattr(entry, "content", []) or []:
        value = content_item.get("value")
        if value:
            parts.append(str(value))
    return _clean_text("\n".join(parts))


def _clean_text(value: str) -> str:
    soup = BeautifulSoup(unescape(value), "html.parser")
    compact = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    return compact.strip()


def _extract_budget(text: str) -> str | None:
    patterns = (
        r"Budget\s*:?\s*(\$[\d,]+(?:\s*(?:-|to)\s*\$?[\d,]+)?)",
        r"Fixed(?:-price)?\s*:?\s*(\$[\d,]+(?:\s*(?:-|to)\s*\$?[\d,]+)?)",
        r"Salary\s*:?\s*(\$[\d,]+(?:\s*(?:-|to)\s*\$?[\d,]+)?)",
        r"((?:USD|US\$)\s*[\d,]+(?:\s*(?:-|to)\s*[\d,]+)?)",
        r"(\$[\d,]+(?:\s*(?:-|to)\s*\$?[\d,]+)?)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def _extract_location(text: str) -> str | None:
    lower_text = text.lower()
    known_locations = {
        "remote": "Remote",
        "united states": "United States",
        "usa": "United States",
        "us only": "United States",
        "canada": "Canada",
        "united kingdom": "United Kingdom",
        "uk": "United Kingdom",
        "australia": "Australia",
        "europe": "Europe",
        "eu": "Europe",
        "germany": "Germany",
        "france": "France",
    }
    for token, location in known_locations.items():
        if re.search(rf"\b{re.escape(token)}\b", lower_text):
            return location

    patterns = (
        r"Country\s*:?\s*([A-Za-z][A-Za-z\s,&.-]{1,60})",
        r"Location\s*:?\s*([A-Za-z][A-Za-z\s,&.-]{1,60})",
        r"Client\s+Location\s*:?\s*([A-Za-z][A-Za-z\s,&.-]{1,60})",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip(" .,-")
    return None
