# cli/embed.py
import typer
from pathlib import Path
from core.embeddings.embedder import generate_embeddings

app = typer.Typer()

@app.command()
def all(
    method: str = typer.Option("summary", help="Which text source to embed: parsed, summary, raw, meta"),
    out_path: Path = typer.Option(None, help="Output path for embeddings JSON file")
):
    """
    Generate embeddings from parsed text, summaries, or raw content.
    """
    generate_embeddings(method=method, out_path=out_path)