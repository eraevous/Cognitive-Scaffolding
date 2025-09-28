"""Registry helpers for cached configuration objects."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Union

from core.constants import DEFAULT_METADATA_SCHEMA_PATH
from core.logger import get_logger

from .path_config import PathConfig
from .remote_config import RemoteConfig

logger = get_logger(__name__)

_path_instance: Optional[PathConfig] = None
_remote_instance: Optional[RemoteConfig] = None

path_config: Optional[Path] = Path(__file__).with_name("path_config.json")
remote_config: Optional[Path] = Path(__file__).with_name("remote_config.json")


def _get_schema_override() -> Optional[Path]:
    """Return the configured schema override, if any."""

    return getattr(configure, "_metadata_schema_override", None)


def _set_schema_override(value: Optional[Path]) -> None:
    if value is None:
        if hasattr(configure, "_metadata_schema_override"):
            delattr(configure, "_metadata_schema_override")
        return
    setattr(configure, "_metadata_schema_override", value)


def _resolve_schema_candidate() -> Path:
    override = _get_schema_override()
    if override is not None:
        return override

    env_value = os.getenv("METADATA_SCHEMA_PATH")
    if env_value:
        return Path(env_value).expanduser()

    return DEFAULT_METADATA_SCHEMA_PATH


def validate_schema_path(path: Path) -> Path:
    """Ensure the metadata schema path exists, logging a warning if it does not."""

    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = DEFAULT_METADATA_SCHEMA_PATH.parent / candidate

    try:
        resolved = candidate.resolve()
    except FileNotFoundError:
        resolved = candidate

    if resolved.exists():
        return resolved

    logger.warning(
        "Metadata schema not found at %s; falling back to packaged default %s.",
        resolved,
        DEFAULT_METADATA_SCHEMA_PATH,
    )

    if DEFAULT_METADATA_SCHEMA_PATH.exists():
        return DEFAULT_METADATA_SCHEMA_PATH

    logger.warning(
        "Packaged metadata schema missing at %s; using unresolved candidate.",
        DEFAULT_METADATA_SCHEMA_PATH,
    )
    return resolved


def configure(
    *,
    path_config_path: Optional[Path] = None,
    remote_config_path: Optional[Path] = None,
    metadata_schema_path: Union[str, Path, None] = None,
) -> None:
    """Override the filesystem locations for configuration files."""

    global path_config, remote_config, _path_instance, _remote_instance

    if path_config_path is not None:
        path_config = Path(path_config_path)
        _path_instance = None

    if remote_config_path is not None:
        remote_config = Path(remote_config_path)
        _remote_instance = None

    if metadata_schema_path is not None:
        schema_override = Path(metadata_schema_path).expanduser()
        _set_schema_override(schema_override)
        _path_instance = None


def get_path_config(force_reload: bool = False) -> PathConfig:
    global _path_instance

    schema_path = validate_schema_path(_resolve_schema_candidate())

    if (
        _path_instance is None
        or force_reload
        or getattr(_path_instance, "schema", None) != schema_path
    ):
        try:
            _path_instance = (
                PathConfig.from_file(path_config, schema_path=schema_path)
                if path_config
                else PathConfig(schema=schema_path)
            )
        except Exception:
            _path_instance = PathConfig(schema=schema_path)
    return _path_instance


def get_remote_config(force_reload: bool = False) -> RemoteConfig:
    global _remote_instance
    if _remote_instance is None or force_reload:
        _remote_instance = (
            RemoteConfig.from_file(remote_config) if remote_config else RemoteConfig()
        )
    return _remote_instance
