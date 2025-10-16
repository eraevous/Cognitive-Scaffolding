"""CLI entrypoints exposed via Typer."""

from . import pipeline as pipeline
from . import parse as parse
from . import embed as embed
from . import dedup as dedup

__all__ = ["pipeline", "parse", "embed", "dedup"]
