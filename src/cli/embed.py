# cli/embed.py
from pathlib import Path

import typer

from core.config.config_registry import get_path_config
from core.embeddings.embedder import generate_embeddings

app = typer.Typer()


@app.command()
def all(
    method: str = typer.Option(
        "parsed", help="Which text source to embed: parsed, summary, raw, meta"
    ),
    out_path: Path = typer.Option(None, help="Output path for embeddings JSON file"),
):
    """
    Generate embeddings from parsed text, summaries, or raw content.
    """
    paths = get_path_config()
    generate_embeddings(
        method=method, out_path=out_path, segment_mode=paths.semantic_chunking
    )
