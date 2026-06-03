from pathlib import Path

from app.core.config import get_settings

MANAGED_KEYS = {
    "AIFOS_ANALYST_PROVIDER",
    "AIFOS_PROPOSAL_PROVIDER",
    "AIFOS_WORKER_PROVIDER",
    "AIFOS_DEEPSEEK_API_KEY",
    "DEEPSEEK_API_KEY",
    "AIFOS_DEEPSEEK_MODEL",
    "AIFOS_DEEPSEEK_MODEL_LIGHT",
    "AIFOS_DEEPSEEK_BASE_URL",
    "GEMINI_API_KEY",
    "AIFOS_GEMINI_API_KEY",
    "AIFOS_GEMINI_MODEL",
    "AIFOS_OPENAI_API_KEY",
    "AIFOS_OPENAI_MODEL",
    "AIFOS_ANTHROPIC_API_KEY",
    "AIFOS_ANTHROPIC_MODEL",
    "AIFOS_TELEGRAM_BOT_TOKEN",
    "AIFOS_TELEGRAM_DEFAULT_CHAT_ID",
    "AIFOS_TELEGRAM_WEBHOOK_SECRET",
    "AIFOS_SCOUT_API_BASE_URL",
    "AIFOS_SCOUT_INTERVAL_SECONDS",
    "AIFOS_SCOUT_LIMIT_PER_SOURCE",
    "AIFOS_RSS_FEED_URLS",
    "AIFOS_UPWORK_RSS_URLS",
    "AIFOS_REDDIT_SUBREDDITS",
    "AIFOS_REDDIT_USER_AGENT",
    "AIFOS_GMAIL_IMAP_HOST",
    "AIFOS_GMAIL_IMAP_PORT",
    "AIFOS_GMAIL_EMAIL",
    "AIFOS_GMAIL_APP_PASSWORD",
    "AIFOS_GMAIL_MAILBOX",
    "AIFOS_GMAIL_ALERT_SUBJECTS",
    "AIFOS_GMAIL_SEARCH_WINDOW_DAYS",
    "AIFOS_GMAIL_MARK_SEEN",
}


def env_path() -> Path:
    return get_settings().project_root / ".env"


def read_env_values() -> dict[str, str]:
    path = env_path()
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value
    return values


def update_env_values(updates: dict[str, str]) -> None:
    safe_updates = {key: value for key, value in updates.items() if key in MANAGED_KEYS}
    if not safe_updates:
        return

    path = env_path()
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    seen: set[str] = set()
    output: list[str] = []

    for line in lines:
        if not line or line.lstrip().startswith("#") or "=" not in line:
            output.append(line)
            continue

        key, _ = line.split("=", 1)
        key = key.strip()
        if key in safe_updates:
            output.append(f"{key}={safe_updates[key]}")
            seen.add(key)
        else:
            output.append(line)

    missing = [key for key in safe_updates if key not in seen]
    if missing:
        if output and output[-1] != "":
            output.append("")
        for key in missing:
            output.append(f"{key}={safe_updates[key]}")

    path.write_text("\n".join(output) + "\n", encoding="utf-8")
    get_settings.cache_clear()


def masked(value: str | None) -> str:
    if not value:
        return "missing"
    if len(value) <= 8:
        return "set"
    return f"{value[:4]}...{value[-4:]}"
