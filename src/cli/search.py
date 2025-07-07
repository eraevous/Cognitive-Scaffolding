import typer

from core.retrieval.retriever import Retriever
from core.utils.logger import get_logger

app = typer.Typer()
logger = get_logger(__name__)


@app.command()
def semantic(query: str, k: int = 5):
    """Return top-k document IDs matching the query."""
    retriever = Retriever()
    logger.info("Running semantic search for: %s", query)
    hits = retriever.query(query, k=k)
    for doc_id, score in hits:
        print(doc_id, f"{score:.3f}")
