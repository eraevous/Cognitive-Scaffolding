#__________________________________________________________________
# File: __init__.py
# No docstring found


#__________________________________________________________________
# File: config_registry.py
# No docstring found

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
#__________________________________________________________________
# File: llm_config.py
# No docstring found

#__________________________________________________________________
# File: path_config.py
"""
Module: path_config.py
Role: Centralized configuration for filesystem paths (raw, parsed, metadata, output).

🔍 Summary:
- Decouples file storage from code location
- Supports flexible directory roots per project or environment
- Can load from CLI, config file, or defaults
- Used across all pipeline stages (parse, classify, organize, cluster)

📦 Inputs:
- root (Path or str): Base directory for the project (optional)
- raw, parsed, metadata, output (Path or str): Specific overrides for subfolders
- config_file (str | Path): Optional path to a JSON or YAML config file

📤 Outputs:
- path_config.raw → Path to raw documents
- path_config.parsed → Path to parsed .txt files
- path_config.metadata → Path to .meta.json files
- path_config.output → Path to exported summaries or plots

🧠 For AI Agents:
- Ensures file access is consistent and portable
- Avoids hardcoded directory names in CLI or workflows
- Safe for integration testing or cloud deployments

🔗 Related Modules:
- Used in classify_all, organize_all, export, etc.

TODOs:
- [x] Add `.from_file()` to read from JSON
- [ ] Add support for environment or .env

AI-Assistance Tags:
@ai-role: config_paths
@ai-dependencies: pathlib, json
@ai-entrypoint: PathConfig
@ai-intent: "Encapsulate and customize filesystem structure for this project"
@ai-version: 0.2.0
"""

"""
Module: path_config.py
Role: Centralized configuration for filesystem paths (raw, parsed, metadata, output).

🔍 Summary:
- Decouples file storage from code location
- Supports flexible directory roots per project or environment
- Can load from CLI, config file, or defaults
- Used across all pipeline stages (parse, classify, organize, cluster)

📦 Inputs:
- root (Path or str): Base directory for the project (optional)
- raw, parsed, metadata, output (Path or str): Specific overrides for subfolders
- config_file (str | Path): Optional path to a JSON or YAML config file

📤 Outputs:
- path_config.raw → Path to raw documents
- path_config.parsed → Path to parsed .txt files
- path_config.metadata → Path to .meta.json files
- path_config.output → Path to exported summaries or plots

🧠 For AI Agents:
- Ensures file access is consistent and portable
- Avoids hardcoded directory names in CLI or workflows
- Safe for integration testing or cloud deployments

🔗 Related Modules:
- Used in classify_all, organize_all, export, etc.

TODOs:
- [x] Add `.from_file()` to read from JSON
- [ ] Add support for environment or .env

AI-Assistance Tags:
@ai-role: config_paths
@ai-dependencies: pathlib, json
@ai-entrypoint: PathConfig
@ai-intent: "Encapsulate and customize filesystem structure for this project"
@ai-version: 0.2.0
"""

import json
from pathlib import Path
from typing import Union


class PathConfig:
    def __init__(
        self,
        root: Union[str, Path] = None,
        raw: Union[str, Path] = None,
        parsed: Union[str, Path] = None,
        metadata: Union[str, Path] = None,
        output: Union[str, Path] = None,
        vector: Union[str, Path] = None,
        schema: Union[str, Path] = None,
        semantic_chunking: bool = False,
    ):
        # Use the root provided (do not resolve relative to codebase)
        self.root = Path(root).expanduser().resolve() if root else Path(".").resolve()
        self.raw = self._resolve_path_relative_to_root(raw, default="raw")
        self.parsed = self._resolve_path_relative_to_root(parsed, default="parsed")
        self.metadata = self._resolve_path_relative_to_root(metadata, default="metadata")
        self.output = self._resolve_path_relative_to_root(output, default="output")
        self.vector = self._resolve_path_relative_to_root(vector, default="vector")
        self.schema = self._resolve_path_relative_to_root(schema, default="config/metadata_schema.json")
        self.semantic_chunking = bool(semantic_chunking)

    def __repr__(self):
        return (
            f"ROOT:     {self.root}\n"
            f"RAW:      {self.raw}\n"
            f"PARSED:   {self.parsed}\n"
            f"METADATA: {self.metadata}\n"
            f"OUTPUT:   {self.output}\n"
            f"VECTOR:   {self.vector}\n"
            f"SCHEMA:   {self.schema}\n"
            f"SEMANTIC_CHUNKING: {self.semantic_chunking}\n"
        )

    def _resolve_path_relative_to_root(self, path_value, default):
        try:
            path = Path(path_value or default)
            return path if path.is_absolute() else (self.root / path).resolve()
        except Exception as e:
            raise ValueError(f"Failed to resolve path relative to root: {path_value}\n{e}")

    @classmethod
    def from_file(cls, config_path: Union[str, Path] = Path("core/config/path_config.json")):
        """
        Load a PathConfig from a JSON file.

        Expected format:
        {
            "root": "C:/my/project/dir",
            "raw": "raw",
            "parsed": "parsed_docs",
            "metadata": "meta",
            "output": "clustered",
            "vector": "vector",
            "schema": "config/metadata_schema.json"
        }
        """
        config_path = Path(config_path).expanduser().resolve()
        if not config_path.exists():
            raise FileNotFoundError(f"Path config file not found at: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        return cls(
            root=config.get("root"),
            raw=config.get("raw"),
            parsed=config.get("parsed"),
            metadata=config.get("metadata"),
            output=config.get("output"),
            vector=config.get("vector"),
            schema=config.get("schema"),
            semantic_chunking=config.get("semantic_chunking", False)
        )
#__________________________________________________________________
# File: remote_config.py
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

# remote_config.py (Enforced Explicit Config Path — No Defaults Allowed)

import json
from pathlib import Path
from typing import Union


class RemoteConfig:
    def __init__(
        self,
        bucket_name: str,
        lambda_name: str,
        region: str,
        root: Union[str, Path],
        openai_api_key: str,
        prefixes: dict
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
    def from_file(cls, config_path: Union[str, Path] = Path("core/config/remote_config.json")):
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
            raise FileNotFoundError(f"Remote config file not found at: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        required_keys = ["bucket_name", "lambda_name", "region", "root", "openai_api_key", "prefixes"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            raise KeyError(f"Missing required remote config fields: {missing}")

        return cls(
            bucket_name=data["bucket_name"],
            lambda_name=data["lambda_name"],
            region=data["region"],
            root=data["root"],
            openai_api_key=data["openai_api_key"],
            prefixes=data["prefixes"]
        )