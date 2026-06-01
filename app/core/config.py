from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_RSS_FEED_URLS = ",".join(
    (
        "https://weworkremotely.com/categories/remote-programming-jobs.rss",
        "https://remoteok.com/remote-jobs.rss",
    )
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AIFOS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Freelancer Operating System"
    env: str = "development"
    database_url: str = "sqlite:///./data/aifos.db"
    analyst_threshold: float = 7.0
    analyst_provider: str = "auto"
    proposal_provider: str = "auto"
    worker_provider: str = "auto"
    portfolio_markdown_path: str = "portfolio/operator_portfolio.md"
    workspace_storage_path: str = "storage/workspaces"
    proposal_max_words: int = 120
    worker_max_repair_attempts: int = 2
    scout_api_base_url: str = "http://127.0.0.1:8001"
    scout_interval_seconds: int = 900
    scout_limit_per_source: int = 25
    rss_feed_urls: str = DEFAULT_RSS_FEED_URLS
    upwork_rss_urls: str = ""
    reddit_subreddits: str = "forhire,freelance_forhire"
    reddit_user_agent: str = "windows:ai-freelancer-os:v0.1 (by /u/dancru299)"
    gmail_imap_host: str = "imap.gmail.com"
    gmail_imap_port: int = 993
    gmail_email: str | None = None
    gmail_app_password: str | None = Field(default=None, validation_alias=AliasChoices("AIFOS_GMAIL_APP_PASSWORD", "GMAIL_APP_PASSWORD"))
    gmail_mailbox: str = "INBOX"
    gmail_alert_subjects: str = "Upwork Job Alert,LinkedIn Job Alert"
    gmail_search_window_days: int = 2
    gmail_mark_seen: bool = False

    telegram_bot_token: str | None = None
    telegram_default_chat_id: str | None = None
    telegram_webhook_secret: str | None = None
    telegram_api_base: str = "https://api.telegram.org"
    # How the bot receives button taps: "webhook" (needs a public HTTPS URL) or
    # "polling" (the app pulls updates itself; works behind NAT / on a laptop).
    telegram_mode: str = "webhook"

    gemini_api_key: str | None = Field(default=None, validation_alias=AliasChoices("AIFOS_GEMINI_API_KEY", "GEMINI_API_KEY"))
    gemini_model: str = Field(default="gemini-2.5-flash", validation_alias=AliasChoices("AIFOS_GEMINI_MODEL", "GEMINI_MODEL"))

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    allow_mock_llm: bool = True

    # Background task dispatch: "background" (FastAPI BackgroundTasks, zero-infra) or "arq" (Redis-backed).
    task_backend: str = "background"
    redis_url: str = "redis://localhost:6379/0"

    # Admin UI auth. When admin_password is unset, /admin is restricted to localhost.
    admin_username: str = "admin"
    admin_password: str | None = None

    # Structured JSON logging for production; plain logging when false.
    json_logs: bool = False

    # Expose Prometheus metrics at /metrics when true.
    metrics_enabled: bool = False

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def resolved_portfolio_path(self) -> Path:
        return (self.project_root / self.portfolio_markdown_path).resolve()

    @property
    def resolved_workspace_storage_path(self) -> Path:
        return (self.project_root / self.workspace_storage_path).resolve()

    @property
    def telegram_enabled(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_default_chat_id)

    @property
    def gmail_inbox_enabled(self) -> bool:
        return bool(self.gmail_email and self.gmail_app_password)

    @property
    def parsed_gmail_alert_subjects(self) -> list[str]:
        return _split_config_list(self.gmail_alert_subjects)

    @property
    def parsed_rss_feed_urls(self) -> list[str]:
        return _split_config_list(self.rss_feed_urls)

    @property
    def parsed_upwork_rss_urls(self) -> list[str]:
        return _split_config_list(self.upwork_rss_urls)

    @property
    def parsed_reddit_subreddits(self) -> list[str]:
        return _split_config_list(self.reddit_subreddits)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def _split_config_list(value: str) -> list[str]:
    normalized = value.replace("\n", ",").replace(";", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]
