from collections.abc import Iterable

from app.services.scouts.rss import RssScout, parse_rss_entry
from app.services.scouts.types import ScoutJob


class UpworkScout(RssScout):
    def __init__(self, rss_urls: Iterable[str], limit_per_feed: int = 25) -> None:
        super().__init__(rss_urls, limit_per_feed=limit_per_feed)


def parse_upwork_entry(entry, rss_url: str = "") -> ScoutJob | None:
    return parse_rss_entry(entry, rss_url, source="upwork")
