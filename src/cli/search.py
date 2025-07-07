import typer

from core.retrieval.retriever import Retriever

app = typer.Typer()


@app.command()
def semantic(query: str, k: int = 5):
    """Return top-k document IDs matching the query."""
    retriever = Retriever()
    hits = retriever.query(query, k=k)
    for doc_id, score in hits:
        print(doc_id, f"{score:.3f}")
