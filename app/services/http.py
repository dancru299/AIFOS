"""Shared HTTP helpers with timeout + retry/backoff for outbound calls.

All outbound LLM and Telegram requests go through ``request_with_retry`` so
transient network errors and retryable status codes (429/5xx) are retried with
exponential backoff instead of failing the whole pipeline on the first hiccup.
"""

import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_BACKOFF_BASE = 0.5
RETRYABLE_STATUS = frozenset({408, 409, 425, 429, 500, 502, 503, 504})


async def request_with_retry(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json: object | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    backoff_base: float = DEFAULT_BACKOFF_BASE,
    transport: httpx.AsyncBaseTransport | None = None,
) -> httpx.Response:
    """Perform an HTTP request, retrying transient failures with backoff.

    Raises the last ``httpx`` error (transport or ``HTTPStatusError``) once
    ``max_attempts`` is exhausted. ``transport`` is injectable for tests.
    """
    attempts = max(1, max_attempts)
    last_exc: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
                response = await client.request(method, url, headers=headers, json=json)
        except (httpx.TransportError, httpx.TimeoutException) as exc:
            last_exc = exc
            if attempt >= attempts:
                logger.warning("HTTP %s %s failed after %s attempts: %s", method, url, attempts, exc)
                raise
            await _sleep_backoff(backoff_base, attempt)
            continue

        if response.status_code in RETRYABLE_STATUS and attempt < attempts:
            logger.warning(
                "Retryable status %s from %s (attempt %s/%s)",
                response.status_code,
                url,
                attempt,
                attempts,
            )
            await _sleep_backoff(backoff_base, attempt)
            continue

        response.raise_for_status()
        return response

    # Unreachable: loop either returns or raises, but keep the type checker happy.
    if last_exc:
        raise last_exc
    raise RuntimeError("request_with_retry exhausted without a response")


async def _sleep_backoff(backoff_base: float, attempt: int) -> None:
    await asyncio.sleep(backoff_base * (2 ** (attempt - 1)))
