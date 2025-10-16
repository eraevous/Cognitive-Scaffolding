"""Compatibility shim around :mod:`core.logger`."""

from __future__ import annotations

from core.logger import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
