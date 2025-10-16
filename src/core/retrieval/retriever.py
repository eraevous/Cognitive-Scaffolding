"""Semantic retrieval over the FAISS vector store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import numpy as np

from core.configuration import config_registry
from core.embeddings import embedder

embed_text = embedder.embed_text
from core.logger import get_logger
from core.vectorstore.faiss_store import FaissStore

logger = get_logger(__name__)


def _load_id_map(path: Path) -> dict[int, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {int(key): value for key, value in data.items()}


def _load_chunk_text(chunk_dir: Path | None, identifier: str) -> str:
    if chunk_dir is None:
        return ""
    text_path = chunk_dir / f"{identifier}.txt"
    if text_path.exists():
        return text_path.read_text(encoding="utf-8")
    json_path = chunk_dir / f"{identifier}.json"
    if json_path.exists():
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        return str(payload.get("text", ""))
    return ""


def _doc_from_identifier(identifier: str) -> str:
    return identifier.split("_chunk", 1)[0]


class Retriever:
    """Convenience wrapper around :class:`FaissStore`."""

    def __init__(
        self,
        store: FaissStore | None = None,
        model: str | None = None,
        chunk_dir: Path | None = None,
    ) -> None:
        paths = config_registry.get_path_config()
        vector_dir = Path(paths.vector)
        dim = embedder.MODEL_DIMS.get(model or embedder.DEFAULT_MODEL, embedder.MODEL_DIMS[embedder.DEFAULT_MODEL])
        self.store = store or FaissStore(vector_dir, dim=dim)
        self.model = model or embedder.DEFAULT_MODEL
        self.chunk_dir = Path(chunk_dir) if chunk_dir is not None else vector_dir / "chunks"
        self.id_map = _load_id_map(vector_dir / "id_map.json")

    def _rank(self, vector: Sequence[float], k: int) -> List[Tuple[str, float]]:
        np_vector = np.asarray(vector, dtype=np.float32).reshape(1, -1)
        hits = self.store.search(np_vector, k=k)
        ranked: List[Tuple[str, float]] = []
        for idx, score in hits:
            identifier = self.id_map.get(int(idx))
            if identifier is None:
                continue
            ranked.append((identifier, float(score)))
        return ranked

    def query(
        self,
        text: str,
        k: int = 5,
        *,
        return_text: bool = False,
    ) -> List[Tuple[str, float] | Tuple[str, float, str]]:
        vector = embed_text(text, model=self.model)
        ranked = self._rank(vector, k)
        if not return_text:
            return ranked
        enriched = []
        for identifier, score in ranked:
            enriched.append(
                (identifier, score, _load_chunk_text(self.chunk_dir, identifier))
            )
        return enriched

    def query_file(
        self,
        path: Path,
        k: int = 5,
        *,
        return_text: bool = False,
    ) -> List[Tuple[str, float] | Tuple[str, float, str]]:
        text = Path(path).read_text(encoding="utf-8")
        return self.query(text, k=k, return_text=return_text)

    def query_multi(
        self,
        texts: Iterable[str],
        k: int = 5,
        *,
        return_text: bool = False,
        aggregate: bool = False,
    ) -> List[Tuple[str, float] | Tuple[str, float, str]]:
        results: list[Tuple[str, float, str]] = []
        for text in texts:
            for identifier, score, chunk_text in self.query(text, k=k, return_text=True):
                results.append((identifier, score, chunk_text))

        if not aggregate:
            if return_text:
                return results
            return [(identifier, score) for identifier, score, _ in results]

        aggregated: dict[str, Tuple[float, list[str]]] = {}
        for identifier, score, chunk_text in results:
            doc_id = _doc_from_identifier(identifier)
            total, texts_acc = aggregated.setdefault(doc_id, (0.0, []))
            total += score
            if chunk_text:
                texts_acc.append(chunk_text)
            aggregated[doc_id] = (total, texts_acc)

        ranked = sorted(aggregated.items(), key=lambda item: item[1][0], reverse=True)
        if return_text:
            return [
                (doc_id, score_texts[0], "\n".join(score_texts[1]))
                for doc_id, score_texts in ranked
            ]
        return [(doc_id, score_texts[0]) for doc_id, score_texts in ranked]


__all__ = ["Retriever"]
