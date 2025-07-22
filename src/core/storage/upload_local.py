import json
from pathlib import Path

from core.config.config_registry import get_path_config
from core.config.path_config import PathConfig
from core.parsing.extract_text import extract_text

def prepare_document_for_processing(
    file_path: Path,
    parsed_name: str | None = None,
    paths: PathConfig | None = None,
) -> dict:
    """
    Convert a raw document into parsed text and save a stub locally.

    Args:
        file_path (Path): Full path to the raw file
        parsed_name (str | None): Optional override for parsed .txt filename
        paths (PathConfig | None): Directory configuration override

    Returns:
        dict: Stub metadata linking source and parsed files
    """
    file_path = Path(file_path)
    paths = paths or get_path_config()
    paths.raw.mkdir(parents=True, exist_ok=True)
    paths.parsed.mkdir(parents=True, exist_ok=True)
    paths.metadata.mkdir(parents=True, exist_ok=True)

    original_name = file_path.name
    parsed_name = parsed_name or file_path.stem.replace(" ", "_").replace("-", "_").lower() + ".txt"

    # Copy raw file
    dest_raw = paths.raw / original_name
    dest_raw.write_bytes(file_path.read_bytes())

    # Extract text and save parsed file
    try:
        text = extract_text(str(file_path))
    except Exception as e:
        raise ValueError(f"Failed to extract text from {original_name}: {e}")

    dest_parsed = paths.parsed / parsed_name
    dest_parsed.write_text(text, encoding="utf-8")

    # Write stub
    stub = {
        "source_file": str(dest_raw),
        "parsed_file": str(dest_parsed),
        "source_ext": file_path.suffix.lower().lstrip(".")
    }

    stub_file = paths.metadata / f"{parsed_name}.stub.json"
    stub_file.write_text(json.dumps(stub, indent=2), encoding="utf-8")

    print(f"Saved stub locally: {stub_file}")
    print(f"Uploaded parsed version to: {dest_parsed}")

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