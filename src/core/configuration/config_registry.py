"""Registry helpers for cached configuration objects."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .path_config import PathConfig
from .remote_config import RemoteConfig

_path_instance: Optional[PathConfig] = None
_remote_instance: Optional[RemoteConfig] = None

path_config: Optional[Path] = Path(__file__).with_name("path_config.json")
remote_config: Optional[Path] = Path(__file__).with_name("remote_config.json")


def configure(
    *,
    path_config_path: Optional[Path] = None,
    remote_config_path: Optional[Path] = None,
) -> None:
    """Override the filesystem locations for configuration files."""

    global path_config, remote_config, _path_instance, _remote_instance

    if path_config_path is not None:
        path_config = Path(path_config_path)
        _path_instance = None

    if remote_config_path is not None:
        remote_config = Path(remote_config_path)
        _remote_instance = None


def get_path_config(force_reload: bool = False) -> PathConfig:
    global _path_instance
    if _path_instance is None or force_reload:
        try:
            _path_instance = (
                PathConfig.from_file(path_config) if path_config else PathConfig()
            )
        except Exception:
            _path_instance = PathConfig()
    return _path_instance


def get_remote_config(force_reload: bool = False) -> RemoteConfig:
    global _remote_instance
    if _remote_instance is None or force_reload:
        _remote_instance = (
            RemoteConfig.from_file(remote_config) if remote_config else RemoteConfig()
        )
    return _remote_instance
