from __future__ import annotations

import os
import sys
from importlib import import_module
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

from core.configuration import config_registry as _config_registry
from core.configuration.path_config import PathConfig
from core.configuration.remote_config import RemoteConfig
from core.constants import DEFAULT_S3_DOWNLOAD_PREFIX, DEFAULT_S3_PREFIXES

load_dotenv()


def _resolve_path_setting(env_name: str, default: Path) -> Path:
    default = Path(default).expanduser().resolve()
    value = os.getenv(env_name)
    if not value:
        return default
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (default.parent / candidate).resolve()


BASE_DIR = (
    Path(os.getenv("PROJECT_ROOT", Path(__file__).resolve().parents[1]))
    .expanduser()
    .resolve()
)
CONFIG_DIR = _resolve_path_setting("CONFIG_DIR", BASE_DIR / "config")
REMOTE_CONFIG_PATH = _resolve_path_setting(
    "REMOTE_CONFIG_PATH", CONFIG_DIR / "remote_config.json"
)
PATH_CONFIG_PATH = _resolve_path_setting(
    "PATH_CONFIG_PATH", CONFIG_DIR / "path_config.json"
)

AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")
AWS_LAMBDA_NAME = os.getenv("AWS_LAMBDA_NAME")

S3_PREFIXES: Dict[str, str] = {
    key: os.getenv(f"S3_PREFIX_{key.upper()}", default)
    for key, default in DEFAULT_S3_PREFIXES.items()
}
S3_DOWNLOAD_PREFIX = os.getenv(
    "S3_DOWNLOAD_PREFIX",
    S3_PREFIXES.get("raw", DEFAULT_S3_DOWNLOAD_PREFIX),
)

_LOCAL_DEFAULTS = {
    "RAW": BASE_DIR / "raw",
    "PARSED": BASE_DIR / "parsed",
    "METADATA": BASE_DIR / "metadata",
    "OUTPUT": BASE_DIR / "output",
    "ORGANIZED": BASE_DIR / "organized",
}
LOCAL_RAW_DIR = _resolve_path_setting("LOCAL_RAW_DIR", _LOCAL_DEFAULTS["RAW"])
LOCAL_PARSED_DIR = _resolve_path_setting("LOCAL_PARSED_DIR", _LOCAL_DEFAULTS["PARSED"])
LOCAL_METADATA_DIR = _resolve_path_setting(
    "LOCAL_METADATA_DIR", _LOCAL_DEFAULTS["METADATA"]
)
LOCAL_OUTPUT_DIR = _resolve_path_setting("LOCAL_OUTPUT_DIR", _LOCAL_DEFAULTS["OUTPUT"])
LOCAL_ORGANIZED_DIR = _resolve_path_setting(
    "LOCAL_ORGANIZED_DIR", _LOCAL_DEFAULTS["ORGANIZED"]
)

_config_registry.configure(
    path_config_path=PATH_CONFIG_PATH,
    remote_config_path=REMOTE_CONFIG_PATH,
)

get_path_config = _config_registry.get_path_config
get_remote_config = _config_registry.get_remote_config
configure_registry = _config_registry.configure

for module_name in ("config_registry", "path_config", "remote_config", "llm_config"):
    sys.modules[f"{__name__}.{module_name}"] = import_module(
        f"core.configuration.{module_name}"
    )

__all__ = [
    "AWS_BUCKET_NAME",
    "AWS_LAMBDA_NAME",
    "AWS_REGION",
    "BASE_DIR",
    "CONFIG_DIR",
    "LOCAL_METADATA_DIR",
    "LOCAL_ORGANIZED_DIR",
    "LOCAL_OUTPUT_DIR",
    "LOCAL_PARSED_DIR",
    "LOCAL_RAW_DIR",
    "PATH_CONFIG_PATH",
    "REMOTE_CONFIG_PATH",
    "S3_DOWNLOAD_PREFIX",
    "S3_PREFIXES",
    "PathConfig",
    "RemoteConfig",
    "get_path_config",
    "get_remote_config",
    "configure_registry",
]
