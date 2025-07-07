from pathlib import Path
from typing import Iterable, List, Tuple
import hashlib

from core.utils.logger import get_logger

import faiss
import numpy as np


class FaissStore:
    """Lightweight wrapper around a FAISS index with ID mapping."""

    def __init__(self, dim: int, path: Path):
        self.dim = dim
        self.path = path
        self.logger = get_logger(__name__)
        self.index = faiss.IndexIDMap(faiss.IndexFlatIP(dim))
        if path.exists():
            self._load()
            if self.index.d != dim:
                self.logger.warning(
                    "Index dimension %d differs from requested %d; using stored dimension",
                    self.index.d,
                    dim,
                )

    def _hash_id(self, identifier: str) -> int:
        return int.from_bytes(
            hashlib.blake2b(identifier.encode("utf-8"), digest_size=8).digest(),
            "big",
        )

    def add(self, ids: Iterable[int | str], vecs: np.ndarray) -> List[int]:
        vecs = np.asarray(vecs, dtype="float32")
        hashed = [self._hash_id(i) if isinstance(i, str) else int(i) for i in ids]
        ids_array = np.asarray(hashed, dtype="int64")
        self.index.add_with_ids(vecs, ids_array)
        return hashed

    def search(self, vec: np.ndarray, k: int = 5) -> List[Tuple[int, float]]:
        vec = np.asarray(vec, dtype="float32").reshape(1, -1)
        D, I = self.index.search(vec, k)
        return [(int(i), float(d)) for i, d in zip(I[0], D[0]) if i != -1]

    def persist(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.path))

    def _load(self) -> None:
        self.index = faiss.read_index(str(self.path))
