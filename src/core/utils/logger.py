import logging
import os


def setup_logging() -> None:
    """Configure basic logging once."""
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=getattr(logging, level, logging.INFO),
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger with standard config."""
    setup_logging()
    return logging.getLogger(name)
