"""Local filesystem ingestion helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from core.configuration import config_registry
from core.configuration.path_config import PathConfig
from core.parsing.extract_text import extract_text
from core.parsing.normalize import normalize_filename
from core.utils.logger import get_logger

logger = get_logger(__name__)


def _resolve_paths(paths: Optional[PathConfig]) -> PathConfig:
    return paths or config_registry.get_path_config()


def _ensure_directories(paths: PathConfig) -> None:
    for attr in ("raw", "parsed", "metadata"):
        Path(getattr(paths, attr)).mkdir(parents=True, exist_ok=True)


def prepare_document_for_processing(
    file_path: Path | str,
    *,
    parsed_name: str | None = None,
    paths: PathConfig | None = None,
) -> dict[str, str]:
    """Copy ``file_path`` into the ingestion directories and emit a stub payload."""

    source = Path(file_path)
    if not source.exists():
        raise FileNotFoundError(source)

    cfg = _resolve_paths(paths)
    _ensure_directories(cfg)

    raw_dir = Path(cfg.raw)
    parsed_dir = Path(cfg.parsed)
    metadata_dir = Path(cfg.metadata)

    raw_dest = raw_dir / source.name
    raw_dest.write_bytes(source.read_bytes())

    safe_name = parsed_name or f"{normalize_filename(source.stem)}.txt"
    parsed_dest = parsed_dir / safe_name
    text = extract_text(source)
    parsed_dest.write_text(text, encoding="utf-8")

    stub = {
        "raw_path": str(raw_dest),
        "parsed_path": str(parsed_dest),
        "source_name": source.name,
    }
    stub_path = metadata_dir / f"{safe_name}.stub.json"
    stub_path.write_text(json.dumps(stub, indent=2), encoding="utf-8")
    stub["stub_path"] = str(stub_path)

    logger.info("Prepared %s -> %s", source, parsed_dest)
    return stub


def upload_file(
    file_path: Path | str,
    *,
    parsed_name: str | None = None,
    paths: PathConfig | None = None,
) -> Path:
    """Convenience wrapper returning the parsed file path."""

    stub = prepare_document_for_processing(file_path, parsed_name=parsed_name, paths=paths)
    return Path(stub["parsed_path"])


__all__ = ["prepare_document_for_processing", "upload_file"]
