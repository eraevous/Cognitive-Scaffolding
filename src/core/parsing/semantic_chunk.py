from typing import List

import numpy as np
from sklearn.cluster import KMeans
import tiktoken

from core.embeddings.embedder import embed_text
from core.utils.logger import get_logger

logger = get_logger(__name__)


def semantic_chunk_text(
    text: str,
    model: str = "text-embedding-3-small",
    window_tokens: int = 200,
    step_tokens: int = 100,
    n_clusters: int = 5,
) -> List[str]:
    """Segment ``text`` using window embeddings and KMeans clustering."""
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text, disallowed_special=())
    logger.debug("Tokenized into %d tokens", len(tokens))

    windows: List[List[float]] = []
    starts = []
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
        return [text]

    X = np.asarray(windows, dtype="float32")
    km = KMeans(n_clusters=min(n_clusters, len(windows)), n_init="auto")
    labels = km.fit_predict(X)
    logger.debug("Window labels: %s", labels.tolist())

    boundaries = [0]
    for idx in range(1, len(labels)):
        if labels[idx] != labels[idx - 1]:
            boundaries.append(starts[idx])
    boundaries.append(len(tokens))
    logger.debug("Detected boundaries at %s", boundaries)

    chunks = []
    for a, b in zip(boundaries[:-1], boundaries[1:]):
        chunk_tokens = tokens[a:b]
        chunks.append(enc.decode(chunk_tokens))
    logger.debug("Produced %d chunks", len(chunks))
    return chunks
