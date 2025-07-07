"""Utility to segment text into topic-coherent blocks."""
from typing import List

from .semantic_chunk import semantic_chunk_text


def segment_text(text: str) -> List[str]:
    """Return semantic segments of ``text`` using :func:`semantic_chunk_text`."""
    return semantic_chunk_text(text)
