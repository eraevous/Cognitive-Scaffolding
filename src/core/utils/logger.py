"""Backward compatibility wrapper for relocated logging helpers."""

from __future__ import annotations

from core.logger import configure_logging as setup_logging
from core.logger import get_logger

__all__ = ["setup_logging", "get_logger"]
