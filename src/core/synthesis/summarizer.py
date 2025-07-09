from typing import Iterable, List

from core.llm.invoke import summarize_text
from core.retrieval.retriever import Retriever


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
