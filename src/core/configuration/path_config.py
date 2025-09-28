"""Path configuration utilities for core workflows."""

import json
import os
from pathlib import Path
from typing import Union

from core.constants import DEFAULT_METADATA_SCHEMA_PATH, ERROR_PATH_RESOLVE_FAILURE
from core.logger import get_logger

logger = get_logger(__name__)


class PathConfig:
    def __init__(
        self,
        root: Union[str, Path] = None,
        raw: Union[str, Path] = None,
        parsed: Union[str, Path] = None,
        metadata: Union[str, Path] = None,
        output: Union[str, Path] = None,
        vector: Union[str, Path] = None,
        schema: Union[str, Path, None] = None,
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
        schema_candidate = (
            schema if schema is not None else os.getenv("METADATA_SCHEMA_PATH")
        )
        self.schema = self._resolve_path_relative_to_root(
            schema_candidate, default=DEFAULT_METADATA_SCHEMA_PATH
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
        cls,
        config_path: Union[str, Path] = Path(__file__).with_name("path_config.json"),
        *,
        schema_path: Union[str, Path, None] = None,
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
            "vector": "vector"
        }
        """
        config_path = Path(config_path).expanduser().resolve()
        if not config_path.exists():
            logger.warning(
                "Path config not found at %s; using default PathConfig.",
                config_path,
            )
            return cls()

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        return cls(
            root=config.get("root"),
            raw=config.get("raw"),
            parsed=config.get("parsed"),
            metadata=config.get("metadata"),
            output=config.get("output"),
            vector=config.get("vector"),
            schema=schema_path,
            semantic_chunking=config.get("semantic_chunking", False),
        )
