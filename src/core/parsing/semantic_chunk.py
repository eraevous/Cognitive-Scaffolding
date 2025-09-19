from typing import Any, Dict, List, Sequence

import hdbscan
import numpy as np
import tiktoken
import umap
from sklearn.cluster import SpectralClustering

from core.embeddings.embedder import embed_text
from core.logger import get_logger

logger = get_logger(__name__)


def _cluster_embeddings(
    embeddings: Sequence[Sequence[float]], method: str
) -> List[int]:
    """Cluster embeddings using UMAP + Spectral Clustering or HDBSCAN."""
    X = np.asarray(embeddings, dtype="float32")
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
    X_red = reducer.fit_transform(X)

    if method == "spectral":
        try:
            n_clusters = max(2, min(10, len(embeddings)))
            clusterer = SpectralClustering(
                n_clusters=n_clusters,
                affinity="nearest_neighbors",
                assign_labels="discretize",
                random_state=42,
            )
            labels = clusterer.fit_predict(X_red)
        except Exception:
            logger.exception("Spectral clustering failed; falling back to HDBSCAN")
            clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
            labels = clusterer.fit_predict(X_red)
    else:
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
        labels = clusterer.fit_predict(X_red)

    logger.debug("Cluster labels: %s", labels.tolist())
    return labels.tolist()


def semantic_chunk(
    text: str,
    model: str = "text-embedding-3-large",
    window_tokens: int = 256,
    step_tokens: int = 128,
    cluster_method: str = "spectral",
) -> List[Dict[str, Any]]:
    """Return semantic chunk objects with embeddings and metadata."""
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text, disallowed_special=())
    logger.debug("Tokenized into %d tokens", len(tokens))

    windows: List[List[float]] = []
    starts: List[int] = []
    for i in range(0, len(tokens), step_tokens):
        window = tokens[i : i + window_tokens]
        if not window:
            continue
        window_text = enc.decode(window)
        vec = embed_text(window_text, model=model)
        windows.append(vec)
        starts.append(i)
    logger.debug("Created %d windows", len(windows))

    if not windows:
        return [
            {
                "text": text,
                "embedding": embed_text(text, model=model),
                "topic": "topic_0",
                "start": 0,
                "end": len(tokens),
                "cluster_id": 0,
            }
        ]

    labels = _cluster_embeddings(windows, cluster_method)

    segments: List[Dict[str, Any]] = []
    current_start = 0
    current_label = labels[0]
    for idx in range(1, len(starts)):
        if labels[idx] != current_label:
            seg_text = enc.decode(tokens[current_start : starts[idx]])
            segments.append(
                {
                    "text": seg_text,
                    "embedding": embed_text(seg_text, model=model),
                    "topic": f"topic_{current_label}",
                    "start": current_start,
                    "end": starts[idx],
                    "cluster_id": int(current_label),
                }
            )
            current_start = starts[idx]
            current_label = labels[idx]

    seg_text = enc.decode(tokens[current_start : len(tokens)])
    segments.append(
        {
            "text": seg_text,
            "embedding": embed_text(seg_text, model=model),
            "topic": f"topic_{current_label}",
            "start": current_start,
            "end": len(tokens),
            "cluster_id": int(current_label),
        }
    )

    logger.debug("Produced %d segments", len(segments))
    return segments


def semantic_chunk_text(*args, **kwargs) -> List[str]:
    """Compatibility wrapper returning only text chunks."""
    return [c["text"] for c in semantic_chunk(*args, **kwargs)]
