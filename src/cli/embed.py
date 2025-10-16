"""Typer entry point for triggering embedding generation."""

from __future__ import annotations

from pathlib import Path

import typer

from core.configuration import config_registry
from core.configuration.path_config import PathConfig
from core.embeddings.embedder import generate_embeddings

app = typer.Typer(add_completion=False, help="Embedding utilities")


@app.command()
def all(
    method: str = typer.Option("parsed", help="Source text to embed"),
    out_path: Path | None = typer.Option(None, help="Optional destination for embeddings JSON"),
    segment_mode: bool | None = typer.Option(None, help="Override semantic chunking flag"),
) -> None:
    """Generate embeddings using the shared :mod:`core.embeddings.embedder`."""

    paths: PathConfig = config_registry.get_path_config()
    destination = out_path or Path(paths.root) / "rich_doc_embeddings.json"
    generate_embeddings(
        method=method,
        out_path=destination,
        segment_mode=segment_mode if segment_mode is not None else bool(paths.semantic_chunking),
        paths=paths,
    )
    typer.echo(str(destination))


__all__ = ["app", "all"]
