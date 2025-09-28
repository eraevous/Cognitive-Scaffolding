"""Central logging utilities for the Cognitive Scaffolding stack."""

from __future__ import annotations

import logging
import os
from typing import Optional

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(default_level: str = "INFO") -> None:
    """Configure the root logger once using environment-aware settings."""

    level_name = os.getenv("LOG_LEVEL", default_level).upper()
    level = getattr(logging, level_name, logging.INFO)

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(level=level, format=_LOG_FORMAT, datefmt=_DATE_FORMAT)
    else:
        root_logger.setLevel(level)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module-level logger configured with project defaults."""

    configure_logging()
    return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger"]
