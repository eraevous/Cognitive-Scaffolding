from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict


_CHUNK_SUFFIX = re.compile(r"_chunk\d+$")


def source_id(result_id: str) -> str:
    """Return the source document id for a chunk or document result id."""

    return _CHUNK_SUFFIX.sub("", result_id)


def chunk_label(result_id: str) -> str:
    match = _CHUNK_SUFFIX.search(result_id)
    return match.group(0).lstrip("_") if match else ""


def load_chatgpt_manifest(root: Path) -> Dict[str, Dict[str, Any]]:
    manifest_path = root / "metadata" / "chatgpt" / "chatgpt_manifest.json"
    if not manifest_path.exists():
        return {}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    records = manifest.get("records", {})
    return records if isinstance(records, dict) else {}


def enrich_result(root: Path, result_id: str) -> Dict[str, Any]:
    doc_id = source_id(result_id)
    records = load_chatgpt_manifest(root)
    record = records.get(doc_id, {})
    return {
        "result_id": result_id,
        "doc_id": doc_id,
        "chunk": chunk_label(result_id),
        "title": record.get("title", doc_id),
        "parsed_path": record.get("parsed_path", ""),
        "create_time": record.get("create_time"),
        "update_time": record.get("update_time"),
    }
