"""
Module: remote_config.py
Role: Load remote service settings for AWS, OpenAI, and future integrations.

🔍 Summary:
- Centralizes all credentials and endpoint settings
- Replaces config.py reliance for remote services
- Keeps setup user-friendly for non-developers

📦 Inputs:
- remote_config.json (located next to this module)

📤 Outputs:
- RemoteConfig object with properties like bucket, region, API keys

🧠 For AI Agents:
- Reduces environment reliance for simpler onboarding
- Can be extended for Claude, Replicate, etc.

🔗 Related Modules:
- aws_clients.py
- s3_utils.py, lambda_summary.py
- any OpenAI-based CLI tool

TODOs:
- [x] Add .from_env fallback for cloud mode

AI-Assistance Tags:
@ai-role: service_config_loader
@ai-entrypoint: RemoteConfig.from_file()
@ai-intent: "Load and manage external service credentials and endpoints"
@ai-version: 0.1.0
"""

# remote_config.py (File-backed with environment fallback)

import json
import os
from pathlib import Path
from typing import Dict, Union

from core.constants import (
    DEFAULT_S3_PREFIXES,
    ERROR_REMOTE_CONFIG_MISSING_FIELDS,
)
from core.logger import get_logger


class RemoteConfig:
    def __init__(
        self,
        bucket_name: str,
        lambda_name: str,
        region: str,
        root: Union[str, Path],
        openai_api_key: str,
        prefixes: dict,
    ):
        self.root = Path(root).expanduser().resolve()
        self.bucket_name = bucket_name
        self.lambda_name = lambda_name
        self.region = region
        self.openai_api_key = openai_api_key
        self.prefixes = prefixes

    def __repr__(self):
        return (
            f"ROOT:     {self.root}\n"
            f"S3 Bucket: {self.bucket_name}\n"
            f"Lambda:    {self.lambda_name} ({self.region})\n"
            f"Prefixes:  {self.prefixes}\n"
            f"OpenAI:    {'set' if self.openai_api_key else 'missing'}\n"
        )

    @classmethod
    def _from_environment(cls, missing_path: Path) -> "RemoteConfig":
        logger = get_logger(__name__)
        logger.warning(
            "Remote config not found at %s; using environment defaults.",
            missing_path,
        )

        project_root = Path(
            os.getenv("PROJECT_ROOT", Path.cwd())
        ).expanduser().resolve()

        prefixes: Dict[str, str] = {
            key: os.getenv(f"S3_PREFIX_{key.upper()}", default)
            for key, default in DEFAULT_S3_PREFIXES.items()
        }

        return cls(
            bucket_name=os.getenv("AWS_BUCKET_NAME", ""),
            lambda_name=os.getenv("AWS_LAMBDA_NAME", ""),
            region=os.getenv("AWS_REGION", "us-east-1"),
            root=project_root,
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            prefixes=prefixes,
        )

    @classmethod
    def from_file(
        cls,
        config_path: Union[str, Path] = Path(__file__).with_name("remote_config.json"),
    ):
        """
        Load a RemoteConfig from a JSON file.

        Requires full specification of all required fields.
        {
            "bucket_name": "your-bucket",
            "lambda_name": "your-lambda",
            "region": "us-east-1",
            "root": "C:/your/project",
            "openai_api_key": "sk-...",
            "prefixes": {
                "raw": "raw/",
                "parsed": "parsed/",
                "stub": "stub/",
                "metadata": "metadata/"
            }
        }
        """
        config_path = Path(config_path).expanduser().resolve()
        if not config_path.exists():
            return cls._from_environment(config_path)

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_keys = [
            "bucket_name",
            "lambda_name",
            "region",
            "root",
            "openai_api_key",
            "prefixes",
        ]
        missing = [k for k in required_keys if k not in data]
        if missing:
            raise KeyError(ERROR_REMOTE_CONFIG_MISSING_FIELDS.format(fields=missing))

        return cls(
            bucket_name=data["bucket_name"],
            lambda_name=data["lambda_name"],
            region=data["region"],
            root=data["root"],
            openai_api_key=data["openai_api_key"],
            prefixes=data["prefixes"],
        )
