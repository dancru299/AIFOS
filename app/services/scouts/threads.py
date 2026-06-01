"""Threads Scout: poll a curated whitelist of target profiles for job posts.

Threads has no public keyword-search API, but the official Graph API exposes a
Profile Discovery endpoint that returns a public profile's recent posts by
username (``GET /{version}/{node}/profile_posts?username=...``). We watch a
hand-picked list of high-signal accounts (founders, indie hackers, hiring hubs),
keep only posts whose text matches hiring keywords, and submit the rest as jobs.

Access notes (see README / .env):
- Reading non-Meta profiles requires **Advanced Access** via App Review; with
  Standard Access the endpoint only returns Meta's own accounts.
- Targets must have >=100 followers; the endpoint allows max 1,000 requests per
  rolling 24h. One request == one profile, so keep
  ``len(targets) * cycles_per_day <= 1000``.

The exact endpoint shape is configurable (``api_base``/``api_version``/``node``);
confirm against current Meta docs and adjust ``AIFOS_THREADS_*`` if Meta changes
it. Parsing/filtering below is what the unit tests pin down.
"""

import logging
from collections.abc import Iterable

import httpx

from app.services.scouts.types import ScoutJob

logger = logging.getLogger(__name__)

THREADS_POST_FIELDS = "id,permalink,text,timestamp,username"


class ThreadsScout:
    def __init__(
        self,
        access_token: str,
        usernames: Iterable[str],
        keywords: Iterable[str] | None = None,
        *,
        node: str = "me",
        api_base: str = "https://graph.threads.net",
        api_version: str = "v1.0",
        limit_per_user: int = 25,
    ) -> None:
        self.access_token = access_token
        self.usernames = [u.strip().lstrip("@") for u in usernames if u.strip()]
        self.keywords = [k.strip().lower() for k in (keywords or []) if k.strip()]
        self.node = node.strip() or "me"
        self.api_base = api_base.rstrip("/")
        self.api_version = api_version.strip("/")
        self.limit_per_user = limit_per_user

    @property
    def endpoint(self) -> str:
        return f"{self.api_base}/{self.api_version}/{self.node}/profile_posts"

    async def fetch_jobs(self) -> list[ScoutJob]:
        jobs: list[ScoutJob] = []
        if not self.access_token or not self.usernames:
            return jobs
        async with httpx.AsyncClient(timeout=30.0) as client:
            for username in self.usernames:
                # One bad/private/over-limit profile must not sink the whole run.
                try:
                    posts = await self._fetch_user_posts(client, username)
                except Exception as exc:
                    logger.warning("Threads profile fetch failed for @%s: %s", username, exc)
                    continue
                for post in posts:
                    job = parse_threads_post(post, username, self.keywords)
                    if job:
                        jobs.append(job)
        return jobs

    async def _fetch_user_posts(self, client: httpx.AsyncClient, username: str) -> list[dict]:
        params = {
            "username": username,
            "fields": THREADS_POST_FIELDS,
            "limit": self.limit_per_user,
            "access_token": self.access_token,
        }
        response = await client.get(self.endpoint, params=params)
        response.raise_for_status()
        return response.json().get("data", []) or []


def post_matches_keywords(text: str, keywords: list[str]) -> bool:
    """No keywords configured -> keep everything and let the Analyst score ROI."""
    if not keywords:
        return True
    low = text.lower()
    return any(keyword in low for keyword in keywords)


def parse_threads_post(post: dict, username: str, keywords: list[str] | None = None) -> ScoutJob | None:
    text = str(post.get("text") or "").strip()
    if not text or not post_matches_keywords(text, keywords or []):
        return None

    post_id = str(post.get("id") or "").strip()
    handle = str(post.get("username") or username).lstrip("@")
    permalink = str(post.get("permalink") or "").strip()
    external_url = permalink or (f"https://www.threads.net/@{handle}/post/{post_id}" if post_id else "")
    if not external_url:
        return None

    snippet = text if len(text) <= 80 else text[:77] + "..."
    return ScoutJob(
        source="threads",
        external_url=external_url,
        title=f"Threads @{handle}: {snippet}",
        description_raw=text,
        client_metadata={
            "threads_username": handle,
            "post_id": post_id,
            "timestamp": post.get("timestamp"),
        },
    )
