"""Tests covering lambda summarization utilities."""

import pytest

from core.utils.lambda_summary import unpack_lambda_claude_result


def test_unpack_lambda_claude_result_invalid_json() -> None:
    """Invalid JSON payloads should raise a ValueError with helpful context."""
    with pytest.raises(ValueError) as excinfo:
        unpack_lambda_claude_result("not json")

    message = str(excinfo.value)
    assert "Failed to parse Claude payload" in message
    assert "not json" in message
