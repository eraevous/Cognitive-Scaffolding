"""Backwards compatible configuration namespace."""

from core.configuration import config_registry as config_registry
from core.configuration.path_config import PathConfig, validate_schema_path
from core.configuration.remote_config import RemoteConfig

__all__ = [
    "config_registry",
    "PathConfig",
    "RemoteConfig",
    "validate_schema_path",
]
