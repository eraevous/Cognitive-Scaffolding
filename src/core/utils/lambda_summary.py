"""Helpers for AWS Lambda based summarisation outputs."""

from __future__ import annotations

import json
from typing import Any


def unpack_lambda_claude_result(payload: str | bytes) -> dict[str, Any]:
    """Parse a JSON string returned from the Lambda summariser."""

    try:
        text = payload.decode("utf-8") if isinstance(payload, bytes) else str(payload)
        data = json.loads(text)
    except json.JSONDecodeError as exc:  # pragma: no cover - exercised in tests
        raise ValueError(f"Failed to parse Claude payload: {payload}") from exc
    if not isinstance(data, dict):
        raise ValueError("Claude payload must be a JSON object")
    return data


__all__ = ["unpack_lambda_claude_result"]
