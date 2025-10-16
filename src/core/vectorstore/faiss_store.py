"""Thin wrapper around a FAISS inner product index."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np

from core.utils.logger import get_logger

logger = get_logger(__name__)

try:  # pragma: no cover - optional dependency shimmed in tests
    import faiss  # type: ignore[import]
except Exception:  # pragma: no cover
    faiss = None  # type: ignore[assignment]


class FaissStore:
    """Manage a FAISS index stored on disk."""

    def __init__(self, directory: Path | str, dim: int) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.index_path = self.directory / "index.faiss"
        self.dim = dim
        self._dirty = False
        self.index = self._load_index()

    def _load_index(self):
        if faiss is None:  # pragma: no cover - used when dependency missing
            class _FallbackIndex:
                def __init__(self, dim: int) -> None:
                    self.dim = dim
                    self.vectors: list[Tuple[int, np.ndarray]] = []

                def add_with_ids(self, vecs: np.ndarray, ids: np.ndarray) -> None:
                    for vec, idx in zip(vecs, ids):
                        self.vectors.append((int(idx), vec.astype(np.float32)))

                def search(self, vec: np.ndarray, k: int):
                    scores = []
                    for idx, stored in self.vectors:
                        score = float(np.dot(vec, stored) / (np.linalg.norm(vec) * np.linalg.norm(stored) + 1e-9))
                        scores.append((idx, score))
                    scores.sort(key=lambda item: item[1], reverse=True)
                    hits = scores[:k]
                    if not hits:
                        return np.empty((1, 0)), np.empty((1, 0), dtype=np.int64)
                    distances = np.asarray([[score for _, score in hits]], dtype=np.float32)
                    ids = np.asarray([[idx for idx, _ in hits]], dtype=np.int64)
                    return distances, ids

            return _FallbackIndex(self.dim)

        if self.index_path.exists():
            index = faiss.read_index(str(self.index_path))
            if getattr(index, "d", self.dim) != self.dim:
                logger.warning(
                    "Existing index dimension %s differs from requested %s", index.d, self.dim
                )
            return faiss.IndexIDMap(index)
        base = faiss.IndexFlatIP(self.dim)
        return faiss.IndexIDMap(base)

    def add(self, ids: Iterable[int], vectors: np.ndarray) -> None:
        arr = np.asarray(vectors, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        id_array = np.fromiter((int(i) for i in ids), dtype=np.int64, count=arr.shape[0])
        if hasattr(self.index, "add_with_ids"):
            self.index.add_with_ids(arr, id_array)
        self._dirty = True

    def search(self, vector: Iterable[float], k: int = 5) -> List[Tuple[int, float]]:
        vec = np.asarray(list(vector), dtype=np.float32).reshape(1, -1)
        if hasattr(self.index, "search"):
            distances, ids = self.index.search(vec, k)
            if distances.size == 0:
                return []
            return [(int(idx), float(score)) for idx, score in zip(ids[0], distances[0])]
        return []

    def persist(self) -> None:
        if not self._dirty:
            return
        if faiss is None:
            return
        faiss.write_index(self.index, str(self.index_path))
        self._dirty = False


__all__ = ["FaissStore"]
