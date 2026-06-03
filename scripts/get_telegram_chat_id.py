import os

import httpx
from dotenv import load_dotenv


def main() -> int:
    load_dotenv()

    bot_token = os.getenv("AIFOS_TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("Missing AIFOS_TELEGRAM_BOT_TOKEN")
        return 1

    # The long-polling worker (telegram_poller) sets allowed_updates=["callback_query"],
    # and getUpdates without allowed_updates inherits that, hiding plain text messages.
    # Explicitly request message updates so this script works regardless of prior state.
    response = httpx.get(
        f"https://api.telegram.org/bot{bot_token}/getUpdates",
        params={"allowed_updates": '["message","channel_post","callback_query"]'},
        timeout=20.0,
    )
    response.raise_for_status()
    data = response.json()

    if not data.get("ok"):
        print(data)
        return 1

    updates = data.get("result", [])
    if not updates:
        print("No updates yet. Send any message to your bot in Telegram, then run this script again.")
        return 0

    seen: set[str] = set()
    for update in updates:
        message = update.get("message") or update.get("channel_post") or {}
        chat = message.get("chat") or {}
        chat_id = chat.get("id")
        if chat_id is None:
            continue

        key = str(chat_id)
        if key in seen:
            continue
        seen.add(key)

        title = chat.get("title") or chat.get("username") or "private_chat"
        print(f"chat_id={chat_id} title={title} type={chat.get('type')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
