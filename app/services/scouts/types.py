from dataclasses import dataclass, field
from typing import Any, Literal


ScoutSource = Literal[
    "upwork",
    "linkedin",
    "reddit",
    "x",
    "rss",
    "weworkremotely",
    "remoteok",
    "hackernews",
]


@dataclass
class ScoutJob:
    source: ScoutSource
    external_url: str
    title: str
    description_raw: str
    budget_raw: str | None = None
    client_location: str | None = None
    client_metadata: dict[str, Any] = field(default_factory=dict)

    def to_ingest_payload(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "external_url": self.external_url,
            "title": self.title,
            "description_raw": self.description_raw,
            "budget_raw": self.budget_raw,
            "client_location": self.client_location,
            "client_metadata": self.client_metadata,
        }
