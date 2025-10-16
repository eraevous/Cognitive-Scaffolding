"""Central logging helpers shared across the codebase."""

from __future__ import annotations

import logging
import os
from typing import Optional

_LOCK = logging.getLogger(__name__)
_CONFIGURED = False


def configure_logging(default_level: str | int = "INFO") -> None:
    """Initialise the root logger exactly once.

    The repository relies on deterministic logging configuration so tests can
    capture warnings and informational output without side effects. The
    function is idempotent and safe to call from multiple modules.
    """

    global _CONFIGURED
    if _CONFIGURED:
        return

    level_name = os.environ.get("LOG_LEVEL", str(default_level)).upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    _CONFIGURED = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module-scoped logger with repository defaults applied."""

    configure_logging()
    return logging.getLogger(name if name is not None else "core")


__all__ = ["configure_logging", "get_logger"]
