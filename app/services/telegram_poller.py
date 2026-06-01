"""Telegram long-polling loop.

An alternative to the webhook for setups without a public HTTPS URL (laptop,
home PC, NAT). The bot pulls updates with ``getUpdates`` and feeds inline-button
callbacks into the shared :func:`dispatch_callback`. Only outbound internet is
required — no inbound port, tunnel, or VPS.

Run it inside the API process by setting ``AIFOS_TELEGRAM_MODE=polling`` (the
lifespan starts it), or standalone via ``python scripts/run_telegram_poller.py``.
"""

import asyncio
import logging

import httpx

from app.core.config import get_settings
from app.services.telegram_dispatch import dispatch_callback

logger = logging.getLogger(__name__)

_LONG_POLL_SECONDS = 25


async def run_poller(stop_event: asyncio.Event | None = None) -> None:
    settings = get_settings()
    token = settings.telegram_bot_token
    if not token:
        logger.warning("Telegram polling requested but no bot token is configured; poller not started.")
        return

    base = f"{settings.telegram_api_base}/bot{token}"

    # getUpdates conflicts with an active webhook (409); drop it first.
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(f"{base}/deleteWebhook", json={"drop_pending_updates": False})
    except Exception:
        logger.warning("deleteWebhook failed; continuing", exc_info=True)

    offset: int | None = None
    logger.info("Telegram long-polling started")

    while stop_event is None or not stop_event.is_set():
        try:
            params: dict[str, str | int] = {
                "timeout": _LONG_POLL_SECONDS,
                "allowed_updates": '["callback_query"]',
            }
            if offset is not None:
                params["offset"] = offset

            async with httpx.AsyncClient(timeout=_LONG_POLL_SECONDS + 10) as client:
                response = await client.get(f"{base}/getUpdates", params=params)
                response.raise_for_status()
                payload = response.json()

            for update in payload.get("result", []):
                offset = update["update_id"] + 1
                callback = update.get("callback_query")
                if not callback or not callback.get("data"):
                    continue
                message = callback.get("message") or {}
                chat_id = (message.get("chat") or {}).get("id")
                try:
                    await dispatch_callback(
                        data=callback.get("data"),
                        callback_id=callback.get("id"),
                        callback_chat_id=chat_id,
                        callback_message_id=message.get("message_id"),
                        settings=settings,
                        background_tasks=None,
                    )
                except Exception:
                    logger.exception("Failed to dispatch Telegram callback %s", callback.get("id"))
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.warning("Telegram poll cycle failed; retrying shortly", exc_info=True)
            await asyncio.sleep(3)

    logger.info("Telegram long-polling stopped")
