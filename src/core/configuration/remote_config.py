"""Remote configuration data model."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from core.constants import DEFAULT_S3_PREFIXES


@dataclass(slots=True)
class RemoteConfig:
    """Serialize settings used for S3 and remote inference utilities."""

    bucket_name: str | None = None
    lambda_name: str | None = None
    region: str | None = None
    root: str | None = None
    openai_api_key: str | None = None
    prefixes: Dict[str, str] = field(default_factory=lambda: dict(DEFAULT_S3_PREFIXES))

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "RemoteConfig":
        return cls(**payload)

    @classmethod
    def from_file(cls, path: Path | str) -> "RemoteConfig":
        with Path(path).expanduser().open("r", encoding="utf-8") as handle:
            payload: Dict[str, Any] = json.load(handle)
        return cls.from_dict(payload)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bucket_name": self.bucket_name,
            "lambda_name": self.lambda_name,
            "region": self.region,
            "root": self.root,
            "openai_api_key": self.openai_api_key,
            "prefixes": dict(self.prefixes),
        }


__all__ = ["RemoteConfig"]
