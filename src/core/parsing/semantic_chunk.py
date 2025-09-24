from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
from sklearn.cluster import SpectralClustering

try:
    import hdbscan  # type: ignore[import]
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    hdbscan = None  # type: ignore[assignment]

try:
    import tiktoken  # type: ignore[import]
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    tiktoken = None  # type: ignore[assignment]

try:
    import umap  # type: ignore[import]
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    umap = None  # type: ignore[assignment]

from core.embeddings.embedder import embed_text, embed_text_batch
from core.logger import get_logger

logger = get_logger(__name__)


def _cluster_embeddings(
    embeddings: Sequence[Sequence[float]], method: str
) -> List[int]:
    """Cluster embeddings using UMAP + Spectral Clustering or HDBSCAN."""
    if umap is None:  # pragma: no cover - optional dependency
        raise ModuleNotFoundError(
            "umap-learn is required for semantic chunking but is not installed."
        )

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
            if hdbscan is None:  # pragma: no cover - optional dependency
                raise ModuleNotFoundError(
                    "hdbscan is required for fallback clustering but is not installed."
                )
            clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
            labels = clusterer.fit_predict(X_red)
    else:
        if hdbscan is None:  # pragma: no cover - optional dependency
            raise ModuleNotFoundError(
                "hdbscan is required for semantic chunking but is not installed."
            )
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
    if tiktoken is None:  # pragma: no cover - optional dependency
        raise ModuleNotFoundError(
            "tiktoken is required for semantic chunking but is not installed."
        )

    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text, disallowed_special=())
    logger.debug("Tokenized into %d tokens", len(tokens))

    window_texts: List[str] = []
    starts: List[int] = []
    for i in range(0, len(tokens), step_tokens):
        window = tokens[i : i + window_tokens]
        if not window:
            continue
        window_texts.append(enc.decode(window))
        starts.append(i)
    logger.debug("Created %d windows", len(window_texts))

    if not window_texts:
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

    window_vectors = embed_text_batch(window_texts, model=model, embedder=embed_text)
    labels = [int(label) for label in _cluster_embeddings(window_vectors, cluster_method)]

    segment_bounds: List[Tuple[int, int, int]] = []
    current_start = 0
    current_label = labels[0]
    for idx in range(1, len(starts)):
        if labels[idx] != current_label:
            segment_bounds.append((current_start, starts[idx], current_label))
            current_start = starts[idx]
            current_label = labels[idx]

    segment_bounds.append((current_start, len(tokens), current_label))

    segment_payload: List[Tuple[int, int, int, str]] = []
    for start, end, label in segment_bounds:
        seg_text = enc.decode(tokens[start:end])
        if not seg_text.strip():
            continue
        segment_payload.append((start, end, label, seg_text))

    if not segment_payload:
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

    segment_embeddings = embed_text_batch(
        [payload[3] for payload in segment_payload], model=model, embedder=embed_text
    )

    segments: List[Dict[str, Any]] = []
    for (start, end, label, seg_text), vector in zip(
        segment_payload, segment_embeddings
    ):
        segments.append(
            {
                "text": seg_text,
                "embedding": vector,
                "topic": f"topic_{label}",
                "start": start,
                "end": end,
                "cluster_id": int(label),
            }
        )

    logger.debug("Produced %d segments", len(segments))
    return segments


def semantic_chunk_text(*args, **kwargs) -> List[str]:
    """Compatibility wrapper returning only text chunks."""
    return [c["text"] for c in semantic_chunk(*args, **kwargs)]
