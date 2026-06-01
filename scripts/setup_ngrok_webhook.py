import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
NGROK_API = "http://127.0.0.1:4040/api/tunnels"


def main() -> int:
    load_dotenv(ROOT / ".env")

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    bot_token = os.getenv("AIFOS_TELEGRAM_BOT_TOKEN")
    secret = os.getenv("AIFOS_TELEGRAM_WEBHOOK_SECRET")

    if not bot_token or not secret:
        print("Missing AIFOS_TELEGRAM_BOT_TOKEN or AIFOS_TELEGRAM_WEBHOOK_SECRET in .env")
        return 1

    public_url = get_public_url(port)
    if not public_url:
        start_ngrok(port)
        public_url = wait_for_public_url(port)

    if not public_url:
        print("Could not start ngrok tunnel.")
        print_ngrok_log_tail()
        print("If ngrok asks for auth, run: ngrok config add-authtoken <your-ngrok-token>")
        return 1

    webhook_url = f"{public_url}/api/v1/telegram/webhook"
    result = set_telegram_webhook(bot_token, secret, webhook_url)

    print(f"ngrok_public_url={public_url}")
    print(f"telegram_webhook_url={webhook_url}")
    print(f"telegram_response={result}")
    return 0


def get_public_url(port: int) -> str | None:
    try:
        response = httpx.get(NGROK_API, timeout=2.0)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    return select_https_tunnel(data, port)


def wait_for_public_url(port: int, timeout_seconds: int = 20) -> str | None:
    started_at = time.time()
    while time.time() - started_at < timeout_seconds:
        public_url = get_public_url(port)
        if public_url:
            return public_url
        time.sleep(1)
    return None


def start_ngrok(port: int) -> None:
    ngrok = shutil.which("ngrok")
    if not ngrok:
        raise RuntimeError("ngrok is not installed or not available in PATH.")

    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    log_file = open(data_dir / "ngrok.log", "ab")

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW

    subprocess.Popen(
        [ngrok, "http", str(port)],
        cwd=ROOT,
        stdout=log_file,
        stderr=log_file,
        creationflags=creationflags,
    )


def select_https_tunnel(data: dict[str, Any], port: int) -> str | None:
    tunnels = data.get("tunnels", [])
    for tunnel in tunnels:
        public_url = tunnel.get("public_url", "")
        config = tunnel.get("config", {})
        if public_url.startswith("https://") and str(config.get("addr", "")).endswith(f":{port}"):
            return public_url.rstrip("/")
    for tunnel in tunnels:
        public_url = tunnel.get("public_url", "")
        if public_url.startswith("https://"):
            return public_url.rstrip("/")
    return None


def set_telegram_webhook(bot_token: str, secret: str, webhook_url: str) -> dict[str, Any]:
    payload = {
        "url": webhook_url,
        "allowed_updates": ["callback_query"],
        "drop_pending_updates": True,
        "secret_token": secret,
    }
    response = httpx.post(f"https://api.telegram.org/bot{bot_token}/setWebhook", json=payload, timeout=20.0)
    response.raise_for_status()
    return response.json()


def print_ngrok_log_tail() -> None:
    log_path = ROOT / "data" / "ngrok.log"
    if not log_path.exists():
        return
    content = log_path.read_text(encoding="utf-8", errors="replace")
    tail = "\n".join(content.splitlines()[-20:])
    if tail:
        print("ngrok log tail:")
        print(tail)


if __name__ == "__main__":
    raise SystemExit(main())
