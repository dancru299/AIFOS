import re
from collections.abc import Iterable

import httpx

from app.services.scouts.types import ScoutJob


class RedditScout:
    def __init__(self, subreddits: Iterable[str], user_agent: str, limit_per_subreddit: int = 25) -> None:
        self.subreddits = [subreddit.strip().strip("/") for subreddit in subreddits if subreddit.strip()]
        self.user_agent = user_agent
        self.limit_per_subreddit = limit_per_subreddit

    async def fetch_jobs(self) -> list[ScoutJob]:
        jobs: list[ScoutJob] = []
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
            for subreddit in self.subreddits:
                response = await self._get_subreddit_json(client, subreddit)
                for child in response.json().get("data", {}).get("children", []):
                    job = parse_reddit_child(child, subreddit)
                    if job:
                        jobs.append(job)
        return jobs

    async def _get_subreddit_json(self, client: httpx.AsyncClient, subreddit: str) -> httpx.Response:
        params = {"limit": self.limit_per_subreddit, "raw_json": 1}
        urls = (
            f"https://www.reddit.com/r/{subreddit}/new/.json",
            f"https://old.reddit.com/r/{subreddit}/new/.json",
        )
        last_response: httpx.Response | None = None
        for url in urls:
            response = await client.get(url, params=params)
            if response.status_code < 400:
                return response
            last_response = response
        assert last_response is not None
        last_response.raise_for_status()
        return last_response


def parse_reddit_child(child: dict, subreddit: str) -> ScoutJob | None:
    data = child.get("data") or {}
    title = str(data.get("title") or "").strip()
    permalink = str(data.get("permalink") or "").strip()
    selftext = str(data.get("selftext") or "").strip()
    url = str(data.get("url") or "").strip()

    if not title or not permalink:
        return None

    external_url = f"https://www.reddit.com{permalink}"
    description = selftext or url or title

    return ScoutJob(
        source="reddit",
        external_url=external_url,
        title=title,
        description_raw=description,
        budget_raw=_extract_budget(f"{title}\n{description}"),
        client_location=_extract_location(f"{title}\n{description}"),
        client_metadata={
            "subreddit": subreddit,
            "reddit_id": data.get("id"),
            "author": data.get("author"),
            "created_utc": data.get("created_utc"),
            "score": data.get("score"),
            "num_comments": data.get("num_comments"),
        },
    )


def _extract_budget(text: str) -> str | None:
    match = re.search(r"(\$[\d,]+(?:\s*-\s*\$?[\d,]+)?|USD\s*[\d,]+(?:\s*-\s*[\d,]+)?)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _extract_location(text: str) -> str | None:
    match = re.search(r"\b(?:US|USA|United States|Canada|UK|United Kingdom|Australia|Europe|EU)\b", text, re.IGNORECASE)
    if match:
        value = match.group(0)
        return "United States" if value.lower() in {"us", "usa", "united states"} else value
    return None
