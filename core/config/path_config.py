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

from pathlib import Path
import json
from typing import Union

class PathConfig:
    def __init__(
        self,
        root: Path = None,
        raw: Path = None,
        parsed: Path = None,
        metadata: Path = None,
        output: Path = None,
        schema: Path = None,
    ):
        """
        Initialize a PathConfig object for controlling storage paths.

        Args:
            root (Path | str): Optional base directory. Defaults to cwd.
            raw (Path | str): Path to raw/ folder (default: root/raw)
            parsed (Path | str): Path to parsed/ folder (default: root/parsed)
            metadata (Path | str): Path to metadata/ folder (default: root/metadata)
            output (Path | str): Path to output/ folder (default: root/output)
        """
        self.root = Path(root or ".").resolve()
        self.raw = Path(raw or self.root / "raw")
        self.parsed = Path(parsed or self.root / "parsed")
        self.metadata = Path(metadata or self.root / "metadata")
        self.output = Path(output or self.root / "output")
        self.schema = Path(schema or self.root / "schema")

    def __repr__(self):
        return (
            f"RAW:      {self.raw}\n"
            f"PARSED:   {self.parsed}\n"
            f"METADATA: {self.metadata}\n"
            f"OUTPUT:   {self.output}\n"
            f"SCHEMA:   {self.schema}\n"
        )

    @classmethod
    def from_file(cls, config_path: Union[str, Path] = f"{Path(".").resolve()}\\config\\path_config.json"):
        """
        Load a PathConfig from a JSON file.

        The file can contain:
        {
            "root": "/project/data",
            "raw": "raw",
            "parsed": "parsed_docs",
            "metadata": "meta",
            "output": "clustered"
            "schema": "metadata_schema.json"
        }

        Returns:
            PathConfig instance
        """
        print(config_path)
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        return cls(
            root=config.get("root"),
            raw=config.get("raw"),
            parsed=config.get("parsed"),
            metadata=config.get("metadata"),
            output=config.get("output"),
            schema=config.get("schema")
        )
    