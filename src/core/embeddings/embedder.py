# core/embeddings/embedder.py
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Callable, Dict, List, Literal, Sequence

import numpy as np
import tiktoken
from openai import OpenAI

from core.configuration.config_registry import get_path_config, get_remote_config
from core.logger import get_logger
from core.utils.budget_tracker import get_budget_tracker
from core.vectorstore.faiss_store import FaissStore

MAX_EMBED_TOKENS = 8191
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
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding

    # chunk into MAX_EMBED_TOKENS slices and average embeddings
    vectors = []
    for i in range(0, len(tokens), MAX_EMBED_TOKENS):
        chunk_tokens = tokens[i : i + MAX_EMBED_TOKENS]
        _charge_budget(len(chunk_tokens), model, tracker)
        chunk_text = enc.decode(chunk_tokens)
        resp = client.embeddings.create(input=[chunk_text], model=model)
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
            total_tokens = sum(short_tokens)
            _charge_budget(total_tokens, model, tracker)
            response = embeddings_api(input=short_payload, model=model)
            for idx, data in zip(short_indices, response.data):
                results[idx] = data.embedding

    return [results[i] for i in range(len(texts))]


def generate_embeddings(
    source_dir: Path = None,
    method: Literal["parsed", "summary", "raw", "meta"] = "parsed",
    out_path: Path = Path("rich_doc_embeddings.json"),
    model: str = "text-embedding-3-large",
    segment_mode: bool | None = None,
    chunk_dir: Path | None = None,
) -> None:
    """Generate embeddings for documents or topic segments.

    When ``segment_mode`` is ``True``, each document is split via
    ``topic_segmenter`` and every chunk is embedded separately. Resulting
    vectors are stored in the FAISS index with IDs in the form
    ``"docID_chunkXX"`` and optionally written to ``chunk_dir``.
    """
    paths = get_path_config()
    segment_mode = paths.semantic_chunking if segment_mode is None else segment_mode
    source_dir = source_dir or paths.parsed
    out_path = out_path or paths.vector / "rich_doc_embeddings.json"
    embeddings: Dict[str, List[float]] = {}
    id_map = {}
    index_dim = MODEL_DIMS.get(model, 1536)
    index_path = paths.vector / "mosaic.index"
    if index_path.exists():
        logger.info("Reinitializing FAISS index at %s", index_path)
        index_path.unlink()
    store = FaissStore(dim=index_dim, path=index_path)

    chunk_dir = chunk_dir or (paths.vector / "chunks")

    pattern = "*.meta.json" if method in {"summary", "meta"} else "*.txt"
    for file in sorted(source_dir.glob(pattern)):
        doc_id = file.stem

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

                segments = [
                    {"text": t, "embedding": embed_text(t, model=model)}
                    for t in chunk_text(text)
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
        except Exception:
            logger.exception("Failed embedding %s", file.name)

    out_path.write_text(json.dumps(embeddings, indent=2))
    store.persist()
    id_map_path = paths.vector / "id_map.json"
    id_map_path.write_text(json.dumps(id_map, indent=2))
    logger.info("Saved %d embeddings to %s", len(embeddings), out_path)
