from pathlib import Path

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


@app.command("file")
def semantic_file(file_path: typer.FileText, k: int = 5):
    """Return top-k IDs similar to the text contained in ``file_path``."""
    retriever = Retriever()
    logger.info("Running semantic search for file: %s", file_path.name)
    hits = retriever.query_file(Path(file_path.name), k=k)
    for doc_id, score in hits:
        print(doc_id, f"{score:.3f}")
