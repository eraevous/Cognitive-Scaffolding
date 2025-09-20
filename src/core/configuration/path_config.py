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

from core.constants import (
    DEFAULT_METADATA_SCHEMA_PATH,
    ERROR_PATH_CONFIG_NOT_FOUND,
    ERROR_PATH_RESOLVE_FAILURE,
)


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
        self.metadata = self._resolve_path_relative_to_root(
            metadata, default="metadata"
        )
        self.output = self._resolve_path_relative_to_root(output, default="output")
        self.vector = self._resolve_path_relative_to_root(vector, default="vector")
        self.schema = self._resolve_path_relative_to_root(
            schema, default=DEFAULT_METADATA_SCHEMA_PATH
        )
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
            raise ValueError(
                ERROR_PATH_RESOLVE_FAILURE.format(value=path_value, error=e)
            )

    @classmethod
    def from_file(
        cls, config_path: Union[str, Path] = Path(__file__).with_name("path_config.json")
    ):
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
            raise FileNotFoundError(
                ERROR_PATH_CONFIG_NOT_FOUND.format(path=config_path)
            )

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
            semantic_chunking=config.get("semantic_chunking", False),
        )
