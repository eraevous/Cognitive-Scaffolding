"""Module: core.synthesis.insight_summarizer
Aggregate and link insights from retrieved documents.
"""
from __future__ import annotations

from typing import List

from core.llm.invoke import summarize_text


def summarize_and_link(docs: List[str], model: str = "gpt-4") -> str:
    """Return a joint summary highlighting connections between documents."""
    summaries = [summarize_text(d).get("summary", "") for d in docs]
    joined = "\n".join(f"- {s}" for s in summaries if s)
    prompt = (
        "Given the following summaries, identify common themes or insights and "
        "produce a concise overview.\n" + joined
    )
    return summarize_text(prompt, doc_type="standard", model=model).get("summary", "")

