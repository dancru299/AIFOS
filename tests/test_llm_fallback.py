from types import SimpleNamespace

import pytest

from app.services import llm
from app.services.llm import LLMTextService


def _settings(**keys):
    base = {
        "deepseek_api_key": None,
        "gemini_api_key": None,
        "anthropic_api_key": None,
        "openai_api_key": None,
    }
    base.update(keys)
    return SimpleNamespace(**base)


async def test_auto_falls_back_to_next_configured_provider(monkeypatch):
    # DeepSeek is tried first; when it fails, auto hands off to the next key.
    settings = _settings(deepseek_api_key="d-key", openai_api_key="o-key")

    async def deepseek_boom(self, *args, **kwargs):
        raise RuntimeError("deepseek 503")

    async def openai_ok(self, system_prompt, user_prompt, temperature):
        return "FROM_OPENAI"

    monkeypatch.setattr(LLMTextService, "_generate_with_deepseek", deepseek_boom)
    monkeypatch.setattr(LLMTextService, "_generate_with_openai", openai_ok)

    result = await LLMTextService(settings, "auto").generate_text("sys", "user")
    assert result == "FROM_OPENAI"


async def test_explicit_provider_does_not_fall_back(monkeypatch):
    settings = _settings(deepseek_api_key="d-key", openai_api_key="o-key")

    async def deepseek_boom(self, *args, **kwargs):
        raise RuntimeError("deepseek down")

    monkeypatch.setattr(LLMTextService, "_generate_with_deepseek", deepseek_boom)

    with pytest.raises(RuntimeError, match="deepseek down"):
        await LLMTextService(settings, "deepseek").generate_text("sys", "user")


async def test_auto_uses_gemini_last(monkeypatch):
    # Chain is [deepseek, gemini]; the last error (Gemini) propagates when all fail.
    settings = _settings(deepseek_api_key="d-key", gemini_api_key="g-key")

    async def deepseek_boom(self, *args, **kwargs):
        raise RuntimeError("deepseek 503")

    async def gemini_boom(self, *args, **kwargs):
        raise RuntimeError("gemini 429")

    monkeypatch.setattr(LLMTextService, "_generate_with_deepseek", deepseek_boom)
    monkeypatch.setattr(llm.GeminiService, "generate_text", gemini_boom)

    with pytest.raises(RuntimeError, match="gemini 429"):
        await LLMTextService(settings, "auto").generate_text("sys", "user")
