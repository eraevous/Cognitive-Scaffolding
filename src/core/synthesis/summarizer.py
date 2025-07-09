from pathlib import Path
from typing import List, Dict

from core.retrieval.retriever import Retriever
from core.llm.invoke import summarize_text
from core.utils.logger import get_logger

logger = get_logger(__name__)


def summarize_and_link(query: str, retriever: Retriever, chunk_dir: Path, k: int = 4) -> Dict[str, List[str]]:
    """Retrieve related chunks for a query and return a combined summary."""
    results = retriever.search(query, k=k, chunk_dir=chunk_dir, return_text=True)
    if not results:
        return {"summary": "", "sources": []}

    summaries = []
    sources = []
    for doc_id, score, text in results:
        try:
            data = summarize_text(text)
            summaries.append(data.get("summary", ""))
            sources.append(doc_id)
        except Exception as e:
            logger.warning("Summary failed for %s: %s", doc_id, e)
    combined = "\n".join(summaries)
    if combined:
        combined = summarize_text(combined).get("summary", combined)
    return {"summary": combined, "sources": sources}
