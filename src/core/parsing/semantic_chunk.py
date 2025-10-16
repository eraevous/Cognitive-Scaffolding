"""Semantic segmentation using embedding-based clustering."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
try:  # pragma: no cover - optional dependency
    import tiktoken  # type: ignore[import]
except Exception:  # pragma: no cover
    class _DummyEncoding:
        def encode(self, text, disallowed_special=()):
            return [ord(ch) for ch in text]

        def decode(self, tokens):
            return "".join(chr(int(t)) for t in tokens)

    class _DummyTiktoken:
        @staticmethod
        def encoding_for_model(_model):
            return _DummyEncoding()

    tiktoken = _DummyTiktoken()  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from sklearn.cluster import SpectralClustering  # type: ignore[import]
except Exception:  # pragma: no cover
    SpectralClustering = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import umap  # type: ignore[import]
except Exception:  # pragma: no cover
    umap = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import hdbscan  # type: ignore[import]
except Exception:  # pragma: no cover
    hdbscan = None  # type: ignore[assignment]

from core.utils.logger import get_logger

logger = get_logger(__name__)
DEFAULT_MODEL = "text-embedding-3-small"


def embed_text(text: str, model: str = DEFAULT_MODEL) -> List[float]:
    """Expose single-text embedding for test overrides."""

    from core.embeddings import embedder

    return embedder.embed_text(text, model=model)


_DEFAULT_EMBED_FN = embed_text


@dataclass(slots=True)
class _Window:
    start_token: int
    end_token: int
    text: str
    embedding: List[float]


def _windows(text: str, window_tokens: int, step_tokens: int, model: str) -> list[_Window]:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text, disallowed_special=())
    spans: list[tuple[int, int, str]] = []
    for start in range(0, len(tokens) or 1, step_tokens or 1):
        end = min(start + window_tokens, len(tokens))
        if start >= end and len(tokens) > 0:
            continue
        segment_tokens = tokens[start:end] if tokens else []
        window_text = encoding.decode(segment_tokens) if segment_tokens else text
        spans.append((start, end if tokens else len(tokens), window_text))
        if end == len(tokens):
            break
    if not spans:
        spans = [(0, len(tokens), text)]
    if embed_text is not _DEFAULT_EMBED_FN:
        embeddings = [embed_text(span[2], model=model) for span in spans]
    else:
        from core.embeddings import embedder

        embeddings = embedder.embed_text_batch([span[2] for span in spans], model=model)
    return [
        _Window(start, end, window_text, list(embedding))
        for (start, end, window_text), embedding in zip(spans, embeddings)
    ]


def _cluster(embeddings: np.ndarray, method: str) -> np.ndarray:
    if embeddings.shape[0] <= 1:
        return np.zeros(embeddings.shape[0], dtype=int)
    coords = embeddings
    if umap is not None and embeddings.shape[0] > 50:
        reducer = umap.UMAP(n_components=2, random_state=42)
        coords = reducer.fit_transform(embeddings)
    if method == "hdbscan" and hdbscan is not None:
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
        return clusterer.fit_predict(coords)
    if SpectralClustering is None:
        return np.zeros(embeddings.shape[0], dtype=int)
    try:
        n_clusters = max(1, min(5, embeddings.shape[0]))
        clusterer = SpectralClustering(
            n_clusters=n_clusters,
            assign_labels="discretize",
            random_state=42,
        )
        labels = clusterer.fit_predict(coords)
        return labels
    except Exception:  # pragma: no cover
        return np.zeros(embeddings.shape[0], dtype=int)


def semantic_chunk(
    text: str,
    *,
    window_tokens: int = 256,
    step_tokens: int = 128,
    cluster_method: str = "spectral",
    model: str = DEFAULT_MODEL,
) -> list[dict[str, object]]:
    """Segment ``text`` into semantic chunks and return chunk metadata."""

    windows = _windows(text, window_tokens, step_tokens, model)
    if not windows:
        return []

    embeddings = np.asarray([win.embedding for win in windows], dtype=np.float32)
    labels = _cluster(embeddings, cluster_method)
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text, disallowed_special=())

    chunks: list[dict[str, object]] = []
    current_label: int | None = None
    buffer: list[_Window] = []

    for window, label in zip(windows, labels):
        label = int(label)
        if current_label is None:
            current_label = label
            buffer = [window]
            continue
        if label == current_label:
            buffer.append(window)
        else:
            chunks.append(_merge_windows(buffer, current_label, tokens, encoding))
            current_label = label
            buffer = [window]
    if buffer:
        chunks.append(_merge_windows(buffer, current_label, tokens, encoding))

    if chunks:
        chunk_embeddings = [embed_text(chunk["text"], model=model) for chunk in chunks]
        for chunk, embedding in zip(chunks, chunk_embeddings):
            chunk["embedding"] = list(embedding)

    logger.debug("semantic_chunk produced %s segments", len(chunks))
    return chunks


def _merge_windows(
    windows: list[_Window],
    cluster_id: int,
    tokens: list[int],
    encoding,
) -> dict[str, object]:
    start_token = windows[0].start_token
    end_token = windows[-1].end_token
    start_char = len(encoding.decode(tokens[:start_token]))
    end_char = len(encoding.decode(tokens[:end_token]))
    text = " ".join(win.text.strip() for win in windows).strip()
    embedding = windows[0].embedding
    return {
        "text": text,
        "embedding": embedding,
        "topic": f"cluster_{cluster_id}",
        "start": start_char,
        "end": end_char,
        "cluster_id": cluster_id,
    }


__all__ = ["semantic_chunk", "umap", "hdbscan", "DEFAULT_MODEL"]
