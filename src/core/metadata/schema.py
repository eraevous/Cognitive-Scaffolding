"""Minimal metadata validation utilities."""

from __future__ import annotations

from typing import Mapping

REQUIRED_FIELDS = {"summary"}


def validate_metadata(metadata: Mapping[str, object]) -> None:
    if not isinstance(metadata, Mapping):
        raise TypeError("Metadata must be a mapping")
    missing = REQUIRED_FIELDS - metadata.keys()
    if missing:
        raise ValueError(f"Missing required metadata fields: {sorted(missing)}")


__all__ = ["validate_metadata", "REQUIRED_FIELDS"]
