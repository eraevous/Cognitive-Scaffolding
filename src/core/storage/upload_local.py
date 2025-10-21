import json
from pathlib import Path
from typing import Any, Dict

from core.configuration.config_registry import get_path_config
from core.configuration.path_config import PathConfig
from core.logger import get_logger
from core.parsing.extract_text import extract_text

logger = get_logger(__name__)


def _build_file_info(
    *,
    source_path: Path,
    parsed_path: Path,
    text: str,
) -> Dict[str, Any]:
    """Return structured file metadata stored alongside classification output."""

    words = text.split()
    return {
        "source_file": str(source_path),
        "parsed_file": str(parsed_path),
        "source_ext": source_path.suffix.lower().lstrip("."),
        "word_count": len(words),
        "char_count": len(text),
    }


def prepare_document_for_processing(
    file_path: Path,
    parsed_name: str | None = None,
    paths: PathConfig | None = None,
) -> dict:
    """
    Convert a raw document into parsed text and save a structured stub locally.

    Args:
        file_path (Path): Full path to the raw file
        parsed_name (str | None): Optional override for parsed .txt filename
        paths (PathConfig | None): Directory configuration override

    Returns:
        dict: Stub metadata containing file information and chunk placeholder
    """
    file_path = Path(file_path)
    paths = paths or get_path_config()
    paths.raw.mkdir(parents=True, exist_ok=True)
    paths.parsed.mkdir(parents=True, exist_ok=True)
    paths.metadata.mkdir(parents=True, exist_ok=True)

    original_name = file_path.name
    parsed_name = (
        parsed_name
        or file_path.stem.replace(" ", "_").replace("-", "_").lower() + ".txt"
    )

    dest_raw = paths.raw / original_name
    dest_raw.write_bytes(file_path.read_bytes())

    try:
        text = extract_text(str(file_path))
    except Exception as e:
        raise ValueError(f"Failed to extract text from {original_name}: {e}")

    dest_parsed = paths.parsed / parsed_name
    dest_parsed.write_text(text, encoding="utf-8")

    stub = {
        "file_info": _build_file_info(
            source_path=dest_raw, parsed_path=dest_parsed, text=text
        ),
        "chunk_map": None,
    }

    stub_file = paths.metadata / f"{parsed_name}.stub.json"
    stub_file.write_text(json.dumps(stub, indent=2), encoding="utf-8")

    logger.info("Prepared %s → %s", dest_raw.name, dest_parsed.name)
    return stub


def upload_file(
    file_path: Path,
    parsed_name: str | None = None,
    paths: PathConfig | None = None,
) -> dict:
    """
    Alias for prepare_document_for_processing.
    Maintained for compatibility with legacy calls.
    """
    return prepare_document_for_processing(file_path, parsed_name, paths)
