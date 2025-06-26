# config_registry.py

from pathlib import Path

from core.config.path_config import PathConfig
from core.config.remote_config import RemoteConfig

_path_instance = None
_remote_instance = None

path_config = Path("src/core/config/path_config.json")
remote_config = Path("src/core/config/remote_config.json")

def get_path_config(force_reload=False):
    global _path_instance
    if _path_instance is None or force_reload:
        _path_instance = PathConfig.from_file(path_config) if path_config else PathConfig()
    return _path_instance

def get_remote_config(force_reload=False):
    global _remote_instance
    if _remote_instance is None or force_reload:
        _remote_instance = RemoteConfig.from_file(remote_config) if remote_config else RemoteConfig()
    return _remote_instance
