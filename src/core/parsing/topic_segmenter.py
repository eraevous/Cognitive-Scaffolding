"""Topic segmentation helpers built on semantic chunking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from core.parsing.semantic_chunk import semantic_chunk
from core.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class Segment:
    text: str
    start: int
    end: int
    cluster_id: int

    def to_dict(self) -> dict[str, object]:
        return {
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "cluster_id": self.cluster_id,
            "topic": f"cluster_{self.cluster_id}",
        }


def _paragraph_segments(text: str) -> List[dict[str, object]]:
    stripped = text.strip()
    if not stripped:
        return []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [stripped]
    segments: List[dict[str, object]] = []
    offset = 0
    for idx, paragraph in enumerate(paragraphs):
        start = text.find(paragraph, offset)
        if start == -1:
            start = offset
        end = start + len(paragraph)
        offset = end
        segments.append(Segment(paragraph, start, end, idx).to_dict())
    return segments


def segment_topics(
    text: str,
    *,
    window_tokens: int = 256,
    step_tokens: int = 128,
    cluster_method: str = "hdbscan",
    model: str | None = None,
) -> List[dict[str, object]]:
    """Return topic-aware segments for ``text``."""

    segments = semantic_chunk(
        text,
        window_tokens=window_tokens,
        step_tokens=step_tokens,
        cluster_method=cluster_method,
        model=model or "text-embedding-3-small",
    )
    if len(segments) > 1:
        logger.debug("topic_segmenter produced %s semantic segments", len(segments))
        return segments

    fallback = _paragraph_segments(text)
    logger.debug("topic_segmenter falling back to %s paragraph segments", len(fallback))
    return fallback


def topic_chunks(**kwargs) -> List[str]:
    """Return segment text only for convenience wrappers."""

    return [segment["text"] for segment in segment_topics(**kwargs)]


__all__ = ["segment_topics", "topic_chunks"]
