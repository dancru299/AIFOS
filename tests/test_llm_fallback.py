from types import SimpleNamespace

import pytest

from app.services import llm
from app.services.llm import LLMTextService


def _settings(**keys):
    base = {"gemini_api_key": None, "anthropic_api_key": None, "openai_api_key": None}
    base.update(keys)
    return SimpleNamespace(**base)


async def test_auto_falls_back_to_next_configured_provider(monkeypatch):
    settings = _settings(gemini_api_key="g-key", openai_api_key="o-key")

    async def gemini_boom(self, *args, **kwargs):
        raise RuntimeError("gemini 503")

    async def openai_ok(self, system_prompt, user_prompt, temperature):
        return "FROM_OPENAI"

    monkeypatch.setattr(llm.GeminiService, "generate_text", gemini_boom)
    monkeypatch.setattr(LLMTextService, "_generate_with_openai", openai_ok)

    result = await LLMTextService(settings, "auto").generate_text("sys", "user")
    assert result == "FROM_OPENAI"


async def test_explicit_provider_does_not_fall_back(monkeypatch):
    settings = _settings(gemini_api_key="g-key", openai_api_key="o-key")

    async def gemini_boom(self, *args, **kwargs):
        raise RuntimeError("gemini down")

    monkeypatch.setattr(llm.GeminiService, "generate_text", gemini_boom)

    with pytest.raises(RuntimeError, match="gemini down"):
        await LLMTextService(settings, "gemini").generate_text("sys", "user")


async def test_auto_raises_last_error_when_all_providers_fail(monkeypatch):
    settings = _settings(gemini_api_key="g-key", openai_api_key="o-key")

    async def gemini_boom(self, *args, **kwargs):
        raise RuntimeError("gemini 503")

    async def openai_boom(self, system_prompt, user_prompt, temperature):
        raise RuntimeError("openai 429")

    monkeypatch.setattr(llm.GeminiService, "generate_text", gemini_boom)
    monkeypatch.setattr(LLMTextService, "_generate_with_openai", openai_boom)

    with pytest.raises(RuntimeError, match="openai 429"):
        await LLMTextService(settings, "auto").generate_text("sys", "user")
