import asyncio
import logging
from dataclasses import dataclass

import httpx

from app.core.config import Settings
from app.services.scouts.gmail_fetcher import GmailInboxScout
from app.services.scouts.reddit import RedditScout
from app.services.scouts.rss import RssScout
from app.services.scouts.types import ScoutJob


logger = logging.getLogger(__name__)


@dataclass
class ScoutRunResult:
    fetched: int = 0
    submitted: int = 0
    duplicates: int = 0
    errors: int = 0


class ScoutRunner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def run_once(self) -> ScoutRunResult:
        jobs = await self.fetch_all()
        result = ScoutRunResult(fetched=len(jobs))

        async with httpx.AsyncClient(timeout=30.0) as client:
            for job in jobs:
                try:
                    response = await client.post(
                        f"{self.settings.scout_api_base_url.rstrip('/')}/api/v1/jobs/ingest",
                        json=job.to_ingest_payload(),
                    )
                    response.raise_for_status()
                    payload = response.json()
                    result.submitted += 1
                    if payload.get("status") != "pending":
                        result.duplicates += 1
                except Exception:
                    result.errors += 1
                    logger.exception("Failed to submit scout job: %s", job.external_url)

        return result

    async def fetch_all(self) -> list[ScoutJob]:
        jobs: list[ScoutJob] = []

        if self.settings.gmail_inbox_enabled:
            try:
                jobs.extend(
                    await GmailInboxScout(
                        email_address=self.settings.gmail_email or "",
                        app_password=self.settings.gmail_app_password or "",
                        host=self.settings.gmail_imap_host,
                        port=self.settings.gmail_imap_port,
                        mailbox=self.settings.gmail_mailbox,
                        subject_filters=self.settings.parsed_gmail_alert_subjects,
                        search_window_days=self.settings.gmail_search_window_days,
                        limit=self.settings.scout_limit_per_source,
                        mark_seen=self.settings.gmail_mark_seen,
                    ).fetch_jobs()
                )
            except Exception:
                logger.exception("Gmail inbox scout failed.")

        if self.settings.parsed_rss_feed_urls:
            try:
                jobs.extend(
                    await RssScout(
                        self.settings.parsed_rss_feed_urls,
                        limit_per_feed=self.settings.scout_limit_per_source,
                    ).fetch_jobs()
                )
            except Exception:
                logger.exception("RSS scout failed.")

        if self.settings.parsed_reddit_subreddits:
            try:
                jobs.extend(
                    await RedditScout(
                        self.settings.parsed_reddit_subreddits,
                        user_agent=self.settings.reddit_user_agent,
                        limit_per_subreddit=self.settings.scout_limit_per_source,
                    ).fetch_jobs()
                )
            except Exception as exc:
                logger.warning("Reddit scout failed: %s", exc)

        return _dedupe(jobs)

    async def run_forever(self) -> None:
        while True:
            result = await self.run_once()
            logger.info("Scout run complete: %s", result)
            await asyncio.sleep(self.settings.scout_interval_seconds)


def _dedupe(jobs: list[ScoutJob]) -> list[ScoutJob]:
    seen: set[str] = set()
    deduped: list[ScoutJob] = []
    for job in jobs:
        if job.external_url in seen:
            continue
        seen.add(job.external_url)
        deduped.append(job)
    return deduped
