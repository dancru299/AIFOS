import os
import sys

import httpx
from dotenv import load_dotenv


def main() -> int:
    load_dotenv()

    if len(sys.argv) != 2:
        print("Usage: python scripts/set_telegram_webhook.py <https-webhook-url>")
        return 1

    webhook_url = sys.argv[1]
    bot_token = os.getenv("AIFOS_TELEGRAM_BOT_TOKEN")
    secret = os.getenv("AIFOS_TELEGRAM_WEBHOOK_SECRET")

    if not bot_token or not secret:
        print("Missing AIFOS_TELEGRAM_BOT_TOKEN or AIFOS_TELEGRAM_WEBHOOK_SECRET")
        return 1

    payload = {
        "url": webhook_url,
        "allowed_updates": ["callback_query"],
        "drop_pending_updates": True,
        "secret_token": secret,
    }

    response = httpx.post(f"https://api.telegram.org/bot{bot_token}/setWebhook", json=payload, timeout=20.0)
    response.raise_for_status()
    print(response.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
