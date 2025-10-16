"""Filesystem configuration helpers for the ingestion pipeline."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

from core.constants import (
    DEFAULT_METADATA_SCHEMA_PATH,
    ERROR_PATH_RESOLVE_FAILURE,
)

logger = logging.getLogger(__name__)


class PathConfig:
    """Materialised path configuration used across the pipeline."""

    __slots__ = (
        "root",
        "raw",
        "parsed",
        "metadata",
        "output",
        "vector",
        "schema",
        "semantic_chunking",
    )

    def __init__(
        self,
        *,
        root: Path | str | None = None,
        raw: Path | str | None = None,
        parsed: Path | str | None = None,
        metadata: Path | str | None = None,
        output: Path | str | None = None,
        vector: Path | str | None = None,
        schema: Path | str | None = None,
        semantic_chunking: bool = False,
    ) -> None:
        base = self._resolve_root(root)
        self.root = base
        self.raw = self._resolve_path(raw, base, "raw")
        self.parsed = self._resolve_path(parsed, base, "parsed")
        self.metadata = self._resolve_path(metadata, base, "metadata")
        self.output = self._resolve_path(output, base, "output")
        self.vector = self._resolve_path(vector, base, "vector")
        self.schema = validate_schema_path(schema)
        self.semantic_chunking = semantic_chunking

    @staticmethod
    def _resolve_root(root: Path | str | None) -> Path:
        if root is None:
            env_root = os.environ.get("PROJECT_ROOT")
            candidate = Path(env_root) if env_root else Path.cwd()
        else:
            candidate = Path(root)
        return candidate.expanduser().resolve()

    @staticmethod
    def _resolve_path(value: Path | str | None, root: Path, default: str) -> Path:
        if value is None:
            candidate = root / default
        else:
            candidate = Path(value)
            if not candidate.is_absolute():
                candidate = (root / candidate).resolve()
        try:
            return candidate.expanduser().resolve()
        except FileNotFoundError as exc:  # pragma: no cover - defensive guard
            message = ERROR_PATH_RESOLVE_FAILURE.format(path=candidate)
            raise ValueError(message) from exc

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "PathConfig":
        return cls(**payload)

    @classmethod
    def from_file(cls, path: Path | str) -> "PathConfig":
        with Path(path).expanduser().open("r", encoding="utf-8") as handle:
            payload: Dict[str, Any] = json.load(handle)
        return cls.from_dict(payload)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root": str(self.root),
            "raw": str(self.raw),
            "parsed": str(self.parsed),
            "metadata": str(self.metadata),
            "output": str(self.output),
            "vector": str(self.vector),
            "schema": str(self.schema),
            "semantic_chunking": self.semantic_chunking,
        }


def validate_schema_path(schema: Path | str | None) -> Path:
    """Ensure a schema path exists, otherwise fall back to the default constant."""

    if schema is None:
        candidate = DEFAULT_METADATA_SCHEMA_PATH
    else:
        candidate = Path(schema).expanduser().resolve(strict=False)
    if not candidate.exists():
        logger.warning("Metadata schema not found at %s; falling back to default.", candidate)
        return DEFAULT_METADATA_SCHEMA_PATH
    return candidate


__all__ = ["PathConfig", "validate_schema_path"]
