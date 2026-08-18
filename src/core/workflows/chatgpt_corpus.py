from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from core.configuration.path_config import PathConfig
from core.embeddings.embedder import generate_embeddings
from core.parsing.normalize import normalize_filename
from core.parsing.openai_export import _extract_messages, _load_conversations


MANIFEST_NAME = "chatgpt_manifest.json"


@dataclass
class ChatGPTIngestResult:
    root: Path
    parsed_dir: Path
    manifest_path: Path
    total: int
    written: int
    skipped: int
    skipped_empty: int
    embedded: bool


def _conversation_key(convo: Dict[str, Any], index: int) -> str:
    stable_id = convo.get("id") or convo.get("conversation_id")
    if stable_id:
        return normalize_filename(str(stable_id))[:48]
    title = normalize_filename(str(convo.get("title") or f"conversation_{index}"))[:32]
    return f"{index:04d}_{title}"


def _render_transcript(convo: Dict[str, Any]) -> tuple[str, int, int]:
    lines: List[str] = []
    user_messages = 0
    assistant_messages = 0

    for role, text in _extract_messages(convo):
        clean = text.strip()
        if not clean:
            continue
        if role == "user":
            user_messages += 1
        elif role == "assistant":
            assistant_messages += 1
        lines.append(f"{role.upper()}: {clean}")

    return "\n".join(lines), user_messages, assistant_messages


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_manifest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"records": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"records": {}}


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_paths(root: Path, *, semantic_chunking: bool = False) -> PathConfig:
    return PathConfig(
        root=root,
        raw=root / "raw",
        parsed=root / "parsed",
        metadata=root / "metadata",
        output=root / "output",
        vector=root / "vector",
        semantic_chunking=semantic_chunking,
    )


def ingest_chatgpt_export(
    export_path: Path,
    root: Path,
    *,
    overwrite: bool = False,
    embed: bool = True,
    model: str = "text-embedding-3-small",
    semantic_chunking: bool = False,
    index_name: str = "default",
) -> ChatGPTIngestResult:
    """Parse a ChatGPT export into a searchable local corpus.

    The MVP path intentionally embeds parsed conversation text directly. LLM
    metadata/classification can be layered on later without blocking search.
    """

    export_path = Path(export_path)
    root = Path(root).expanduser().resolve()
    paths = _build_paths(root, semantic_chunking=semantic_chunking)
    parsed_dir = paths.parsed / "chatgpt"
    metadata_dir = paths.metadata / "chatgpt"
    manifest_path = metadata_dir / MANIFEST_NAME

    for directory in (
        paths.raw,
        paths.parsed,
        paths.metadata,
        paths.output,
        paths.vector,
        parsed_dir,
        metadata_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    conversations = _load_conversations(export_path)
    old_manifest = _load_manifest(manifest_path)
    old_records = old_manifest.get("records", {})
    records: Dict[str, Dict[str, Any]] = {}
    written = 0
    skipped = 0
    skipped_empty = 0

    for index, convo in enumerate(conversations):
        key = _conversation_key(convo, index)
        title = str(convo.get("title") or f"Conversation {index}")
        transcript, user_count, assistant_count = _render_transcript(convo)
        if not transcript.strip():
            skipped_empty += 1
            continue
        content_hash = _hash_text(transcript)
        parsed_path = parsed_dir / f"{key}.txt"
        meta_path = metadata_dir / f"{key}.json"
        previous = old_records.get(key, {})
        unchanged = (
            previous.get("content_hash") == content_hash
            and parsed_path.exists()
            and not overwrite
        )

        record = {
            "key": key,
            "title": title,
            "source_index": index,
            "create_time": convo.get("create_time"),
            "update_time": convo.get("update_time"),
            "content_hash": content_hash,
            "parsed_path": str(parsed_path.relative_to(root)),
            "metadata_path": str(meta_path.relative_to(root)),
            "message_count": user_count + assistant_count,
            "user_message_count": user_count,
            "assistant_message_count": assistant_count,
            "char_count": len(transcript),
            "word_count": len(transcript.split()),
        }
        records[key] = record

        if unchanged:
            skipped += 1
            continue

        parsed_path.write_text(transcript, encoding="utf-8")
        _write_json(meta_path, record)
        written += 1

    manifest = {
        "source_export": str(export_path),
        "total": len(conversations),
        "written": written,
        "skipped": skipped,
        "skipped_empty": skipped_empty,
        "records": records,
    }
    _write_json(manifest_path, manifest)

    vector_dir = paths.vector if index_name == "default" else paths.vector / index_name
    index_path = vector_dir / "mosaic.index"
    should_embed = embed and (written > 0 or overwrite or not index_path.exists())
    if should_embed:
        generate_embeddings(
            source_dir=parsed_dir,
            method="parsed",
            out_path=(
                root / "rich_doc_embeddings.json"
                if index_name == "default"
                else vector_dir / "rich_doc_embeddings.json"
            ),
            model=model,
            segment_mode=semantic_chunking,
            chunk_dir=vector_dir / "chunks",
            paths=paths,
            vector_name=index_name,
        )

    return ChatGPTIngestResult(
        root=root,
        parsed_dir=parsed_dir,
        manifest_path=manifest_path,
        total=len(conversations),
        written=written,
        skipped=skipped,
        skipped_empty=skipped_empty,
        embedded=should_embed,
    )


def repair_chatgpt_embeddings(
    root: Path,
    *,
    model: str = "text-embedding-3-small",
    semantic_chunking: bool = False,
    index_name: str = "default",
) -> Path:
    """Append embeddings for parsed transcripts missing from the existing index."""

    root = Path(root).expanduser().resolve()
    paths = _build_paths(root, semantic_chunking=semantic_chunking)
    parsed_dir = paths.parsed / "chatgpt"
    vector_dir = paths.vector if index_name == "default" else paths.vector / index_name
    generate_embeddings(
        source_dir=parsed_dir,
        method="parsed",
        out_path=(
            root / "rich_doc_embeddings.json"
            if index_name == "default"
            else vector_dir / "rich_doc_embeddings.json"
        ),
        model=model,
        segment_mode=semantic_chunking,
        chunk_dir=vector_dir / "chunks",
        paths=paths,
        reset_index=False,
        vector_name=index_name,
    )
    return vector_dir / "embedding_failures.json"
