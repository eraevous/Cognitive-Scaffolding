"""Embedding helpers wrapping OpenAI models with local fallbacks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
try:  # pragma: no cover - optional dependency
    import tiktoken  # type: ignore[import]
except Exception:  # pragma: no cover
    class _DummyEncoding:
        def encode(self, text, disallowed_special=()):
            return [ord(ch) for ch in text]

        def decode(self, tokens):
            return ''.join(chr(int(t)) for t in tokens)

    class _DummyTiktoken:
        @staticmethod
        def encoding_for_model(_model):
            return _DummyEncoding()

    tiktoken = _DummyTiktoken()  # type: ignore[assignment]

from core.configuration import config_registry
from core.parsing import semantic_chunk
from core.utils import budget_tracker
from core.vectorstore.faiss_store import FaissStore

try:  # pragma: no cover - optional dependency in tests
    from openai import OpenAI
except Exception:  # pragma: no cover - fallback when package missing
    OpenAI = None  # type: ignore[misc]

MODEL_DIMS: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}
DEFAULT_MODEL = "text-embedding-3-small"
MAX_EMBED_TOKENS = 8192

_client: OpenAI | None = None  # type: ignore[assignment]


def _get_client() -> OpenAI | None:  # pragma: no cover - exercised in integration
    global _client
    if _client is None and OpenAI is not None:
        remote = config_registry.get_remote_config()
        api_key = remote.openai_api_key
        if api_key:
            _client = OpenAI(api_key=api_key)
        else:
            _client = OpenAI()
    return _client


def _tokenize(text: str, model: str) -> Sequence[int]:
    encoding = tiktoken.encoding_for_model(model)
    return encoding.encode(text, disallowed_special=())


def _deterministic_embedding(text: str, dim: int) -> list[float]:
    data = text.encode("utf-8")
    vec = np.zeros(dim, dtype=np.float32)
    for idx, byte in enumerate(data):
        vec[idx % dim] += byte / 255.0
    norm = np.linalg.norm(vec)
    if norm:
        vec /= norm
    return vec.astype(float).tolist()


def embed_text(text: str, model: str = DEFAULT_MODEL) -> list[float]:
    """Embed ``text`` returning a dense vector.

    When the OpenAI client is unavailable, a deterministic hashing fallback is
    used. This keeps local tests hermetic while still producing stable vectors.
    """

    dim = MODEL_DIMS.get(model, MODEL_DIMS[DEFAULT_MODEL])
    tokens = _tokenize(text, model)
    if len(tokens) > MAX_EMBED_TOKENS:
        window = tokens[:MAX_EMBED_TOKENS]
        text = tiktoken.encoding_for_model(model).decode(window)
    tracker = budget_tracker.get_budget_tracker()
    tracker.check(0.0001 * len(tokens) / 1000.0)

    client = _get_client()
    if client is None:
        return _deterministic_embedding(text, dim)

    response = client.embeddings.create(model=model, input=text)
    return list(response.data[0].embedding)


def embed_text_batch(texts: Iterable[str], model: str = DEFAULT_MODEL) -> list[list[float]]:
    return [embed_text(text, model=model) for text in texts]


def _stable_hash(identifier: str) -> int:
    digest = hashlib.sha1(identifier.encode("utf-8")).hexdigest()
    return int(digest[:16], 16) & ((1 << 63) - 1)


def _collect_source_files(source_dir: Path) -> list[Path]:
    return sorted(p for p in source_dir.iterdir() if p.is_file() and p.suffix in {".txt", ".md"})


def generate_embeddings(
    *,
    source_dir: Path | None = None,
    method: str = "parsed",
    out_path: Path | None = None,
    model: str = DEFAULT_MODEL,
    segment_mode: bool | None = None,
    paths=None,
) -> Path:
    """Generate embeddings for files under ``source_dir``.

    The function writes a ``rich_doc_embeddings.json`` payload and returns the
    output path for convenience.
    """

    if paths is None:
        paths = config_registry.get_path_config()
    if source_dir is None:
        source_dir = paths.parsed
    if out_path is None:
        out_path = Path(paths.root) / "rich_doc_embeddings.json"

    segment = segment_mode if segment_mode is not None else bool(paths.semantic_chunking)
    vector_dir = Path(paths.vector)
    vector_dir.mkdir(parents=True, exist_ok=True)
    id_map_path = vector_dir / "id_map.json"

    embeddings: dict[str, dict[str, object]] = {}
    id_map: dict[str, str] = {}
    faiss_store = FaissStore(vector_dir, dim=MODEL_DIMS.get(model, MODEL_DIMS[DEFAULT_MODEL]))

    for path in _collect_source_files(Path(source_dir)):
        text = path.read_text(encoding="utf-8")
        if segment:
            chunk_dir = vector_dir / "chunks"
            chunk_dir.mkdir(parents=True, exist_ok=True)
            chunks = semantic_chunk.semantic_chunk(text, model=model)
            for idx, chunk in enumerate(chunks):
                chunk_id = f"{path.stem}_chunk{idx:02d}"
                chunk_path = chunk_dir / f"{chunk_id}.json"
                chunk_payload = dict(chunk)
                if "embedding" not in chunk_payload or not chunk_payload["embedding"]:
                    chunk_payload["embedding"] = embed_text(chunk_payload["text"], model=model)
                chunk_path.write_text(json.dumps(chunk_payload, indent=2), encoding="utf-8")
                identifier = chunk_id
                embeddings[identifier] = {
                    "embedding": chunk_payload["embedding"],
                    "source": path.name,
                    "method": method,
                }
                hashed = _stable_hash(identifier)
                id_map[str(hashed)] = identifier
                faiss_store.add([hashed], np.asarray([chunk_payload["embedding"]], dtype=np.float32))
        else:
            identifier = path.stem
            vector = embed_text(text, model=model)
            embeddings[identifier] = {
                "embedding": vector,
                "source": path.name,
                "method": method,
            }
            hashed = _stable_hash(identifier)
            id_map[str(hashed)] = identifier
            faiss_store.add([hashed], np.asarray([vector], dtype=np.float32))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(embeddings, indent=2), encoding="utf-8")
    id_map_path.write_text(json.dumps(id_map, indent=2), encoding="utf-8")
    faiss_store.persist()
    return out_path


def get_path_config(force_reload: bool = False):
    return config_registry.get_path_config(force_reload=force_reload)


__all__ = [
    "MODEL_DIMS",
    "DEFAULT_MODEL",
    "MAX_EMBED_TOKENS",
    "embed_text",
    "embed_text_batch",
    "generate_embeddings",
    "get_path_config",
]
