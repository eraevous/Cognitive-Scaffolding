"""
Module: remote_config.py
Role: Load remote service settings for AWS, OpenAI, and future integrations.

🔍 Summary:
- Centralizes all credentials and endpoint settings
- Replaces config.py reliance for remote services
- Keeps setup user-friendly for non-developers

📦 Inputs:
- remote_config.json

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
- [ ] Add .from_env fallback for cloud mode

AI-Assistance Tags:
@ai-role: service_config_loader
@ai-entrypoint: RemoteConfig.from_file()
@ai-intent: "Load and manage external service credentials and endpoints"
@ai-version: 0.1.0
"""

import json
from pathlib import Path
from typing import Union


class RemoteConfig:
    def __init__(
        self,
        bucket_name: str,
        lambda_name: str,
        region: str = "us-east-1",
        root: Union[str, Path] = None,
        openai_api_key: str = None,
        prefixes: dict = None
    ):
        self.root = Path(root).expanduser().resolve() if root else Path(".").resolve()
        self.bucket_name = bucket_name
        self.lambda_name = lambda_name
        self.region = region
        self.openai_api_key = openai_api_key
        self.prefixes = prefixes or {
            "raw": "raw/",
            "parsed": "parsed/",
            "stub": "stub/",
            "metadata": "metadata/"
        }

    def __repr__(self):
        return (
            f"ROOT:     {self.root}\n"
            f"S3 Bucket: {self.bucket_name}\n"
            f"Lambda:    {self.lambda_name} ({self.region})\n"
            f"Prefixes:  {self.prefixes}\n"
            f"OpenAI:    {'set' if self.openai_api_key else 'missing'}\n"
        )

    @classmethod
    def from_file(cls, config_path: Union[str, Path] = Path("core/config/remote_config.json")):
        config_path = Path(config_path).expanduser().resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Remote config file not found at: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(
            bucket_name=data.get("bucket_name"),
            lambda_name=data.get("lambda_name"),
            region=data.get("region", "us-east-1"),
            root=data.get("root"),
            openai_api_key=data.get("openai_api_key"),
            prefixes=data.get("prefixes", {})
        )
