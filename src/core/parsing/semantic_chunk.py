"""Semantic chunking utilities focused on retrieval-first segmentation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

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


@dataclass
class _Window:
    idx: int
    start: int
    end: int
    text: str


@dataclass
class _Segment:
    start: int
    end: int
    window_ids: List[int]
    entry_score: float
    entry_reason: Optional[str]
    internal_max: float = 0.0


@dataclass
class _Boundary:
    reason: str
    score: float


class _FallbackTokenizer:
    """Lightweight tokenizer used when ``tiktoken`` is unavailable."""

    def encode(self, text: str, disallowed_special: Iterable[str] = ()) -> List[str]:
        del disallowed_special
        return list(text)

    def decode(self, tokens: Sequence[str]) -> str:
        return "".join(tokens)


def _get_tokenizer(model: str):
    if tiktoken is None:  # pragma: no cover - optional dependency
        logger.warning("tiktoken unavailable; falling back to character tokenizer")
        return _FallbackTokenizer()

    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:  # pragma: no cover - optional dependency
        logger.warning(
            "Model %%s not found in tiktoken; using cl100k_base encoding", model
        )
        try:
            return tiktoken.get_encoding("cl100k_base")
        except Exception:  # pragma: no cover - optional dependency
            logger.warning(
                "Failed to load cl100k_base; falling back to character tokenizer"
            )
            return _FallbackTokenizer()


def _batched_embeddings(
    texts: Sequence[str],
    model: str,
    batch_size: Optional[int],
) -> List[List[float]]:
    if not texts:
        return []

    if batch_size and batch_size > 0:
        vectors: List[List[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            vectors.extend(
                embed_text_batch(batch, model=model, embedder=embed_text)
            )
        return vectors

    return embed_text_batch(texts, model=model, embedder=embed_text)


def _normalize_vectors(vectors: Sequence[Sequence[float]]) -> np.ndarray:
    if not vectors:
        return np.zeros((0, 0), dtype="float32")
    X = np.asarray(vectors, dtype="float32")
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return X / norms


def _compute_cosine_deltas(norm_vectors: np.ndarray) -> List[float]:
    if len(norm_vectors) < 2:
        return []
    sims = np.sum(norm_vectors[:-1] * norm_vectors[1:], axis=1)
    sims = np.clip(sims, -1.0, 1.0)
    return [float(1.0 - sim) for sim in sims]


def _build_windows(
    tokens: Sequence[Any],
    tokenizer,
    window_tokens: int,
    step_tokens: int,
) -> List[_Window]:
    windows: List[_Window] = []
    if not tokens:
        return windows

    idx = 0
    for start in range(0, len(tokens), step_tokens):
        end = min(start + window_tokens, len(tokens))
        if start >= len(tokens):
            break
        if start >= end:
            continue
        window_text = tokenizer.decode(tokens[start:end])
        if not window_text:
            continue
        windows.append(_Window(idx=idx, start=start, end=end, text=window_text))
        idx += 1
    return windows


def _segment_windows(
    windows: Sequence[_Window],
    deltas: Sequence[float],
    tau: float,
    max_chunk_tokens: int,
) -> Tuple[List[_Segment], List[_Boundary]]:
    if not windows:
        return [], []

    segments: List[_Segment] = []
    boundaries: List[_Boundary] = []

    current = _Segment(
        start=windows[0].start,
        end=windows[0].end,
        window_ids=[windows[0].idx],
        entry_score=0.0,
        entry_reason=None,
        internal_max=0.0,
    )

    for idx in range(1, len(windows)):
        window = windows[idx]
        delta = float(deltas[idx - 1]) if idx - 1 < len(deltas) else 0.0
        candidate_end = max(current.end, window.end)
        boundary_due_to_change = delta >= tau
        boundary_due_to_span = (candidate_end - current.start) > max_chunk_tokens

        if boundary_due_to_change or boundary_due_to_span:
            segments.append(current)
            reason = "change" if boundary_due_to_change else "length"
            boundaries.append(_Boundary(reason=reason, score=delta))
            current = _Segment(
                start=window.start,
                end=window.end,
                window_ids=[window.idx],
                entry_score=delta,
                entry_reason=reason,
                internal_max=0.0,
            )
            continue

        current.window_ids.append(window.idx)
        current.end = candidate_end
        current.internal_max = max(current.internal_max, delta)

    segments.append(current)
    return segments, boundaries


def _merge_two_segments(left: _Segment, boundary: _Boundary, right: _Segment) -> _Segment:
    return _Segment(
        start=left.start,
        end=right.end,
        window_ids=left.window_ids + right.window_ids,
        entry_score=left.entry_score,
        entry_reason=left.entry_reason,
        internal_max=max(
            left.internal_max,
            right.internal_max,
            boundary.score,
            right.entry_score,
        ),
    )


def _merge_small_segments(
    segments: List[_Segment],
    boundaries: List[_Boundary],
    min_chunk_tokens: int,
) -> Tuple[List[_Segment], List[_Boundary]]:
    if len(segments) <= 1:
        return segments, boundaries

    idx = 0
    while idx < len(segments):
        segment = segments[idx]
        span = max(segment.end - segment.start, 0)
        if span >= min_chunk_tokens:
            idx += 1
            continue

        merged = False
        if idx > 0 and boundaries[idx - 1].reason != "change":
            segments[idx - 1] = _merge_two_segments(
                segments[idx - 1], boundaries[idx - 1], segment
            )
            del segments[idx]
            del boundaries[idx - 1]
            idx = max(idx - 1, 0)
            merged = True
        elif idx < len(segments) - 1 and boundaries[idx].reason != "change":
            segments[idx] = _merge_two_segments(segment, boundaries[idx], segments[idx + 1])
            del segments[idx + 1]
            del boundaries[idx]
            merged = True
        if not merged:
            idx += 1

    return segments, boundaries


def _chunk_to_dict(
    tokenizer,
    tokens: Sequence[Any],
    segment: _Segment,
    embedding: Sequence[float],
    source_doc_id: Optional[str],
) -> Dict[str, Any]:
    chunk_tokens = tokens[segment.start : segment.end]
    text = tokenizer.decode(chunk_tokens) if chunk_tokens else ""
    topic_change_score = max(segment.entry_score, segment.internal_max)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return {
        "text": text,
        "embedding": list(embedding),
        "start": int(segment.start),
        "end": int(segment.end),
        "topic_change_score": float(topic_change_score),
        "cluster_id": None,
        "window_ids": list(segment.window_ids),
        "source_doc_id": source_doc_id,
        "sha256": digest,
    }


def _assign_clusters(
    embeddings: Sequence[Sequence[float]],
    method: str,
) -> Optional[List[int]]:
    if len(embeddings) < 3:
        return [0 for _ in embeddings]

    if umap is None:  # pragma: no cover - optional dependency
        logger.warning("Adaptive mode requested but umap-learn is unavailable")
        return None

    try:
        X = np.asarray(embeddings, dtype="float32")
        n_neighbors = max(2, min(15, len(embeddings) - 1))
        reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=0.1, random_state=42)
        X_red = reducer.fit_transform(X)
    except Exception:  # pragma: no cover - optional dependency
        logger.exception("UMAP reduction failed; skipping adaptive clustering")
        return None

    method = method.lower()
    if method not in {"spectral", "hdbscan"}:
        raise ValueError(f"Unsupported cluster_method: {method}")
    labels: Optional[np.ndarray] = None
    if method == "spectral":
        try:
            upper = max(2, len(embeddings) // 2)
            n_clusters = max(2, min(len(embeddings), upper))
            clusterer = SpectralClustering(
                n_clusters=n_clusters,
                affinity="nearest_neighbors",
                assign_labels="discretize",
                random_state=42,
            )
            labels = clusterer.fit_predict(X_red)
        except Exception:  # pragma: no cover - optional dependency
            logger.exception("Spectral clustering failed; attempting HDBSCAN fallback")
            method = "hdbscan"

    if method == "hdbscan":
        if hdbscan is None:  # pragma: no cover - optional dependency
            logger.warning("HDBSCAN not installed; cannot perform adaptive clustering")
            return None
        min_cluster_size = max(2, min(len(embeddings), max(2, len(embeddings) // 2)))
        clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size)
        labels = clusterer.fit_predict(X_red)

    if labels is None:
        return None

    mapped: List[int] = []
    label_map: Dict[int, int] = {}
    next_id = 0
    for raw in labels.tolist():
        value = int(raw)
        if value < 0:
            value = 0
        if value not in label_map:
            label_map[value] = next_id
            next_id += 1
        mapped.append(label_map[value])

    return mapped


def semantic_chunk(
    text: str,
    model: str = "text-embedding-3-small",
    window_tokens: int = 256,
    step_tokens: int = 128,
    *,
    mode: str = "coarse",
    cluster_method: str = "spectral",
    change_point_cosine_tau: float = 0.28,
    min_chunk_tokens: int = 120,
    max_chunk_tokens: int = 1200,
    batch_size: Optional[int] = None,
    source_doc_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return retrieval-ready semantic chunks with provenance metadata."""

    if window_tokens <= 0 or step_tokens <= 0:
        raise ValueError("window_tokens and step_tokens must be positive integers")
    if min_chunk_tokens <= 0 or max_chunk_tokens <= 0:
        raise ValueError("Chunk token thresholds must be positive")
    if min_chunk_tokens > max_chunk_tokens:
        raise ValueError("min_chunk_tokens cannot exceed max_chunk_tokens")

    tokenizer = _get_tokenizer(model)
    tokens = tokenizer.encode(text, disallowed_special=())
    total_tokens = len(tokens)
    logger.debug("Tokenized into %d tokens", total_tokens)

    windows = _build_windows(tokens, tokenizer, window_tokens, step_tokens)
    logger.debug("Created %d windows", len(windows))

    if total_tokens == 0:
        embeddings = _batched_embeddings([text], model, batch_size)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [
            {
                "text": text,
                "embedding": embeddings[0] if embeddings else [],
                "start": 0,
                "end": 0,
                "topic_change_score": 0.0,
                "cluster_id": None,
                "window_ids": [],
                "source_doc_id": source_doc_id,
                "sha256": digest,
            }
        ]

    if len(windows) < 3:
        embeddings = _batched_embeddings([text], model, batch_size)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        window_ids = [w.idx for w in windows]
        return [
            {
                "text": text,
                "embedding": embeddings[0] if embeddings else [],
                "start": 0,
                "end": total_tokens,
                "topic_change_score": 0.0,
                "cluster_id": None,
                "window_ids": window_ids,
                "source_doc_id": source_doc_id,
                "sha256": digest,
            }
        ]

    window_embeddings = list(
        _batched_embeddings([w.text for w in windows], model, batch_size)
    )
    if len(window_embeddings) != len(windows):
        logger.warning(
            "Window embedding count mismatch (windows=%d, embeddings=%d); truncating",
            len(windows),
            len(window_embeddings),
        )
        limit = min(len(windows), len(window_embeddings))
        windows = windows[:limit]
        window_embeddings = window_embeddings[:limit]

    norm_vectors = _normalize_vectors(window_embeddings)
    deltas = _compute_cosine_deltas(norm_vectors)

    segments, boundaries = _segment_windows(
        windows,
        deltas,
        change_point_cosine_tau,
        max_chunk_tokens,
    )

    segments, boundaries = _merge_small_segments(
        segments,
        boundaries,
        min_chunk_tokens,
    )

    if not segments:
        logger.warning("No segments produced; returning coarse fallback chunk")
        embeddings = _batched_embeddings([text], model, batch_size)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return [
            {
                "text": text,
                "embedding": embeddings[0] if embeddings else [],
                "start": 0,
                "end": total_tokens,
                "topic_change_score": 0.0,
                "cluster_id": None,
                "window_ids": [w.idx for w in windows],
                "source_doc_id": source_doc_id,
                "sha256": digest,
            }
        ]

    chunk_texts = [
        tokenizer.decode(tokens[segment.start : segment.end])
        if segment.start < segment.end
        else ""
        for segment in segments
    ]

    chunk_embeddings = list(_batched_embeddings(chunk_texts, model, batch_size))
    if len(chunk_embeddings) < len(segments):
        logger.warning(
            "Chunk embedding count mismatch (segments=%d, embeddings=%d); padding",
            len(segments),
            len(chunk_embeddings),
        )
        chunk_embeddings.extend([[]] * (len(segments) - len(chunk_embeddings)))
    elif len(chunk_embeddings) > len(segments):
        chunk_embeddings = chunk_embeddings[: len(segments)]

    chunks = [
        _chunk_to_dict(tokenizer, tokens, segment, embedding, source_doc_id)
        for segment, embedding in zip(segments, chunk_embeddings)
    ]

    mode_value = mode.lower()
    if mode_value == "adaptive" and chunks:
        cluster_ids = _assign_clusters(chunk_embeddings, cluster_method)
        if cluster_ids is not None:
            for chunk, cluster_id in zip(chunks, cluster_ids):
                chunk["cluster_id"] = int(cluster_id)
        else:
            logger.debug("Adaptive clustering skipped; leaving cluster_id unset")
    elif mode_value != "coarse":
        raise ValueError(f"Unsupported mode: {mode}")

    logger.debug("Produced %d segments", len(chunks))
    return chunks


def semantic_chunk_text(*args, **kwargs) -> List[str]:
    """Compatibility wrapper returning only text chunks."""
    return [c["text"] for c in semantic_chunk(*args, **kwargs)]
