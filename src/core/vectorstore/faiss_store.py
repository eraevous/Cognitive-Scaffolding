from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np


class FaissStore:
    """Lightweight wrapper around a FAISS index with ID mapping."""

    def __init__(self, dim: int, path: Path):
        self.dim = dim
        self.path = path
        self.index = faiss.IndexIDMap(faiss.IndexFlatIP(dim))
        if path.exists():
            self._load()

    def add(self, ids: List[int], vecs: np.ndarray) -> None:
        vecs = np.asarray(vecs, dtype="float32")
        ids = np.asarray(ids, dtype="int64")
        self.index.add_with_ids(vecs, ids)

    def search(self, vec: np.ndarray, k: int = 5) -> List[Tuple[int, float]]:
        vec = np.asarray(vec, dtype="float32").reshape(1, -1)
        D, I = self.index.search(vec, k)
        return [(int(i), float(d)) for i, d in zip(I[0], D[0]) if i != -1]

    def persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.path))

    def _load(self) -> None:
        self.index = faiss.read_index(str(self.path))
