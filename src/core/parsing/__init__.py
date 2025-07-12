"""Lightweight wrappers to avoid heavy imports at module load."""
from __future__ import annotations

def semantic_chunk_text(*args, **kwargs):
    from .semantic_chunk import semantic_chunk_text as fn
    return fn(*args, **kwargs)


def segment_text(*args, **kwargs):
    from .topic_segmenter import segment_text as fn
    return fn(*args, **kwargs)


def segment_topics(*args, **kwargs):
    from .topic_segmenter import segment_topics as fn
    return fn(*args, **kwargs)


def topic_segmenter(*args, **kwargs):
    from .topic_segmenter import topic_segmenter as fn
    return fn(*args, **kwargs)


def parse_chatgpt_export(*args, **kwargs):
    from .openai_export import parse_chatgpt_export as fn
    return fn(*args, **kwargs)

__all__ = [
    "semantic_chunk_text",
    "segment_text",
    "segment_topics",
    "topic_segmenter",
    "parse_chatgpt_export",
]
