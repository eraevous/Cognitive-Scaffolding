"""Configuration registry caching filesystem and remote settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from core.configuration.path_config import PathConfig
from core.configuration.remote_config import RemoteConfig


def _default_config_dir() -> Path:
    env_dir = os.environ.get("CONFIG_DIR")
    if env_dir:
        return Path(env_dir).expanduser()
    return Path(__file__).resolve().parents[3] / "config"


_DEFAULT_CONFIG_DIR = _default_config_dir()
_DEFAULT_PATH_CONFIG_PATH = Path(
    os.environ.get("PATH_CONFIG_PATH", _DEFAULT_CONFIG_DIR / "path_config.json")
).expanduser().resolve(strict=False)
_DEFAULT_REMOTE_CONFIG_PATH = Path(
    os.environ.get("REMOTE_CONFIG_PATH", _DEFAULT_CONFIG_DIR / "remote_config.json")
).expanduser().resolve(strict=False)

path_config: Path = _DEFAULT_PATH_CONFIG_PATH
remote_config: Path = _DEFAULT_REMOTE_CONFIG_PATH

_path_config_cache: Optional[PathConfig] = None
_remote_config_cache: Optional[RemoteConfig] = None


def configure(
    *,
    path_config_path: Path | str | None = _DEFAULT_PATH_CONFIG_PATH,
    remote_config_path: Path | str | None = _DEFAULT_REMOTE_CONFIG_PATH,
) -> None:
    """Override configuration file locations and clear caches.

    Passing ``None`` resets to the default config packaged with the repository.
    """

    global path_config, remote_config, _path_config_cache, _remote_config_cache

    if path_config_path is None:
        path_config = _DEFAULT_PATH_CONFIG_PATH
    else:
        path_config = Path(path_config_path).expanduser().resolve(strict=False)

    if remote_config_path is None:
        remote_config = _DEFAULT_REMOTE_CONFIG_PATH
    else:
        remote_config = Path(remote_config_path).expanduser().resolve(strict=False)

    _path_config_cache = None
    _remote_config_cache = None


def get_path_config(*, force_reload: bool = False) -> PathConfig:
    """Return a cached :class:`PathConfig` instance."""

    global _path_config_cache
    if force_reload or _path_config_cache is None:
        if path_config.exists():
            _path_config_cache = PathConfig.from_file(path_config)
        else:
            root = path_config.parent if path_config.parent.exists() else Path.cwd()
            _path_config_cache = PathConfig(root=root)
    return _path_config_cache


def get_remote_config(*, force_reload: bool = False) -> RemoteConfig:
    """Return a cached :class:`RemoteConfig` instance."""

    global _remote_config_cache
    if force_reload or _remote_config_cache is None:
        if remote_config.exists():
            _remote_config_cache = RemoteConfig.from_file(remote_config)
        else:
            _remote_config_cache = RemoteConfig()
    return _remote_config_cache


__all__ = [
    "configure",
    "get_path_config",
    "get_remote_config",
    "path_config",
    "remote_config",
    "_DEFAULT_PATH_CONFIG_PATH",
    "_DEFAULT_REMOTE_CONFIG_PATH",
]
