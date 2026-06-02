import json
import logging
import re

from app.core.config import Settings
from app.services.gemini import GeminiService
from app.services.http import request_with_retry

logger = logging.getLogger(__name__)


class LLMTextService:
    def __init__(self, settings: Settings, provider: str | None = None) -> None:
        self.settings = settings
        self.provider = (provider or "auto").lower()

    async def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.35) -> str:
        chain = self._provider_chain()
        last_exc: Exception | None = None
        for index, provider in enumerate(chain):
            try:
                return await self._generate_with(provider, system_prompt, user_prompt, temperature)
            except Exception as exc:
                last_exc = exc
                if index < len(chain) - 1:
                    logger.warning(
                        "LLM provider %s failed (%s); falling back to %s",
                        provider,
                        exc,
                        chain[index + 1],
                    )
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("No configured LLM provider is available.")

    async def _generate_with(self, provider: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
        if provider == "gemini":
            return await GeminiService(self.settings).generate_text(
                user_prompt,
                system_instruction=system_prompt,
                temperature=temperature,
            )
        if provider == "openai":
            return await self._generate_with_openai(system_prompt, user_prompt, temperature)
        if provider == "anthropic":
            return await self._generate_with_anthropic(system_prompt, user_prompt)
        raise RuntimeError(f"Unknown LLM provider: {provider}")

    def _provider_chain(self) -> list[str]:
        """Ordered providers to try. An explicit provider is used alone; ``auto``
        falls through every configured key so a failing key can hand off to a
        different one that is already configured."""
        if self.provider in {"gemini", "openai", "anthropic"}:
            return [self.provider]
        if self.provider == "mock":
            raise RuntimeError("Mock provider requested.")

        chain: list[str] = []
        if self.settings.gemini_api_key:
            chain.append("gemini")
        if self.settings.anthropic_api_key:
            chain.append("anthropic")
        if self.settings.openai_api_key:
            chain.append("openai")
        if not chain:
            raise RuntimeError("No LLM API key is configured.")
        return chain

    async def _generate_with_openai(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        if not self.settings.openai_api_key:
            raise RuntimeError("OpenAI API key is not configured.")
        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        response = await request_with_retry(
            "POST",
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _generate_with_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        if not self.settings.anthropic_api_key:
            raise RuntimeError("Anthropic API key is not configured.")
        payload = {
            "model": self.settings.anthropic_model,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        headers = {
            "x-api-key": self.settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        response = await request_with_retry(
            "POST",
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
        )
        data = response.json()
        text_blocks = [block["text"] for block in data.get("content", []) if block.get("type") == "text"]
        return "\n".join(text_blocks).strip()


def load_json_object(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if fenced:
            return json.loads(fenced.group(1))
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))
