"""Registry helpers for cached configuration objects."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from .path_config import PathConfig
from .remote_config import RemoteConfig

_path_instance: Optional[PathConfig] = None
_remote_instance: Optional[RemoteConfig] = None

_DEFAULT_PATH_CONFIG_PATH = (
    Path(__file__).with_name("path_config.json").expanduser().resolve(strict=False)
)
_DEFAULT_REMOTE_CONFIG_PATH = (
    Path(__file__).with_name("remote_config.json").expanduser().resolve(strict=False)
)

path_config: Optional[Path] = _DEFAULT_PATH_CONFIG_PATH
remote_config: Optional[Path] = _DEFAULT_REMOTE_CONFIG_PATH

_UNSET = object()


def configure(
    *,
    path_config_path: Union[Path, str, None, object] = _UNSET,
    remote_config_path: Union[Path, str, None, object] = _UNSET,
) -> None:
    """Override the filesystem locations for configuration files."""

    global path_config, remote_config, _path_instance, _remote_instance

    if path_config_path is not _UNSET:
        if path_config_path is None:
            path_config = _DEFAULT_PATH_CONFIG_PATH
        else:
            path_config = Path(path_config_path).expanduser().resolve(strict=False)
        _path_instance = None

    if remote_config_path is not _UNSET:
        if remote_config_path is None:
            remote_config = _DEFAULT_REMOTE_CONFIG_PATH
        else:
            remote_config = Path(remote_config_path).expanduser().resolve(
                strict=False
            )
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
