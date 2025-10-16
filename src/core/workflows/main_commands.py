"""High level document classification workflow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

from core.configuration import config_registry
from core.configuration.path_config import PathConfig
from core.metadata.schema import validate_metadata
from core.parsing.semantic_chunk import semantic_chunk
from core.storage.upload_local import upload_file
from core.synthesis.summarizer import summarize_text as _default_summarize


def segment_text(text: str) -> List[str]:
    """Naive paragraph segmentation used when semantic mode is disabled."""

    segments = [segment.strip() for segment in text.split("\n\n") if segment.strip()]
    return segments or [text.strip()]


def summarize_text(text: str, doc_type: str = "standard") -> dict[str, object]:
    """Delegate to the shared summarizer with a sensible default."""

    return _default_summarize(text, doc_type=doc_type)


def classify(
    file_name: str,
    *,
    chunked: bool = False,
    segmentation: str = "semantic",
    paths: Optional[PathConfig] = None,
) -> dict:
    """Generate metadata for ``file_name`` and persist it alongside the document."""

    paths = paths or config_registry.get_path_config()
    parsed_path = Path(paths.parsed) / file_name
    text = parsed_path.read_text(encoding="utf-8")

    if chunked and segmentation == "semantic":
        chunks = semantic_chunk(text)
        combined = "\n".join(chunk["text"] for chunk in chunks)
    elif chunked:
        combined = "\n".join(segment_text(text))
    else:
        combined = text

    metadata = summarize_text(combined, doc_type=segmentation)
    validate_metadata(metadata)

    metadata_dir = Path(paths.metadata)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    meta_path = metadata_dir / f"{file_name}.meta.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def upload_and_prepare(path: Path, *, paths: Optional[PathConfig] = None) -> Path:
    """Copy ``path`` into the ingestion directories and return the parsed path."""

    parsed = upload_file(path, paths=paths)
    return parsed


__all__ = ["classify", "segment_text", "summarize_text", "upload_and_prepare"]
