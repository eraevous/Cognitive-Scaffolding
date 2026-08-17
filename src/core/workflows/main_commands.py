"""
Module: core_lib.workflows.main_commands 
- @ai-path: core_lib.workflows.main_commands 
- @ai-source-file: main_commands.py 
- @ai-module: main_commands 
- @ai-role: classifier 
- @ai-entrypoint: classify(), classify_large() 
- @ai-intent: "Classify parsed documents (or chunks of documents) using LLM-based Lambda summarization."

🔍 Summary:
This module contains two core functions to classify documents. `classify()` supports direct classification of single parsed files or chat logs, while `classify_large()` supports chunked classification for longer documents and merges the results. Both rely on Claude Lambda summarization and return validated `.meta.json`.

📦 Inputs:
- name (str): Filename of the parsed document (or raw for large mode)
- paths (PathConfig): Config for raw, parsed, and metadata directories
- remote (RemoteConfig, optional): AWS credentials and bucket names

📤 Outputs:
- dict: Validated metadata dictionary saved to S3

🔗 Related Modules:
- lambda_summary → sends chunks or full files to Claude Lambda
- chunk_text → used to split long documents
- merge_metadata_blocks → merges multiple chunk-level results
- schema → validates output
- s3_utils → saves final `.meta.json`

🧠 For AI Agents:
- @ai-dependencies: json, boto3, pathlib
- @ai-calls: invoke_summary(), invoke_chatlog_summary(), chunk_text(), validate_metadata(), save_metadata_s3()
- @ai-uses: PathConfig, RemoteConfig, stub_path
- @ai-tags: summarization, metadata, classification, S3, chunking, schema-validation

⚙️ Meta: 
- @ai-version: 0.3.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Move classify/classify_large logic from CLI into shared main_commands module 
- @change-summary: Refactor classification into reusable backend for CLI + batch 
- @notes: 
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from core.configuration.config_registry import get_path_config, get_remote_config
from core.configuration.path_config import PathConfig
from core.llm.invoke import summarize_text
from core.metadata.merge import merge_metadata_blocks
from core.metadata.schema import validate_metadata
from core.parsing.chunk_text import chunk_text
from core.parsing.topic_segmenter import segment_text
from core.storage.upload_local import upload_file

MAX_CHARS = 16000


def _chunk_metadata_path(name: str, paths: PathConfig) -> Path:
    return paths.metadata / f"{name}.chunks.json"


def _load_stub(name: str, paths: PathConfig) -> tuple[Dict[str, Any], Path]:
    stub_path = paths.metadata / f"{name}.stub.json"
    if stub_path.exists():
        try:
            return json.loads(stub_path.read_text("utf-8")), stub_path
        except json.JSONDecodeError:
            return {}, stub_path
    return {}, stub_path


def _write_stub(path: Path, stub: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stub, indent=2), encoding="utf-8")


def _default_file_info(name: str) -> Dict[str, str]:
    return {"source_file": name, "parsed_file": name}


def _ensure_file_info(name: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    file_info = metadata.get("file_info")
    if not isinstance(file_info, dict):
        file_info = {}
    metadata["file_info"] = {**_default_file_info(name), **file_info}
    return metadata


def _enforce_window(chunk: str) -> List[str]:
    trimmed = chunk.strip()
    if not trimmed:
        return []
    if len(trimmed) <= MAX_CHARS:
        return [trimmed]
    return chunk_text(trimmed, max_chars=MAX_CHARS)


def _chunk_texts(
    text: str, segmentation: Literal["semantic", "paragraph"], use_chunks: bool
) -> List[str]:
    if not use_chunks:
        return [text.strip()]

    if segmentation == "semantic":
        raw_chunks = segment_text(text)
        if not raw_chunks:
            raw_chunks = chunk_text(text, max_chars=MAX_CHARS)
    else:
        raw_chunks = chunk_text(text, max_chars=MAX_CHARS)

    normalized: List[str] = []
    for chunk in raw_chunks:
        normalized.extend(_enforce_window(chunk))
    return [c for c in normalized if c.strip()]


def _build_chunk_records(
    name: str,
    text: str,
    segmentation: Literal["semantic", "paragraph"],
    use_chunks: bool,
) -> List[Dict[str, Any]]:
    texts = _chunk_texts(text, segmentation, use_chunks)
    if not texts:
        texts = [text.strip()]

    stem = Path(name).stem
    records: List[Dict[str, Any]] = []
    search_pos = 0
    strategy = segmentation if use_chunks else "single"

    for idx, chunk_body in enumerate(texts):
        chunk_id = f"{stem}_chunk{idx:02d}"
        start_idx = text.find(chunk_body, search_pos)
        if start_idx == -1:
            start_idx = search_pos
        end_idx = start_idx + len(chunk_body)
        search_pos = end_idx
        records.append(
            {
                "id": chunk_id,
                "order": idx,
                "strategy": strategy,
                "text": chunk_body,
                "char_start": start_idx,
                "char_end": end_idx,
                "char_length": len(chunk_body),
            }
        )

    return records


def build_chunk_map(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "strategy": records[0]["strategy"] if records else "single",
        "context_window": MAX_CHARS,
        "count": len(records),
        "chunks": [
            {
                "id": record["id"],
                "order": record["order"],
                "char_start": record.get("char_start", 0),
                "char_end": record.get("char_end", 0),
                "char_length": record.get("char_length", 0),
            }
            for record in records
        ],
    }


def _write_chunk_metadata(
    name: str, records: List[Dict[str, Any]], paths: PathConfig
) -> None:
    chunk_path = _chunk_metadata_path(name, paths)
    payload = []
    for record in records:
        payload.append(
            {
                "id": record["id"],
                "order": record["order"],
                "strategy": record["strategy"],
                "char_start": record.get("char_start", 0),
                "char_end": record.get("char_end", 0),
                "char_length": record.get("char_length", len(record.get("text", ""))),
                "text": record.get("text", ""),
            }
        )

    chunk_path.parent.mkdir(parents=True, exist_ok=True)
    chunk_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_chunk_metadata(
    name: str, paths: PathConfig | None = None
) -> List[Dict[str, Any]]:
    paths = paths or get_path_config()
    chunk_path = _chunk_metadata_path(name, paths)
    if not chunk_path.exists():
        return []
    try:
        records = json.loads(chunk_path.read_text("utf-8"))
    except json.JSONDecodeError:
        return []

    for record in records:
        if "char_length" not in record:
            record["char_length"] = len(record.get("text", ""))
    return records


def prepare_chunk_plan(
    name: str,
    *,
    chunked: bool = False,
    segmentation: Literal["semantic", "paragraph"] = "semantic",
    paths: PathConfig | None = None,
    text: str | None = None,
) -> tuple[str, List[Dict[str, Any]]]:
    paths = paths or get_path_config()
    parsed_path = paths.parsed / name
    text = text if text is not None else parsed_path.read_text(encoding="utf-8")

    doc_type, use_chunks = detect(text, chunked)
    expected_strategy = segmentation if use_chunks else "single"

    existing_records = load_chunk_metadata(name, paths=paths)
    if existing_records and all("text" in rec for rec in existing_records):
        stored_strategy = existing_records[0].get("strategy", expected_strategy)
        if stored_strategy == expected_strategy:
            stub, stub_path = _load_stub(name, paths)
            stub["file_info"] = {
                **_default_file_info(name),
                **stub.get("file_info", {}),
            }
            stub["chunk_map"] = build_chunk_map(existing_records)
            _write_stub(stub_path, stub)
            return doc_type, existing_records

    records = _build_chunk_records(name, text, segmentation, use_chunks)
    _write_chunk_metadata(name, records, paths)

    stub, stub_path = _load_stub(name, paths)
    stub["file_info"] = {**_default_file_info(name), **stub.get("file_info", {})}
    stub["chunk_map"] = build_chunk_map(records)
    _write_stub(stub_path, stub)

    return doc_type, records


def get_parsed_text(name: str) -> str:
    paths = get_path_config()
    parsed_path = paths.parsed / name
    return parsed_path.read_text(encoding="utf-8")


def looks_like_chatlog(text: str) -> bool:
    lines = text.lower().splitlines()
    return (
        sum(
            1
            for line in lines[:50]
            if any(k in line for k in ["user:", "assistant:", "you:", "chatgpt:"])
        )
        > 2
    )


def detect(text: str, force_chunked: bool) -> tuple[str, bool]:
    """Determine document type and whether chunked summarization is required."""
    doc_type = "chatlog" if looks_like_chatlog(text) else "standard"
    use_chunks = force_chunked or len(text) > MAX_CHARS
    return doc_type, use_chunks


def segment(text: str, segmentation: Literal["semantic", "paragraph"]) -> list[str]:
    """Split text into chunks using the configured segmentation strategy."""
    return _chunk_texts(text, segmentation, True)


def summarize_records(
    records: List[Dict[str, Any]], doc_type: str
) -> tuple[dict, List[dict]]:
    """Summarize provided chunk records and merge results when necessary."""
    if not records:
        raise ValueError("No chunk records supplied for summarization")

    block_results = [
        summarize_text(record["text"], doc_type=doc_type) for record in records
    ]

    if len(block_results) == 1:
        return block_results[0], block_results

    merged = merge_metadata_blocks(block_results)
    return merged, block_results


def merge_stubs(name: str, metadata: dict, paths: PathConfig) -> dict:
    """Overlay stub metadata onto generated metadata if present."""
    stub_path = paths.metadata / f"{name}.stub.json"
    if not stub_path.exists():
        return metadata

    try:
        stub = json.loads(stub_path.read_text("utf-8"))
    except json.JSONDecodeError:
        return metadata

    file_info = stub.get("file_info")
    if isinstance(file_info, dict):
        merged_info = {**file_info, **metadata.get("file_info", {})}
        metadata["file_info"] = merged_info

    if "chunk_map" in stub and "chunk_map" not in metadata:
        metadata["chunk_map"] = stub["chunk_map"]

    for key, value in stub.items():
        if key in {"file_info", "chunk_map"}:
            continue
        metadata.setdefault(key, value)

    return metadata


def _combine_chunk_results(
    records: List[Dict[str, Any]], chunk_outputs: List[dict]
) -> List[Dict[str, Any]]:
    keys_to_copy = [
        "summary",
        "topics",
        "tags",
        "themes",
        "priority",
        "tone",
        "stage",
        "depth",
        "category",
    ]
    combined: List[Dict[str, Any]] = []
    for record, output in zip(records, chunk_outputs):
        entry: Dict[str, Any] = {
            "id": record["id"],
            "order": record["order"],
            "strategy": record["strategy"],
            "char_length": record.get("char_length", len(record.get("text", ""))),
        }
        for key in keys_to_copy:
            if key in output:
                entry[key] = output[key]
        combined.append(entry)
    return combined


def persist(name: str, metadata: dict, paths: PathConfig) -> dict:
    """Validate and write metadata to disk."""
    validate_metadata(metadata)
    out_path = paths.metadata / f"{name}.meta.json"
    out_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def classify(
    name: str,
    chunked: bool = False,
    segmentation: Literal["semantic", "paragraph"] = "semantic",
    paths: PathConfig | None = None,
    chunk_records: Optional[List[Dict[str, Any]]] = None,
) -> dict:
    """Summarize a parsed document into metadata."""
    paths = paths or get_path_config()
    parsed_path = paths.parsed / name
    text = parsed_path.read_text(encoding="utf-8")

    doc_type, use_chunks = detect(text, chunked)

    if not chunk_records:
        doc_type, chunk_records = prepare_chunk_plan(
            name,
            chunked=chunked,
            segmentation=segmentation,
            paths=paths,
            text=text,
        )
    else:
        if not all("text" in record for record in chunk_records):
            doc_type, chunk_records = prepare_chunk_plan(
                name,
                chunked=chunked,
                segmentation=segmentation,
                paths=paths,
                text=text,
            )
        else:
            stub, stub_path = _load_stub(name, paths)
            stub["file_info"] = {
                **_default_file_info(name),
                **stub.get("file_info", {}),
            }
            stub["chunk_map"] = build_chunk_map(chunk_records)
            _write_stub(stub_path, stub)
            chunk_path = _chunk_metadata_path(name, paths)
            if not chunk_path.exists():
                _write_chunk_metadata(name, chunk_records, paths)

    metadata, block_results = summarize_records(chunk_records, doc_type)
    metadata["chunk_map"] = build_chunk_map(chunk_records)
    metadata["chunks"] = _combine_chunk_results(chunk_records, block_results)
    metadata = merge_stubs(name, metadata, paths)
    metadata = _ensure_file_info(name, metadata)
    return persist(name, metadata, paths)


def upload_metadata_to_s3(name: str, metadata: dict):
    from core.storage.s3_utils import save_metadata_s3

    remote = get_remote_config()
    key = f"{remote.prefixes['metadata']}{name}.meta.json"
    save_metadata_s3(remote.bucket_name, key, metadata)


def upload_and_prepare(
    file_name: str,
    parsed_name: Optional[str] = None,
    paths: PathConfig | None = None,
):
    """Parse ``file_name`` and save stub metadata."""
    upload_file(file_name, parsed_name, paths)


def pipeline_from_upload(
    file_name: str,
    parsed_name: Optional[str] = None,
    segmentation: Literal["semantic", "paragraph"] = "semantic",
    paths: PathConfig | None = None,
) -> dict:
    """Upload, parse, and classify a single document."""
    upload_and_prepare(file_name, parsed_name, paths)
    txt_name = (
        parsed_name
        or Path(file_name).stem.replace(" ", "_").replace("-", "_").lower() + ".txt"
    )
    metadata = classify(txt_name, segmentation=segmentation, paths=paths)
    return metadata
