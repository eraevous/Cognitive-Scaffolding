from typing import List, Tuple

import numpy as np

from core.embeddings.embedder import embed_text
from core.config.config_registry import get_path_config
from core.vectorstore.faiss_store import FaissStore


class Retriever:
    """Embed queries and return top-k document IDs from the FAISS index."""

    def __init__(self, store: FaissStore | None = None, dim: int = 1536):
        paths = get_path_config()
        # Use the dedicated vector path to locate the persistent FAISS index
        self.store = store or FaissStore(dim=dim, path=paths.vector / "mosaic.index")

    def query(self, text: str, k: int = 5) -> List[Tuple[int, float]]:
        vec = np.asarray(embed_text(text), dtype="float32")
        return self.store.search(vec, k)
