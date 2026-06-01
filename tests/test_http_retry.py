import httpx
import pytest

from app.services.http import request_with_retry


async def test_retries_then_succeeds():
    attempts = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["n"] += 1
        if attempts["n"] < 3:
            return httpx.Response(503, text="busy")
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    response = await request_with_retry(
        "GET",
        "https://example.test/x",
        transport=transport,
        backoff_base=0.0,
    )

    assert response.status_code == 200
    assert attempts["n"] == 3


async def test_raises_after_exhausting_attempts():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="busy")

    transport = httpx.MockTransport(handler)
    with pytest.raises(httpx.HTTPStatusError):
        await request_with_retry(
            "GET",
            "https://example.test/x",
            transport=transport,
            max_attempts=2,
            backoff_base=0.0,
        )
