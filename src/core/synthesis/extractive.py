from __future__ import annotations

from collections import Counter
from typing import Iterable, List

from core.retrieval.lexical import LexicalHit, search_chatgpt_corpus


def synthesize_lexical_hits(query: str, hits: Iterable[LexicalHit]) -> str:
    """Build a local extractive synthesis from ranked lexical hits."""

    hit_list = list(hits)
    if not hit_list:
        return ""

    title_terms = Counter()
    for hit in hit_list:
        title_terms.update(
            token.lower()
            for token in hit.title.replace("_", " ").split()
            if len(token) > 3
        )
    common_terms = ", ".join(term for term, _ in title_terms.most_common(8))

    lines: List[str] = [
        f"Query: {query}",
        f"Top local hits: {len(hit_list)}",
    ]
    if common_terms:
        lines.append(f"Recurring title terms: {common_terms}")

    lines.append("")
    lines.append("Extractive throughline:")
    for idx, hit in enumerate(hit_list, start=1):
        lines.append(
            f"{idx}. {hit.title} ({hit.doc_id}, score={hit.score:.3f})\n"
            f"   {hit.snippet}"
        )

    return "\n".join(lines)


def synthesize_lexical_query(root, query: str, k: int = 8) -> str:
    hits = search_chatgpt_corpus(root, query, k=k)
    return synthesize_lexical_hits(query, hits)
