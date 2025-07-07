from typing import List

from .semantic_chunk import semantic_chunk_text
from .chunk_text import chunk_text


def topic_segmenter(text: str, model: str = "text-embedding-3-small") -> List[str]:
    """Segment text by topic using semantic chunking with a fallback."""
    chunks = semantic_chunk_text(text, model=model)
    if len(chunks) <= 1:
        return chunk_text(text)
    return chunks
