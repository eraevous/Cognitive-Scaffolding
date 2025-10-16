"""Repository-wide constants and error message templates."""

from __future__ import annotations

from pathlib import Path

# Default directory names for remote object storage. These mirror the path
# structure used throughout the ingestion pipeline.
DEFAULT_S3_PREFIXES: dict[str, str] = {
    "raw": "raw/",
    "parsed": "parsed/",
    "metadata": "metadata/",
    "stub": "stub/",
}

# Error templates consumed by configuration helpers. They remain human readable so
# CLI feedback is understandable when users provide invalid paths.
ERROR_PATH_RESOLVE_FAILURE = "Failed to resolve configured path: {path}"

# The repository ships with a reference metadata schema. The path is resolved
# relative to the project root but does not need to exist for tests; validation
# utilities fall back to this constant when overrides are missing.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METADATA_SCHEMA_PATH: Path = (
    _PROJECT_ROOT / "config" / "metadata.schema.json"
).resolve()

__all__ = [
    "DEFAULT_S3_PREFIXES",
    "DEFAULT_METADATA_SCHEMA_PATH",
    "ERROR_PATH_RESOLVE_FAILURE",
]
