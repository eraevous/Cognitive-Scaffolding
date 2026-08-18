from typing import Iterable, List

from core.llm.invoke import summarize_text
from core.retrieval.retriever import Retriever


CHARS_PER_TOKEN_ESTIMATE = 4
SYNTHESIS_OVERHEAD_TOKENS = 1000
MIN_SOURCE_TOKENS = 240


def summarize_documents(doc_ids: Iterable[str], retriever: Retriever) -> str:
    """Retrieve documents by ID and produce a combined summary."""
    texts: List[str] = []
    for doc_id in doc_ids:
        result = retriever.query(doc_id, k=1, return_text=True)
        if result and isinstance(result[0], tuple) and len(result[0]) == 3:
            texts.append(result[0][2])
    combined = "\n".join(texts)
    if not combined:
        return ""
    summary = summarize_text(combined, doc_type="standard")
    return summary.get("summary", "")


def _trim_text(text: str, max_tokens: int) -> str:
    max_chars = max_tokens * CHARS_PER_TOKEN_ESTIMATE
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0].strip()


def synthesize_query(
    query: str,
    retriever: Retriever,
    k: int = 8,
    *,
    max_input_tokens: int = 50000,
) -> str:
    """Search for relevant chunks and synthesize a cited throughline summary."""

    hits = retriever.query_rich(query, k=k, return_text=True, aggregate=True)
    texts: List[str] = []
    source_budget = max(max_input_tokens - SYNTHESIS_OVERHEAD_TOKENS, MIN_SOURCE_TOKENS)
    source_limit = max(1, min(len(hits), source_budget // MIN_SOURCE_TOKENS))
    per_source_tokens = max(MIN_SOURCE_TOKENS, source_budget // source_limit)
    for idx, hit in enumerate(hits[:source_limit], start=1):
        text = str(hit.get("text", "")).strip()
        if not text:
            continue
        source = f"S{idx}"
        title = hit.get("title", hit.get("doc_id"))
        doc_id = hit.get("doc_id", hit.get("result_id"))
        score = float(hit.get("score", 0.0))
        trimmed = _trim_text(text, per_source_tokens)
        texts.append(
            f"[{source}] {title} ({doc_id}, score={score:.3f})\n{trimmed}"
        )

    if not texts:
        return ""

    prompt = (
        "Synthesize the recurring ideas, useful distinctions, and unresolved "
        "questions in these retrieved conversation excerpts. Cite sources using "
        "the bracketed source labels such as [S1] when making claims. Return a "
        'JSON object with a single string field named "summary".\n\n'
        f"User query: {query}\n\n"
        + "\n\n---\n\n".join(texts)
    )
    prompt = _trim_text(prompt, max_input_tokens)
    summary = summarize_text(prompt, doc_type="chatlog", prompt_override="{text}")
    return summary.get("summary", "")
