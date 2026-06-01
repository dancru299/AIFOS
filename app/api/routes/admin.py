import secrets
from html import escape
from secrets import token_urlsafe

import httpx
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.core.config import DEFAULT_RSS_FEED_URLS, get_settings
from app.services.env_file import masked, read_env_values, update_env_values

router = APIRouter(tags=["admin"])

ANALYST_PROVIDERS = ("auto", "gemini", "openai", "mock")
PROPOSAL_PROVIDERS = ("auto", "gemini", "anthropic", "openai", "mock")
WORKER_PROVIDERS = ("auto", "gemini", "anthropic", "openai", "mock")

# Hosts allowed to reach /admin when no admin password is configured.
_LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost", "testclient"}
_basic_auth = HTTPBasic(auto_error=False)


def require_admin(request: Request, credentials: HTTPBasicCredentials | None = Depends(_basic_auth)) -> None:
    """Guard the admin UI. Requires HTTP Basic auth when AIFOS_ADMIN_PASSWORD is set;
    otherwise restricts access to loopback callers only."""
    settings = get_settings()

    if not settings.admin_password:
        host = request.client.host if request.client else ""
        if host in _LOOPBACK_HOSTS:
            return
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin password is not set; remote access to /admin is disabled.",
        )

    valid = (
        credentials is not None
        and secrets.compare_digest(credentials.username, settings.admin_username)
        and secrets.compare_digest(credentials.password, settings.admin_password)
    )
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )


@router.get("/admin", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
async def admin_page(request: Request, saved: str | None = None, webhook_url: str | None = None) -> HTMLResponse:
    settings = get_settings()
    env_values = read_env_values()
    webhook_info = await _get_webhook_info(settings.telegram_bot_token)

    content = _render_admin_page(
        analyst_provider=env_values.get("AIFOS_ANALYST_PROVIDER", settings.analyst_provider),
        proposal_provider=env_values.get("AIFOS_PROPOSAL_PROVIDER", settings.proposal_provider),
        worker_provider=env_values.get("AIFOS_WORKER_PROVIDER", settings.worker_provider),
        gemini_model=env_values.get("AIFOS_GEMINI_MODEL", settings.gemini_model),
        openai_model=env_values.get("AIFOS_OPENAI_MODEL", settings.openai_model),
        anthropic_model=env_values.get("AIFOS_ANTHROPIC_MODEL", settings.anthropic_model),
        telegram_chat_id=env_values.get("AIFOS_TELEGRAM_DEFAULT_CHAT_ID", settings.telegram_default_chat_id or ""),
        telegram_secret=env_values.get("AIFOS_TELEGRAM_WEBHOOK_SECRET", settings.telegram_webhook_secret or ""),
        scout_api_base_url=env_values.get("AIFOS_SCOUT_API_BASE_URL", settings.scout_api_base_url),
        scout_interval_seconds=env_values.get("AIFOS_SCOUT_INTERVAL_SECONDS", str(settings.scout_interval_seconds)),
        scout_limit_per_source=env_values.get("AIFOS_SCOUT_LIMIT_PER_SOURCE", str(settings.scout_limit_per_source)),
        rss_feed_urls=env_values.get("AIFOS_RSS_FEED_URLS", settings.rss_feed_urls),
        gmail_imap_host=env_values.get("AIFOS_GMAIL_IMAP_HOST", settings.gmail_imap_host),
        gmail_imap_port=env_values.get("AIFOS_GMAIL_IMAP_PORT", str(settings.gmail_imap_port)),
        gmail_email=env_values.get("AIFOS_GMAIL_EMAIL", settings.gmail_email or ""),
        gmail_app_password=env_values.get("AIFOS_GMAIL_APP_PASSWORD") or settings.gmail_app_password,
        gmail_mailbox=env_values.get("AIFOS_GMAIL_MAILBOX", settings.gmail_mailbox),
        gmail_alert_subjects=env_values.get("AIFOS_GMAIL_ALERT_SUBJECTS", settings.gmail_alert_subjects),
        gmail_search_window_days=env_values.get("AIFOS_GMAIL_SEARCH_WINDOW_DAYS", str(settings.gmail_search_window_days)),
        reddit_subreddits=env_values.get("AIFOS_REDDIT_SUBREDDITS", settings.reddit_subreddits),
        reddit_user_agent=env_values.get("AIFOS_REDDIT_USER_AGENT", settings.reddit_user_agent),
        gemini_key=env_values.get("GEMINI_API_KEY") or env_values.get("AIFOS_GEMINI_API_KEY"),
        openai_key=env_values.get("AIFOS_OPENAI_API_KEY"),
        anthropic_key=env_values.get("AIFOS_ANTHROPIC_API_KEY"),
        telegram_token=env_values.get("AIFOS_TELEGRAM_BOT_TOKEN"),
        saved=saved == "1",
        webhook_url=webhook_url,
        webhook_info=webhook_info,
        base_url=str(request.base_url).rstrip("/"),
    )
    return HTMLResponse(content)


@router.post("/admin/settings", dependencies=[Depends(require_admin)])
async def update_admin_settings(
    analyst_provider: str = Form("auto"),
    proposal_provider: str = Form("auto"),
    worker_provider: str = Form("auto"),
    gemini_model: str = Form("gemini-2.5-flash"),
    openai_model: str = Form("gpt-4o-mini"),
    anthropic_model: str = Form("claude-3-5-sonnet-20241022"),
    gemini_api_key: str = Form(""),
    openai_api_key: str = Form(""),
    anthropic_api_key: str = Form(""),
    telegram_bot_token: str = Form(""),
    telegram_chat_id: str = Form(""),
    telegram_webhook_secret: str = Form(""),
    scout_api_base_url: str = Form("http://127.0.0.1:8001"),
    scout_interval_seconds: str = Form("900"),
    scout_limit_per_source: str = Form("25"),
    rss_feed_urls: str = Form(DEFAULT_RSS_FEED_URLS),
    gmail_imap_host: str = Form("imap.gmail.com"),
    gmail_imap_port: str = Form("993"),
    gmail_email: str = Form(""),
    gmail_app_password: str = Form(""),
    gmail_mailbox: str = Form("INBOX"),
    gmail_alert_subjects: str = Form("Upwork Job Alert,LinkedIn Job Alert"),
    gmail_search_window_days: str = Form("2"),
    reddit_subreddits: str = Form("forhire,freelance_forhire"),
    reddit_user_agent: str = Form("AI-Freelancer-OS/0.1 by dancru299"),
):
    current_env = read_env_values()
    updates = {
        "AIFOS_ANALYST_PROVIDER": _valid_choice(analyst_provider, ANALYST_PROVIDERS, "auto"),
        "AIFOS_PROPOSAL_PROVIDER": _valid_choice(proposal_provider, PROPOSAL_PROVIDERS, "auto"),
        "AIFOS_WORKER_PROVIDER": _valid_choice(worker_provider, WORKER_PROVIDERS, "auto"),
        "AIFOS_GEMINI_MODEL": gemini_model.strip() or "gemini-2.5-flash",
        "AIFOS_OPENAI_MODEL": openai_model.strip() or "gpt-4o-mini",
        "AIFOS_ANTHROPIC_MODEL": anthropic_model.strip() or "claude-3-5-sonnet-20241022",
        "AIFOS_TELEGRAM_DEFAULT_CHAT_ID": telegram_chat_id.strip(),
        "AIFOS_SCOUT_API_BASE_URL": scout_api_base_url.strip() or "http://127.0.0.1:8001",
        "AIFOS_SCOUT_INTERVAL_SECONDS": scout_interval_seconds.strip() or "900",
        "AIFOS_SCOUT_LIMIT_PER_SOURCE": scout_limit_per_source.strip() or "25",
        "AIFOS_RSS_FEED_URLS": rss_feed_urls.strip(),
        "AIFOS_GMAIL_IMAP_HOST": gmail_imap_host.strip() or "imap.gmail.com",
        "AIFOS_GMAIL_IMAP_PORT": gmail_imap_port.strip() or "993",
        "AIFOS_GMAIL_EMAIL": gmail_email.strip(),
        "AIFOS_GMAIL_MAILBOX": gmail_mailbox.strip() or "INBOX",
        "AIFOS_GMAIL_ALERT_SUBJECTS": gmail_alert_subjects.strip() or "Upwork Job Alert,LinkedIn Job Alert",
        "AIFOS_GMAIL_SEARCH_WINDOW_DAYS": gmail_search_window_days.strip() or "2",
        "AIFOS_REDDIT_SUBREDDITS": reddit_subreddits.strip() or "forhire,freelance_forhire",
        "AIFOS_REDDIT_USER_AGENT": reddit_user_agent.strip() or "AI-Freelancer-OS/0.1 by dancru299",
    }

    if telegram_webhook_secret.strip():
        updates["AIFOS_TELEGRAM_WEBHOOK_SECRET"] = telegram_webhook_secret.strip()
    elif not current_env.get("AIFOS_TELEGRAM_WEBHOOK_SECRET"):
        updates["AIFOS_TELEGRAM_WEBHOOK_SECRET"] = token_urlsafe(24)

    if gemini_api_key.strip():
        updates["GEMINI_API_KEY"] = gemini_api_key.strip()
    if openai_api_key.strip():
        updates["AIFOS_OPENAI_API_KEY"] = openai_api_key.strip()
    if anthropic_api_key.strip():
        updates["AIFOS_ANTHROPIC_API_KEY"] = anthropic_api_key.strip()
    if telegram_bot_token.strip():
        updates["AIFOS_TELEGRAM_BOT_TOKEN"] = telegram_bot_token.strip()
    if gmail_app_password.strip():
        updates["AIFOS_GMAIL_APP_PASSWORD"] = gmail_app_password.strip()

    update_env_values(updates)
    return RedirectResponse("/admin?saved=1", status_code=303)


def _valid_choice(value: str, choices: tuple[str, ...], fallback: str) -> str:
    return value if value in choices else fallback


async def _get_webhook_info(bot_token: str | None) -> dict:
    if not bot_token:
        return {"ok": False, "description": "Telegram bot token is missing."}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"https://api.telegram.org/bot{bot_token}/getWebhookInfo")
            response.raise_for_status()
            return response.json()
    except Exception as exc:
        return {"ok": False, "description": str(exc)}


def _render_admin_page(
    *,
    analyst_provider: str,
    proposal_provider: str,
    worker_provider: str,
    gemini_model: str,
    openai_model: str,
    anthropic_model: str,
    telegram_chat_id: str,
    telegram_secret: str,
    gemini_key: str | None,
    openai_key: str | None,
    anthropic_key: str | None,
    telegram_token: str | None,
    scout_api_base_url: str,
    scout_interval_seconds: str,
    scout_limit_per_source: str,
    rss_feed_urls: str,
    gmail_imap_host: str,
    gmail_imap_port: str,
    gmail_email: str,
    gmail_app_password: str | None,
    gmail_mailbox: str,
    gmail_alert_subjects: str,
    gmail_search_window_days: str,
    reddit_subreddits: str,
    reddit_user_agent: str,
    saved: bool,
    webhook_url: str | None,
    webhook_info: dict,
    base_url: str,
) -> str:
    webhook_result = webhook_info.get("result", {}) if webhook_info.get("ok") else {}
    current_webhook = webhook_result.get("url") or "not set"
    last_error = webhook_result.get("last_error_message") or webhook_info.get("description") or ""

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI-FOS Settings</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #17202a;
      --muted: #657182;
      --line: #d9dee7;
      --accent: #0f766e;
      --accent-soft: #d9f4ef;
      --warn: #8a5a00;
      --warn-soft: #fff2c2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 15px;
      line-height: 1.5;
    }}
    main {{
      width: min(1120px, calc(100% - 32px));
      margin: 32px auto 56px;
    }}
    header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 24px;
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 30px;
      line-height: 1.15;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 16px;
      font-size: 17px;
      line-height: 1.25;
      letter-spacing: 0;
    }}
    p {{ margin: 0; color: var(--muted); }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      align-items: start;
    }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 10px 30px rgba(18, 29, 43, 0.04);
    }}
    .full {{ grid-column: 1 / -1; }}
    label {{
      display: block;
      margin-bottom: 6px;
      font-size: 13px;
      font-weight: 650;
      color: #2f3a47;
    }}
    input, select {{
      width: 100%;
      height: 40px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--text);
      padding: 0 10px;
      font: inherit;
    }}
    .row {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 14px;
    }}
    .status-list {{
      display: grid;
      gap: 8px;
      margin-top: 2px;
    }}
    .status-item {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      background: #fbfcfd;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      border-radius: 999px;
      padding: 0 10px;
      font-size: 12px;
      font-weight: 700;
      color: var(--accent);
      background: var(--accent-soft);
      white-space: nowrap;
    }}
    .badge.warn {{
      color: var(--warn);
      background: var(--warn-soft);
    }}
    .actions {{
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 6px;
    }}
    button, .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 40px;
      border: 1px solid #0f766e;
      border-radius: 6px;
      background: var(--accent);
      color: white;
      padding: 0 14px;
      font: inherit;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
    }}
    .button.secondary {{
      background: #ffffff;
      color: var(--accent);
    }}
    .notice {{
      border: 1px solid #b7eadf;
      background: #ecfbf8;
      color: #0f4f49;
      border-radius: 8px;
      padding: 12px 14px;
      margin-bottom: 16px;
      font-weight: 650;
    }}
    code {{
      background: #edf0f4;
      border-radius: 5px;
      padding: 2px 5px;
      font-size: 13px;
    }}
    .help {{
      margin-top: 8px;
      font-size: 13px;
      color: var(--muted);
    }}
    @media (max-width: 780px) {{
      header, .grid, .row {{
        display: block;
      }}
      .panel, header > div {{
        margin-bottom: 14px;
      }}
      main {{
        width: min(100% - 20px, 1120px);
        margin-top: 20px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>AI-FOS Settings</h1>
        <p>Local control panel for provider routing, API keys, Telegram, and webhook setup.</p>
      </div>
      <a class="button secondary" href="/docs">API Docs</a>
    </header>

    {('<div class="notice">Settings saved. Restart background workers if you run them outside this FastAPI process.</div>' if saved else '')}

    <form method="post" action="/admin/settings" class="grid">
      <section class="panel">
        <h2>Provider Routing</h2>
        <div class="row">
          <div>
            <label for="analyst_provider">Analyst provider</label>
            {_select("analyst_provider", ANALYST_PROVIDERS, analyst_provider)}
          </div>
          <div>
            <label for="proposal_provider">Proposal provider</label>
            {_select("proposal_provider", PROPOSAL_PROVIDERS, proposal_provider)}
          </div>
          <div>
            <label for="worker_provider">Worker provider</label>
            {_select("worker_provider", WORKER_PROVIDERS, worker_provider)}
          </div>
        </div>
        <p class="help"><code>auto</code> uses available keys in order. Workers use Gemini, Anthropic, OpenAI, then local mock fallback when enabled.</p>
      </section>

      <section class="panel">
        <h2>Key Status</h2>
        <div class="status-list">
          {_status_item("Gemini", gemini_key)}
          {_status_item("OpenAI", openai_key)}
          {_status_item("Anthropic", anthropic_key)}
          {_status_item("Telegram bot", telegram_token)}
          {_status_item("Gmail IMAP", gmail_app_password if gmail_email else None)}
        </div>
      </section>

      <section class="panel">
        <h2>Model Names</h2>
        <div class="row">
          <div>
            <label for="gemini_model">Gemini model</label>
            <input id="gemini_model" name="gemini_model" value="{escape(gemini_model)}">
          </div>
          <div>
            <label for="openai_model">OpenAI model</label>
            <input id="openai_model" name="openai_model" value="{escape(openai_model)}">
          </div>
        </div>
        <div>
          <label for="anthropic_model">Anthropic model</label>
          <input id="anthropic_model" name="anthropic_model" value="{escape(anthropic_model)}">
        </div>
      </section>

      <section class="panel">
        <h2>Replace Keys</h2>
        <div class="row">
          <div>
            <label for="gemini_api_key">Gemini API key</label>
            <input id="gemini_api_key" name="gemini_api_key" placeholder="Leave blank to keep current key">
          </div>
          <div>
            <label for="openai_api_key">OpenAI API key</label>
            <input id="openai_api_key" name="openai_api_key" placeholder="Leave blank to keep current key">
          </div>
        </div>
        <div>
          <label for="anthropic_api_key">Anthropic API key</label>
          <input id="anthropic_api_key" name="anthropic_api_key" placeholder="Leave blank to keep current key">
        </div>
      </section>

      <section class="panel full">
        <h2>Scout Sources</h2>
        <div class="row">
          <div>
            <label for="scout_api_base_url">Ingest API base URL</label>
            <input id="scout_api_base_url" name="scout_api_base_url" value="{escape(scout_api_base_url)}">
          </div>
          <div>
            <label for="scout_interval_seconds">Interval seconds</label>
            <input id="scout_interval_seconds" name="scout_interval_seconds" value="{escape(scout_interval_seconds)}">
          </div>
        </div>
        <div class="row">
          <div>
            <label for="scout_limit_per_source">Limit per source</label>
            <input id="scout_limit_per_source" name="scout_limit_per_source" value="{escape(scout_limit_per_source)}">
          </div>
          <div>
            <label for="gmail_search_window_days">Gmail search window days</label>
            <input id="gmail_search_window_days" name="gmail_search_window_days" value="{escape(gmail_search_window_days)}">
          </div>
        </div>
        <div class="row">
          <div>
            <label for="gmail_email">Gmail address</label>
            <input id="gmail_email" name="gmail_email" value="{escape(gmail_email)}" placeholder="name@gmail.com">
          </div>
          <div>
            <label for="gmail_app_password">Gmail app password</label>
            <input id="gmail_app_password" name="gmail_app_password" placeholder="Current: {escape(masked(gmail_app_password))}. Leave blank to keep it.">
          </div>
          <div>
            <label for="gmail_imap_host">IMAP host</label>
            <input id="gmail_imap_host" name="gmail_imap_host" value="{escape(gmail_imap_host)}">
          </div>
          <div>
            <label for="gmail_imap_port">IMAP port</label>
            <input id="gmail_imap_port" name="gmail_imap_port" value="{escape(gmail_imap_port)}">
          </div>
          <div>
            <label for="gmail_mailbox">Mailbox</label>
            <input id="gmail_mailbox" name="gmail_mailbox" value="{escape(gmail_mailbox)}">
          </div>
          <div>
            <label for="gmail_alert_subjects">Alert subject filters</label>
            <input id="gmail_alert_subjects" name="gmail_alert_subjects" value="{escape(gmail_alert_subjects)}">
          </div>
        </div>
        <p class="help">Inbox Hunter scans recent Gmail alerts by subject, parses Upwork/LinkedIn job links, then submits normalized jobs to <code>/api/v1/jobs/ingest</code>.</p>
        <div>
          <label for="rss_feed_urls">Open RSS feed URLs</label>
          <input id="rss_feed_urls" name="rss_feed_urls" value="{escape(rss_feed_urls)}" placeholder="Paste RSS URLs, separated by comma or semicolon">
        </div>
        <p class="help">Recommended legal/open feeds: WeworkRemotely programming RSS and RemoteOK RSS. Add a Hacker News Who is Hiring RSS bridge URL here when you choose one.</p>
        <div class="row" style="margin-top:14px">
          <div>
            <label for="reddit_subreddits">Reddit subreddits</label>
            <input id="reddit_subreddits" name="reddit_subreddits" value="{escape(reddit_subreddits)}">
          </div>
          <div>
            <label for="reddit_user_agent">Reddit User-Agent</label>
            <input id="reddit_user_agent" name="reddit_user_agent" value="{escape(reddit_user_agent)}">
          </div>
        </div>
      </section>

      <section class="panel full">
        <h2>Telegram</h2>
        <div class="row">
          <div>
            <label for="telegram_chat_id">Default chat ID</label>
            <input id="telegram_chat_id" name="telegram_chat_id" value="{escape(telegram_chat_id)}">
          </div>
          <div>
            <label for="telegram_webhook_secret">Webhook secret</label>
            <input id="telegram_webhook_secret" name="telegram_webhook_secret" placeholder="Current: {escape(masked(telegram_secret))}. Leave blank to keep it.">
          </div>
        </div>
        <div>
          <label for="telegram_bot_token">Telegram bot token</label>
          <input id="telegram_bot_token" name="telegram_bot_token" placeholder="Leave blank to keep current token">
        </div>
        <p class="help">Current webhook: <code>{escape(current_webhook)}</code>{(' | Last error: ' + escape(last_error)) if last_error else ''}</p>
      </section>

      <section class="panel full">
        <h2>Webhook Setup</h2>
        <p>Local API base: <code>{escape(base_url)}</code></p>
        <p class="help">For Telegram button clicks, expose this local API with ngrok and register <code>/api/v1/telegram/webhook</code> as the webhook URL.</p>
        {('<p class="help">Last registered URL from setup script: <code>' + escape(webhook_url) + '</code></p>' if webhook_url else '')}
      </section>

      <div class="actions full">
        <button type="submit">Save Settings</button>
      </div>
    </form>
  </main>
</body>
</html>"""


def _select(name: str, choices: tuple[str, ...], selected: str) -> str:
    options = []
    for choice in choices:
        attr = ' selected' if choice == selected else ''
        options.append(f'<option value="{escape(choice)}"{attr}>{escape(choice)}</option>')
    return f'<select id="{escape(name)}" name="{escape(name)}">' + "".join(options) + "</select>"


def _status_item(label: str, value: str | None) -> str:
    status = masked(value)
    css = "badge" if value else "badge warn"
    return f'<div class="status-item"><span>{escape(label)}</span><span class="{css}">{escape(status)}</span></div>'
