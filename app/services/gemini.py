import logging
from typing import Any

from app.core.config import Settings
from app.services.http import request_with_retry

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate_text(self, prompt: str, system_instruction: str | None = None, temperature: float = 0.2) -> str:
        if not self.settings.gemini_api_key:
            raise RuntimeError("Gemini API key is not configured.")

        payload: dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "candidateCount": 1,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.settings.gemini_model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.settings.gemini_api_key,
        }

        response = await request_with_retry("POST", url, headers=headers, json=payload, timeout=45.0)
        data = response.json()

        text = _extract_text(data)
        if not text:
            logger.debug("Gemini returned no text content: %s", data)
            raise RuntimeError("Gemini returned no text content.")
        return text


def _extract_text(data: dict[str, Any]) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        return ""

    parts = candidates[0].get("content", {}).get("parts") or []
    return "\n".join(part.get("text", "") for part in parts if part.get("text")).strip()
