"""Shared retry helpers for OpenAI API calls."""

from __future__ import annotations

import time
from typing import Callable, Iterable, TypeVar

try:  # pragma: no cover - import depends on optional openai install
    from openai import APIStatusError, RateLimitError
except ImportError:  # pragma: no cover - fallback for test environments
    class RateLimitError(Exception):
        """Fallback RateLimitError when OpenAI SDK is unavailable."""

    class APIStatusError(Exception):
        """Fallback APIStatusError with an optional status_code attribute."""

        def __init__(self, *args, status_code: int | None = None, **kwargs):
            super().__init__(*args)
            self.status_code = status_code

from core.logger import get_logger

T = TypeVar("T")

_DEFAULT_STATUS_CODES = (429,)


def retry_with_exponential_backoff(
    operation: Callable[[], T],
    *,
    retries: int = 5,
    base_delay: float = 2.0,
    backoff_factor: float = 2.0,
    retriable_status_codes: Iterable[int] = _DEFAULT_STATUS_CODES,
    logger=None,
) -> T:
    """Execute ``operation`` with exponential backoff on rate-limit style failures."""

    log = logger or get_logger(__name__)
    delay = base_delay
    last_error: Exception | None = None
    status_codes = tuple(retriable_status_codes)

    for attempt in range(1, retries + 1):
        try:
            return operation()
        except RateLimitError as exc:  # pragma: no cover - network dependent
            last_error = exc
            log.warning(
                "OpenAI rate limit encountered (attempt %s/%s): %s; sleeping for %.1f seconds",
                attempt,
                retries,
                exc,
                delay,
            )
        except APIStatusError as exc:  # pragma: no cover - network dependent
            if exc.status_code in status_codes:
                last_error = exc
                log.warning(
                    "OpenAI API status %s on attempt %s/%s: %s; sleeping for %.1f seconds",
                    exc.status_code,
                    attempt,
                    retries,
                    exc,
                    delay,
                )
            else:
                raise

        time.sleep(delay)
        delay *= backoff_factor

    assert last_error is not None  # for type checkers
    log.error("Exhausted OpenAI retries after %s attempts", retries)
    raise last_error


__all__ = ["retry_with_exponential_backoff"]
