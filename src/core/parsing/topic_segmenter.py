"""
Module: core.parsing.topic_segmenter
- @ai-path: core.parsing.topic_segmenter
- @ai-source-file: topic_segmenter.py
- @ai-role: parser
- @ai-intent: "Detect topic boundaries using UMAP + HDBSCAN over window embeddings."
"""

from typing import Any, Dict, List, Optional

import hdbscan
import numpy as np
import tiktoken
import umap

from .semantic_chunk import semantic_chunk_text
from core.embeddings.embedder import embed_text
from core.utils.logger import get_logger
from .chunk_text import chunk_text

logger = get_logger(__name__)

def topic_segmenter(text: str, model: str = "text-embedding-3-small") -> List[str]:
    """Segment text by topic using semantic chunking with a fallback."""
    chunks = semantic_chunk_text(text, model=model)
    if len(chunks) <= 1:
        return chunk_text(text)
    return chunks

def segment_text(text: str) -> List[str]:
    """Return semantic segments of ``text`` using :func:`semantic_chunk_text`."""
    return semantic_chunk_text(text)

def segment_topics(
    text: str,
    window_tokens: int = 200,
    step_tokens: int = 100,
    cluster_method: str = "hdbscan",
    model: str = "text-embedding-3-small",
    umap_config: Optional[Dict[str, Any]] = None,
    hdbscan_config: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Return topic segments with start/end token indices and cluster IDs."""
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text, disallowed_special=())

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

    if not windows:
        logger.warning("No windows produced for segmentation")
        return [
            {
                "text": text,
                "start": 0,
                "end": len(tokens),
                "cluster_id": 0,
            }
        ]

    logger.info("Embedded %d windows", len(windows))

    X = np.asarray(windows, dtype="float32")
    reducer = umap.UMAP(
        **(
            umap_config
            or {"n_neighbors": 15, "min_dist": 0.1, "random_state": 42}
        )
    )
    X_red = reducer.fit_transform(X)

    if cluster_method != "hdbscan":
        logger.warning("Unsupported cluster_method %s; using hdbscan", cluster_method)

    clusterer = hdbscan.HDBSCAN(
        **(hdbscan_config or {"min_cluster_size": 2})
    )
    labels = clusterer.fit_predict(X_red)

    logger.info(
        "HDBSCAN found %d clusters", len(set(labels)) - (1 if -1 in labels else 0)
    )

    segments: List[Dict[str, Any]] = []
    current_start = 0
    current_label = int(labels[0])
    for idx in range(1, len(starts)):
        if int(labels[idx]) != current_label:
            segments.append(
                {
                    "text": enc.decode(tokens[current_start : starts[idx]]),
                    "start": current_start,
                    "end": starts[idx],
                    "cluster_id": current_label,
                }
            )
            current_start = starts[idx]
            current_label = int(labels[idx])

    segments.append(
        {
            "text": enc.decode(tokens[current_start: len(tokens)]),
            "start": current_start,
            "end": len(tokens),
            "cluster_id": current_label,
        }
    )

    return segments