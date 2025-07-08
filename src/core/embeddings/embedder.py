# core/embeddings/embedder.py
import json
from pathlib import Path
from typing import Dict, List, Literal
import hashlib

from openai import OpenAI
import numpy as np
import tiktoken

from core.utils.budget_tracker import get_budget_tracker

from core.config.config_registry import get_path_config, get_remote_config
from core.vectorstore.faiss_store import FaissStore
from core.utils.logger import get_logger


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


def embed_text(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Return an embedding for ``text``. Handles long inputs by chunking."""
    remote = get_remote_config()
    client = OpenAI(api_key=remote.openai_api_key)
    tracker = get_budget_tracker()

    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text, disallowed_special=())

    if len(tokens) <= MAX_EMBED_TOKENS:
        if tracker:
            est_cost = len(tokens) / 1000 * EMBED_COST_PER_1K.get(model, 0)
            if not tracker.check(est_cost):
                raise RuntimeError("Budget exceeded for embedding request")
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding

    # chunk into MAX_EMBED_TOKENS slices and average embeddings
    vectors = []
    for i in range(0, len(tokens), MAX_EMBED_TOKENS):
        chunk_tokens = tokens[i : i + MAX_EMBED_TOKENS]
        if tracker:
            est_cost = len(chunk_tokens) / 1000 * EMBED_COST_PER_1K.get(model, 0)
            if not tracker.check(est_cost):
                raise RuntimeError("Budget exceeded for embedding request")
        chunk_text = enc.decode(chunk_tokens)
        resp = client.embeddings.create(input=[chunk_text], model=model)
        vectors.append(np.asarray(resp.data[0].embedding, dtype="float32"))

    return np.mean(vectors, axis=0).tolist()


def generate_embeddings(
    source_dir: Path = None,
    method: Literal["parsed", "summary", "raw", "meta"] = "parsed",
    out_path: Path = Path("rich_doc_embeddings.json"),
    model: str = "text-embedding-3-large",
    segment_mode: bool = False,
    chunk_dir: Path | None = None,
) -> None:
    """Generate embeddings for documents or topic segments.

    When ``segment_mode`` is ``True``, each document is split via
    ``topic_segmenter`` and every chunk is embedded separately. Resulting
    vectors are stored in the FAISS index with IDs in the form
    ``"docID_chunkXX"`` and optionally written to ``chunk_dir``.
    """
    paths = get_path_config()
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
    if segment_mode:
        chunk_dir.mkdir(parents=True, exist_ok=True)

    for file in sorted(source_dir.glob("*.txt" if method != "meta" else "*.meta.json")):
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
                from core.parsing.topic_segmenter import topic_segmenter
                segments = topic_segmenter(text, model=model)
                for idx, chunk in enumerate(segments):
                    seg_id = f"{doc_id}_chunk{idx:02d}"
                    vector = embed_text(chunk, model=model)
                    embeddings[seg_id] = vector
                    hashed = store.add([seg_id], [vector])[0]
                    id_map[str(hashed)] = seg_id
                    (chunk_dir / f"{seg_id}.txt").write_text(chunk, encoding="utf-8")
            else:
                vector = embed_text(text, model=model)
                embeddings[doc_id] = vector
                hashed_id = int.from_bytes(
                    hashlib.blake2b(doc_id.encode("utf-8"), digest_size=8).digest(),
                    "big",
                ) & 0x7FFF_FFFF_FFFF_FFFF  # truncate to 63 bits for FAISS
                store.add([hashed_id], [vector])
                id_map[str(hashed_id)] = doc_id
        except Exception:
            logger.exception("Failed embedding %s", file.name)

    out_path.write_text(json.dumps(embeddings, indent=2))
    store.persist()
    id_map_path = paths.vector / "id_map.json"
    id_map_path.write_text(json.dumps(id_map, indent=2))
    logger.info("Saved %d embeddings to %s", len(embeddings), out_path)
