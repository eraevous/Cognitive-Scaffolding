# core/embeddings/embedder.py
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Sequence

import numpy as np
import tiktoken
from openai import OpenAI

from core.configuration.config_registry import get_path_config, get_remote_config
from core.logger import get_logger
from core.utils.budget_tracker import get_budget_tracker
from core.vectorstore.faiss_store import FaissStore
from core.utils.openai_retry import retry_with_exponential_backoff

MAX_EMBED_TOKENS = 8191
MAX_EMBED_BATCH_TOKENS = 100_000
MAX_EMBED_BATCH_ITEMS = 512
MODEL_DIMS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}
MODEL_BY_DIM = {v: k for k, v in MODEL_DIMS.items()}
EMBED_COST_PER_1K = {
    "text-embedding-3-small": 0.00002,
    "text-embedding-3-large": 0.00013,
}


def get_model_for_dim(dim: int) -> str:
    """Return embedding model name corresponding to FAISS index dimension."""
    return MODEL_BY_DIM.get(dim, "text-embedding-3-small")


logger = get_logger(__name__)


_client: OpenAI | None = None
_encodings: Dict[str, tiktoken.Encoding] = {}


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        remote = get_remote_config()
        _client = OpenAI(api_key=remote.openai_api_key)
    return _client


def _get_encoding(model: str) -> tiktoken.Encoding:
    if model not in _encodings:
        _encodings[model] = tiktoken.encoding_for_model(model)
    return _encodings[model]


def _charge_budget(token_count: int, model: str, tracker) -> None:
    if not tracker or token_count <= 0:
        return
    est_cost = token_count / 1000 * EMBED_COST_PER_1K.get(model, 0)
    if not tracker.check(est_cost):
        raise RuntimeError("Budget exceeded for embedding request")


def embed_text(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Return an embedding for ``text``. Handles long inputs by chunking."""
    client = _get_client()
    tracker = get_budget_tracker()

    enc = _get_encoding(model)
    tokens = enc.encode(text, disallowed_special=())

    if len(tokens) <= MAX_EMBED_TOKENS:
        _charge_budget(len(tokens), model, tracker)
        response = retry_with_exponential_backoff(
            lambda: client.embeddings.create(input=[text], model=model),
            logger=logger,
        )
        return response.data[0].embedding

    # chunk into MAX_EMBED_TOKENS slices and average embeddings
    vectors = []
    for i in range(0, len(tokens), MAX_EMBED_TOKENS):
        chunk_tokens = tokens[i : i + MAX_EMBED_TOKENS]
        _charge_budget(len(chunk_tokens), model, tracker)
        chunk_text = enc.decode(chunk_tokens)
        resp = retry_with_exponential_backoff(
            lambda: client.embeddings.create(input=[chunk_text], model=model),
            logger=logger,
        )
        vectors.append(np.asarray(resp.data[0].embedding, dtype="float32"))

    return np.mean(vectors, axis=0).tolist()


def embed_text_batch(
    texts: Sequence[str],
    model: str = "text-embedding-3-small",
    *,
    embedder: Callable[[str, str], List[float]] | None = None,
) -> List[List[float]]:
    """Embed multiple texts in as few API calls as possible."""

    if not texts:
        return []

    tracker = get_budget_tracker()
    enc = _get_encoding(model)
    embed_fn = embedder or embed_text

    results: Dict[int, List[float]] = {}
    short_payload: List[str] = []
    short_indices: List[int] = []
    short_tokens: List[int] = []

    for idx, text in enumerate(texts):
        token_ids = enc.encode(text, disallowed_special=())
        if len(token_ids) <= MAX_EMBED_TOKENS:
            short_payload.append(text)
            short_indices.append(idx)
            short_tokens.append(len(token_ids))
        else:
            results[idx] = embed_fn(text, model=model)

    if short_payload:
        client = _get_client()
        embeddings_api = getattr(getattr(client, "embeddings", None), "create", None)
        if embeddings_api is None:
            for idx, text in zip(short_indices, short_payload):
                results[idx] = embed_fn(text, model=model)
        else:
            batch_payload: List[str] = []
            batch_indices: List[int] = []
            batch_tokens = 0

            def flush_batch() -> None:
                nonlocal batch_payload, batch_indices, batch_tokens
                if not batch_payload:
                    return
                _charge_budget(batch_tokens, model, tracker)
                response = retry_with_exponential_backoff(
                    lambda: embeddings_api(input=batch_payload, model=model),
                    logger=logger,
                )
                for idx, data in zip(batch_indices, response.data):
                    results[idx] = data.embedding
                batch_payload = []
                batch_indices = []
                batch_tokens = 0

            for idx, text, token_count in zip(
                short_indices, short_payload, short_tokens
            ):
                would_exceed_tokens = (
                    batch_tokens + token_count > MAX_EMBED_BATCH_TOKENS
                )
                would_exceed_items = len(batch_payload) >= MAX_EMBED_BATCH_ITEMS
                if batch_payload and (would_exceed_tokens or would_exceed_items):
                    flush_batch()
                batch_payload.append(text)
                batch_indices.append(idx)
                batch_tokens += token_count

            flush_batch()

    return [results[i] for i in range(len(texts))]


def generate_embeddings(
    source_dir: Path = None,
    method: Literal["parsed", "summary", "raw", "meta"] = "parsed",
    out_path: Path = Path("rich_doc_embeddings.json"),
    model: str = "text-embedding-3-large",
    segment_mode: bool | None = None,
    chunk_dir: Path | None = None,
    paths=None,
    reset_index: bool = True,
) -> None:
    """Generate embeddings for documents or topic segments.

    When ``segment_mode`` is ``True``, each document is split via
    ``topic_segmenter`` and every chunk is embedded separately. Resulting
    vectors are stored in the FAISS index with IDs in the form
    ``"docID_chunkXX"`` and optionally written to ``chunk_dir``.
    """
    paths = paths or get_path_config()
    segment_mode = paths.semantic_chunking if segment_mode is None else segment_mode
    source_dir = source_dir or paths.parsed
    out_path = out_path or paths.vector / "rich_doc_embeddings.json"
    embeddings: Dict[str, List[float]] = {}
    id_map: Dict[str, str] = {}
    failures: List[Dict[str, Any]] = []
    index_dim = MODEL_DIMS.get(model, 1536)
    index_path = paths.vector / "mosaic.index"
    id_map_path = paths.vector / "id_map.json"
    if index_path.exists() and reset_index:
        logger.info("Reinitializing FAISS index at %s", index_path)
        index_path.unlink()
    if not reset_index:
        if out_path.exists():
            try:
                embeddings = json.loads(out_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                embeddings = {}
        if id_map_path.exists():
            try:
                id_map = json.loads(id_map_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                id_map = {}
    store = FaissStore(dim=index_dim, path=index_path)

    chunk_dir = chunk_dir or (paths.vector / "chunks")

    pattern = "*.meta.json" if method in {"summary", "meta"} else "*.txt"
    for file in sorted(source_dir.glob(pattern)):
        doc_id = file.stem
        if not reset_index and (
            doc_id in embeddings
            or any(key.startswith(f"{doc_id}_chunk") for key in embeddings)
        ):
            logger.info("Skipping already embedded file: %s", file.name)
            continue

        if method == "parsed":
            text = file.read_text(encoding="utf-8")
        elif method == "raw":
            raw_path = paths.raw / file.name
            text = raw_path.read_text(encoding="utf-8") if raw_path.exists() else ""
        elif method == "summary" or method == "meta":
            try:
                meta = json.loads(file.read_text("utf-8"))
                text = meta.get("summary", "")
            except Exception:
                continue
        else:
            raise ValueError(f"Unsupported method: {method}")

        if not text.strip():
            logger.warning("Skipping empty file: %s", file.name)
            continue

        try:
            if segment_mode:
                from core.parsing.semantic_chunk import semantic_chunk

                segments = semantic_chunk(text, model=model)
            else:
                from core.parsing.chunk_text import chunk_text

                chunk_texts = chunk_text(text)
                vectors = embed_text_batch(chunk_texts, model=model)
                segments = [
                    {"text": chunk_text, "embedding": vector}
                    for chunk_text, vector in zip(chunk_texts, vectors)
                ]

            if len(segments) == 1 and not segment_mode:
                vector = segments[0]["embedding"]
                embeddings[doc_id] = vector
                hashed_id = (
                    int.from_bytes(
                        hashlib.blake2b(doc_id.encode("utf-8"), digest_size=8).digest(),
                        "big",
                    )
                    & 0x7FFF_FFFF_FFFF_FFFF
                )
                store.add([hashed_id], [vector])
                id_map[str(hashed_id)] = doc_id
                chunk_dir.mkdir(parents=True, exist_ok=True)
                (chunk_dir / f"{doc_id}.txt").write_text(text, encoding="utf-8")
            else:
                chunk_dir.mkdir(parents=True, exist_ok=True)
                for idx, chunk in enumerate(segments):
                    seg_id = f"{doc_id}_chunk{idx:02d}"
                    vector = chunk["embedding"]
                    embeddings[seg_id] = vector
                    hashed = store._hash_id(seg_id) & 0x7FFF_FFFF_FFFF_FFFF
                    store.add([hashed], [vector])
                    id_map[str(hashed)] = seg_id
                    (chunk_dir / f"{seg_id}.json").write_text(
                        json.dumps(chunk, indent=2), encoding="utf-8"
                    )
                    (chunk_dir / f"{seg_id}.txt").write_text(
                        chunk.get("text", ""), encoding="utf-8"
                    )
        except Exception as exc:
            logger.exception("Failed embedding %s", file.name)
            failures.append(
                {
                    "file": str(file),
                    "doc_id": doc_id,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )

    out_path.write_text(json.dumps(embeddings, indent=2))
    store.persist()
    id_map_path.write_text(json.dumps(id_map, indent=2))
    failure_path = paths.vector / "embedding_failures.json"
    if failures:
        failure_path.write_text(json.dumps(failures, indent=2), encoding="utf-8")
        logger.warning("Saved %d embedding failure(s) to %s", len(failures), failure_path)
    elif failure_path.exists():
        failure_path.unlink()
    logger.info("Saved %d embeddings to %s", len(embeddings), out_path)
