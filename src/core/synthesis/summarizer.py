"""Combine retrieved chunks and call an LLM summarizer."""

from __future__ import annotations

from typing import Iterable, Protocol


class SupportsQuery(Protocol):
    def query(
        self,
        text: str,
        k: int = 5,
        *,
        return_text: bool = False,
    ) -> list:
        ...


def summarize_text(text: str, doc_type: str = "standard") -> dict[str, object]:
    """Fallback summarisation routine used when no LLM client is configured."""

    excerpt = text[:500]
    return {
        "summary": excerpt,
        "topics": [],
        "tags": [],
        "themes": [],
        "priority": 0,
        "tone": "neutral",
        "stage": "draft",
        "depth": "low",
        "category": doc_type,
    }


def summarize_documents(doc_ids: Iterable[str], retriever: SupportsQuery, doc_type: str = "standard") -> str:
    """Fetch chunk text for ``doc_ids`` and return a combined summary string."""

    collected: list[str] = []
    for doc_id in doc_ids:
        hits = retriever.query(doc_id, k=1, return_text=True)
        if not hits:
            continue
        text = hits[0][2] if len(hits[0]) >= 3 else ""
        if text:
            collected.append(text)
    if not collected:
        return ""
    payload = summarize_text("\n".join(collected), doc_type=doc_type)
    return str(payload.get("summary", ""))


__all__ = ["summarize_documents", "summarize_text"]
