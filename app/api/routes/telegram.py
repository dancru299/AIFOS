from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, status

from app.core.config import Settings, get_settings
from app.schemas import TelegramWebhookUpdate
from app.services.telegram_dispatch import dispatch_callback

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


def _verify_webhook_secret(settings: Settings, secret_token: str | None) -> None:
    if not settings.telegram_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram webhook secret is not configured.",
        )
    if not secret_token or secret_token != settings.telegram_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Telegram webhook secret.",
        )


@router.post("/webhook")
async def telegram_webhook(
    payload: TelegramWebhookUpdate,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
    secret_token: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
):
    _verify_webhook_secret(settings, secret_token)

    callback = payload.callback_query
    if not callback or not callback.data:
        return {"ok": True, "ignored": True}

    callback_chat_id = callback.message.chat.id if callback.message else None
    callback_message_id = callback.message.message_id if callback.message else None

    return await dispatch_callback(
        data=callback.data,
        callback_id=callback.id,
        callback_chat_id=callback_chat_id,
        callback_message_id=callback_message_id,
        settings=settings,
        background_tasks=background_tasks,
    )
