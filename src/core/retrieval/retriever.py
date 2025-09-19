import json
from pathlib import Path
from typing import Iterable, List, Tuple, cast

import numpy as np

from core.config.config_registry import get_path_config
from core.embeddings.embedder import MODEL_DIMS, embed_text, get_model_for_dim
from core.utils.logger import get_logger
from core.vectorstore.faiss_store import FaissStore


class Retriever:
    """Embed queries and return ranked document IDs from the FAISS index.

    Supports multi-query search, ranking across results, and optional
    cross-document text aggregation.
    """

    def __init__(
        self,
        store: FaissStore | None = None,
        model: str | None = None,
        chunk_dir: Path | None = None,
    ):
        self.logger = get_logger(__name__)
        paths = get_path_config()
        default_model = model or "text-embedding-3-small"
        dim = MODEL_DIMS.get(default_model, 1536)
        self.store = store or FaissStore(dim=dim, path=paths.vector / "mosaic.index")
        self.dim = self.store.index.d
        id_map_path = paths.vector / "id_map.json"
        if id_map_path.exists():
            self.id_map = {
                int(k): v for k, v in json.loads(id_map_path.read_text()).items()
            }
        else:
            self.id_map = {}
        self.chunk_dir = chunk_dir or (
            paths.vector / "chunks" if (paths.vector / "chunks").exists() else None
        )
        if model is None and self.dim != dim:
            inferred = get_model_for_dim(self.dim)
            self.logger.info(
                "Detected index dimension %d; switching to model %s", self.dim, inferred
            )
            self.model = inferred
        else:
            self.model = default_model

    def query(self, text: str, k: int = 5, return_text: bool = False):
        """Return top ``k`` results for a single query string."""
        return self.query_multi([text], k=k, return_text=return_text)

    def query_file(self, file: str | Path, k: int = 5, return_text: bool = False):
        """Return top ``k`` results using the contents of ``file`` as the query."""
        text = Path(file).read_text("utf-8")
        return self.query(text, k=k, return_text=return_text)

    def query_multi(
        self,
        texts: Iterable[str],
        k: int = 5,
        return_text: bool = False,
        aggregate: bool = False,
    ) -> List[Tuple[str, float] | Tuple[str, float, str]]:
        """Return ranked results for multiple query strings.

        Parameters
        ----------
        texts : Iterable[str]
            Query strings to embed and search.
        k : int, optional
            Maximum number of results to return.
        return_text : bool, optional
            Include chunk text when available.
        aggregate : bool, optional
            Combine chunks belonging to the same document.
        """

        vectors = [
            np.asarray(embed_text(t, model=self.model), dtype="float32") for t in texts
        ]

        score_map: dict[str, List[float]] = {}
        for vec in vectors:
            for doc_id, score in self.store.search(vec, k):
                name = self.id_map.get(doc_id, str(doc_id))
                score_map.setdefault(name, []).append(score)

        ranked_all: List[Tuple[str, float]] = sorted(
            ((name, float(np.mean(scores))) for name, scores in score_map.items()),
            key=lambda x: x[1],
            reverse=True,
        )

        if aggregate:
            doc_groups: dict[str, dict[str, List]] = {}
            for name, score in ranked_all:
                root = name.split("_chunk")[0]
                entry = doc_groups.setdefault(root, {"scores": [], "chunks": []})
                scores_list: List = entry["scores"]
                chunks_list: List = entry["chunks"]
                scores_list.append(score)
                chunks_list.append(name)

            aggregated: List[Tuple[str, float] | Tuple[str, float, str]] = []
            for root, info in doc_groups.items():
                avg_score = float(np.mean(info["scores"]))
                if return_text and self.chunk_dir is not None:
                    texts_combined = []
                    for chunk_name in info["chunks"]:
                        chunk_path = self.chunk_dir / f"{chunk_name}.txt"
                        text_val = (
                            chunk_path.read_text("utf-8") if chunk_path.exists() else ""
                        )
                        texts_combined.append(text_val)
                    aggregated.append((root, avg_score, "\n".join(texts_combined)))
                else:
                    aggregated.append((root, avg_score))
            return cast(
                List[Tuple[str, float] | Tuple[str, float, str]],
                sorted(aggregated, key=lambda x: x[1], reverse=True)[:k],
            )

        ranked = ranked_all[:k]

        if return_text and self.chunk_dir is not None:
            enriched: List[Tuple[str, float, str]] = []
            for name, score in ranked:
                chunk_path = self.chunk_dir / f"{name}.txt"
                text_val = chunk_path.read_text("utf-8") if chunk_path.exists() else ""
                enriched.append((name, score, text_val))
            return cast(List[Tuple[str, float] | Tuple[str, float, str]], enriched)

        return cast(List[Tuple[str, float] | Tuple[str, float, str]], ranked)
