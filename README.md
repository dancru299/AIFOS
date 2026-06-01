# AI Freelancer Operating System

This repo now contains an MVP-ready headless backend for the workflow described in `prd-v1.md`.

## What is implemented

- `POST /api/v1/jobs/ingest`
  - Accepts normalized jobs from scout collectors.
  - Stores them in SQLite.
  - Kicks off asynchronous analyst scoring.
- `POST /api/v1/telegram/webhook`
  - Verifies `X-Telegram-Bot-Api-Secret-Token`.
  - Handles inline `[APPROVE & PITCH]` and `[DISMISS]` decisions.
  - Moves approved jobs into `generating_proposal` immediately, returns `200 OK`, then generates the proposal in a background task.
- Lightweight state machine for `jobs.status`.
- Structured portfolio markdown template for proposal prompting.
- Mock fallbacks when OpenAI / Anthropic keys are not configured, so the pipeline can still be exercised locally.

## Status model

`jobs.status` supports:

- `pending`
- `analyzing`
- `discarded`
- `awaiting_human_review`
- `generating_proposal`
- `proposal_ready`
- `rejected`
- `analysis_failed`
- `proposal_failed`

This keeps the Telegram webhook idempotent and avoids long-running work inside the webhook request itself.

## Quick start

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

2. Copy env vars:

```bash
copy .env.example .env
```

3. Fill in:

- `AIFOS_TELEGRAM_BOT_TOKEN`
- `AIFOS_TELEGRAM_DEFAULT_CHAT_ID`
- `AIFOS_TELEGRAM_WEBHOOK_SECRET`
- `GEMINI_API_KEY` for live analyst scoring and proposal generation
- `AIFOS_OPENAI_API_KEY` optional fallback for analyst scoring
- `AIFOS_ANTHROPIC_API_KEY` optional fallback for proposal generation

4. Update `portfolio/operator_portfolio.md`.

5. Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

6. Register your Telegram webhook:

```bash
python scripts/set_telegram_webhook.py https://your-domain.example/api/v1/telegram/webhook
```

Or let the helper start ngrok and register Telegram automatically:

```bash
python scripts/setup_ngrok_webhook.py 8001
```

## Where to get keys

- `GEMINI_API_KEY`: create it from Google AI Studio API Keys. This is enough for the MVP's live scoring and proposal generation.
- `AIFOS_TELEGRAM_BOT_TOKEN`: create a bot with Telegram `@BotFather`.
- `AIFOS_TELEGRAM_DEFAULT_CHAT_ID`: the chat ID where the bot should send job alerts. Send a message to your bot, then run `python scripts/get_telegram_chat_id.py`.
- `AIFOS_TELEGRAM_WEBHOOK_SECRET`: make a random private string yourself; pass the same value when registering the webhook.
- `AIFOS_OPENAI_API_KEY` and `AIFOS_ANTHROPIC_API_KEY`: optional fallbacks. You do not need them while Gemini is configured.

## What webhook registration means

Telegram cannot call your local Python function directly. You give Telegram one public HTTPS URL for this app, and Telegram sends button-click events to that URL.

For local development, that usually means:

1. Run the API locally with `uvicorn`.
2. Expose it with a tunnel such as ngrok or Cloudflare Tunnel.
3. Run `scripts/set_telegram_webhook.py` with the public HTTPS URL from the tunnel.

Example:

```bash
python scripts/set_telegram_webhook.py https://example-tunnel.ngrok-free.app/api/v1/telegram/webhook
```

The webhook secret is not a key you get from Telegram. It is a random private value you choose, store in `.env`, and send to Telegram during webhook registration. Telegram then includes it in the `X-Telegram-Bot-Api-Secret-Token` header on every webhook call.

## Local settings UI

Open `http://127.0.0.1:8001/admin` while the API is running.

The UI lets you:

- choose analyst and proposal providers,
- update model names,
- paste or replace API keys without displaying existing secret values,
- check Telegram webhook status.

## Scout Agent

Configure sources in `.env`:

```bash
AIFOS_GMAIL_EMAIL=your.name@gmail.com
AIFOS_GMAIL_APP_PASSWORD=your-gmail-app-password
AIFOS_GMAIL_ALERT_SUBJECTS=Upwork Job Alert,LinkedIn Job Alert
AIFOS_RSS_FEED_URLS=https://weworkremotely.com/categories/remote-programming-jobs.rss,https://remoteok.com/remote-jobs.rss
AIFOS_REDDIT_SUBREDDITS=forhire,freelance_forhire
AIFOS_SCOUT_INTERVAL_SECONDS=900
```

The Scout Agent now runs as an "Inbox Hunter" first: it connects to Gmail over IMAP, scans recent alert emails whose subject contains `Upwork Job Alert` or `LinkedIn Job Alert`, parses the HTML with BeautifulSoup, extracts job title, description, budget, location, and job link, then submits each normalized job to `POST /api/v1/jobs/ingest`.

Run a safe fetch preview without ingesting jobs:

```bash
python scripts/run_scouts.py --dry-run
```

Run one real scout cycle and submit jobs into `POST /api/v1/jobs/ingest`:

```bash
python scripts/run_scouts.py --once
```

Run continuously every 15 minutes:

```bash
python scripts/run_scouts.py
```

Open RSS sources are still supported through `AIFOS_RSS_FEED_URLS`. The default legal/open feeds are WeworkRemotely programming jobs and RemoteOK remote jobs. You can add a Hacker News "Who is Hiring" RSS bridge URL to the same comma-separated setting.

## Local behavior without API keys

If `AIFOS_ALLOW_MOCK_LLM=true` and the provider keys are empty:

- the Analyst Agent uses deterministic heuristics,
- the Proposal Agent generates a compact local draft,
- Telegram delivery still works if the bot credentials are configured.

## Example ingest

```bash
curl -X POST http://127.0.0.1:8000/api/v1/jobs/ingest ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"upwork\",\"external_url\":\"https://www.upwork.com/jobs/_123\",\"title\":\"Need Next.js Tailwind Landing Page\",\"description_raw\":\"Need a responsive landing page from Figma.\",\"budget_raw\":\"$400 fixed\",\"client_location\":\"United States\"}"
```

## Notes

- The webhook route rejects requests when the secret header is missing or invalid.
- The portfolio prompt source is a compact markdown file, not raw site HTML.
- SQLite is used for MVP speed; the models are structured to migrate cleanly to PostgreSQL later.
- Gemini is the first live LLM provider used when `GEMINI_API_KEY` is present. OpenAI and Anthropic remain optional fallbacks.

## Architecture: reality vs PRD

`prd-v1.md` is the original spec and is intentionally kept as-is. A few things drifted from it during implementation — this section is the source of truth:

- **LLM provider:** the PRD planned `gpt-4o-mini` (Analyst) + `Claude 3.5 Sonnet` (Proposal/Worker). The implementation is **Gemini-first** (`gemini-2.5-flash` by default), with OpenAI and Anthropic as optional fallbacks. Provider routing is `auto` by default and configurable per stage via `AIFOS_ANALYST_PROVIDER` / `AIFOS_PROPOSAL_PROVIDER` / `AIFOS_WORKER_PROVIDER`. In `auto` mode each outbound LLM call retries the same provider on transient errors, then **falls through to the next configured key** (Gemini → Anthropic → OpenAI), so a bad/overloaded key hands off automatically. Pinning an explicit provider disables that fallback.
- **Job sources:** to stay within platform ToS, the Scout Agent does not scrape Upwork directly. It reads Gmail job-alert emails over IMAP ("Inbox Hunter") plus open RSS feeds (WeWorkRemotely, RemoteOK) and Reddit.
- **Pipeline depth:** the PRD lists PM / Worker / QA / Delivery as "Future Horizon" (Phase 3-5). These are **already implemented** — the `jobs.status` flow goes through `in_progress -> qa_running -> delivery_ready`, generating files in a sandboxed workspace, running QA checks, and packaging a ZIP for delivery.

## Autonomous worker (Claude Code engine)

By default the worker (`AIFOS_WORKER_ENGINE=scaffold`) generates a one-shot draft and a ZIP. Set `AIFOS_WORKER_ENGINE=claude_code` to instead run **Claude Code as an autonomous agent** that plans, writes real code, runs/tests it, and iterates — handing you a finished, review-ready deliverable in a folder.

```bash
# .env
AIFOS_WORKER_ENGINE=claude_code
AIFOS_DELIVERY_ROOT=D:/work/aifos-jobs   # a folder you control and open to review
AIFOS_CLAUDE_BIN=claude                  # uses the CLI's existing login; no API key
```

Flow (per job, after you tap **Start Work**):

1. **PLANNING** — Claude Code reads the brief and writes `PLAN.md` → status `awaiting_plan_approval`. You get a Telegram card with the plan and **✅ Duyệt kế hoạch / ✋ Huỷ**.
2. **Approve** → Claude Code executes the plan autonomously in `AIFOS_DELIVERY_ROOT/<job>/`: writes real code, runs tests, fixes failures, writes `SUMMARY.md` (and `QUESTIONS.md` if blocked).
3. A **reviewer** pass scores completion vs the brief and runs tests. If ≥90% and passing → `delivery_ready`; otherwise it self-repairs up to `AIFOS_AGENT_MAX_REPAIRS` times.
4. Telegram pings you: *"Xong ~N%, review tại `<folder>`"* — you open the folder, no ZIP.

If you want fewer interruptions, set `AIFOS_AGENT_PLAN_GATE=false`: Claude Code still writes `PLAN.md`, but then immediately executes it and only asks you to review once QA says the job is done or needs a human decision.

When the reviewer finishes, the Telegram card carries action buttons so you never get stuck: **✅ Nghiệm thu / 🔁 Làm lại** when it passes, **🔁 Làm lại** when it stalls (re-runs the planner/worker). Anything the agent recorded in `QUESTIONS.md` is quoted directly in that message, so the things only you can answer surface in chat instead of staying buried in the folder.

**Safety & cost:**
- File edits are confined to the job folder (`cwd` + `--add-dir`).
- The **plan gate** is the main human checkpoint — you reject before the expensive execute run. `AIFOS_AGENT_MAX_TURNS`, `AIFOS_AGENT_RUN_TIMEOUT_SECONDS`, and `AIFOS_AGENT_MAX_REPAIRS` bound each job.
- **Shell permission mode** (`AIFOS_AGENT_PERMISSION_MODE`): on **Windows** only `bypassPermissions` actually lets the agent run tests/builds headless, so that is the default. ⚠️ In this mode the allow/deny guardrail in `app/services/agent/guardrail.py` is **not enforced at runtime** — the agent can run *any* shell command on the host. Mitigate by pointing `AIFOS_DELIVERY_ROOT` at a dedicated workspace — ideally inside a container or VM — and keeping the plan gate on. On **Linux/macOS/containers** set it to `default` to enforce the command allow/deny list (only safe prefixes like `python`/`pip`/`pytest`/`npm` run; `rm`/`sudo`/`git push`/`ssh` are denied). To enforce the deny list **even under `bypassPermissions`**, set `AIFOS_AGENT_ENFORCE_GUARDRAIL_HOOK=true`: the runner drops a `.claude/settings.json` into each job folder wiring a **PreToolUse hook** (`guard_hook.py`) that blocks destructive Bash commands at runtime. Default off.
- **Each job consumes real Claude Code usage** (billed via your Claude Code login, logged per run as turns + USD). Always review the deliverable before sending it to a client.

## Run on your own machine (no public URL needed)

If you can't expose a public HTTPS webhook (laptop, home PC, shared hosting, behind NAT), run the bot in **long-polling** mode — the app pulls updates from Telegram instead of receiving them, so no tunnel, public IP, or VPS is required. Only outbound internet is needed.

```bash
# .env
AIFOS_TELEGRAM_MODE=polling
```

Then start the API and the scout (two terminals):

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001   # serves /ingest, runs the poller in-process
python scripts/run_scouts.py                         # finds jobs, posts them to /ingest
```

The poller runs inside the API process and shares its database and pipeline; setting `AIFOS_TELEGRAM_MODE=polling` deletes any existing webhook automatically. Approve / Dismiss / Start Work all work over polling. Keep the machine on while you want to receive jobs. (You can also run the poller standalone with `python scripts/run_telegram_poller.py`.)

## Production setup

The default `background` task backend (FastAPI `BackgroundTasks`) needs no extra infra and is great for local use, but in-flight work is lost if the process restarts. For an always-on, durable deployment (webhook mode), run the stack:

```bash
cp .env.example .env   # fill in provider keys, Telegram, AIFOS_ADMIN_PASSWORD
docker compose up --build
```

This starts four services: `api` (uvicorn), `worker` (Arq), `redis`, and `postgres`. The compose file sets `AIFOS_TASK_BACKEND=arq`, points the app at Postgres, and runs `alembic upgrade head` before serving.

Key pieces:

- **Durable queue:** with `AIFOS_TASK_BACKEND=arq`, job processing is enqueued to Redis and run by the Arq worker (`app/worker_arq.py`), so jobs survive restarts and are retried. On startup the API also re-drives any jobs left in a transitional state (`app/services/recovery.py`).
- **Migrations:** schema is managed by Alembic. Run `alembic upgrade head` after pulling changes; create new revisions with `alembic revision --autogenerate -m "..."`.
- **Admin auth:** set `AIFOS_ADMIN_PASSWORD` to require HTTP Basic auth on `/admin`. Without it, `/admin` is reachable only from localhost.
- **Observability:** `/healthz` is a liveness probe; `/health/deep` checks the database (and Redis when using Arq). Set `AIFOS_METRICS_ENABLED=true` to expose Prometheus metrics at `/metrics`. Every request carries an `X-Request-ID`, and `AIFOS_JSON_LOGS=true` emits structured logs.

## Development

```bash
pip install -e .[dev]
ruff check .
mypy app
pytest
```

CI (`.github/workflows/ci.yml`) runs the same lint, type-check, and tests on Python 3.11 and 3.12.
