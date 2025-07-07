from typing import List, Tuple
import json

import numpy as np

from core.embeddings.embedder import MODEL_DIMS, get_model_for_dim, embed_text
from core.config.config_registry import get_path_config
from core.vectorstore.faiss_store import FaissStore
from core.utils.logger import get_logger


class Retriever:
    """Embed queries and return top-k document IDs from the FAISS index."""

    def __init__(self, store: FaissStore | None = None, model: str | None = None):
        self.logger = get_logger(__name__)
        paths = get_path_config()
        default_model = model or "text-embedding-3-small"
        dim = MODEL_DIMS.get(default_model, 1536)
        self.store = store or FaissStore(dim=dim, path=paths.vector / "mosaic.index")
        self.dim = self.store.index.d
        id_map_path = paths.vector / "id_map.json"
        if id_map_path.exists():
            self.id_map = {int(k): v for k, v in json.loads(id_map_path.read_text()).items()}
        else:
            self.id_map = {}
        if model is None and self.dim != dim:
            inferred = get_model_for_dim(self.dim)
            self.logger.info(
                "Detected index dimension %d; switching to model %s", self.dim, inferred
            )
            self.model = inferred
        else:
            self.model = default_model

    def query(self, text: str, k: int = 5) -> List[Tuple[str, float]]:
        vec = np.asarray(embed_text(text, model=self.model), dtype="float32")
        results = self.store.search(vec, k)
        return [(self.id_map.get(doc_id, str(doc_id)), score) for doc_id, score in results]
