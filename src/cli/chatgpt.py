from pathlib import Path

import typer

from core.parsing.openai_export import parse_chatgpt_export
from core.workflows.chatgpt_corpus import (
    ingest_chatgpt_export,
    repair_chatgpt_embeddings,
)

app = typer.Typer(help="ChatGPT data export utilities")


@app.command("parse")
def parse_export(
    export_path: Path = typer.Argument(
        ..., exists=True, help="Path to ChatGPT export zip or folder"
    ),
    out_dir: Path = typer.Option(
        Path("chat_exports"), help="Directory to save parsed conversations"
    ),
    markdown: bool = typer.Option(False, help="Save transcripts as Markdown"),
):
    """Extract conversations and prompts from a ChatGPT data export."""

    results = parse_chatgpt_export(export_path, out_dir, markdown=markdown)
    typer.echo(f"Parsed {len(results)} conversations into {out_dir}")


@app.command("ingest")
def ingest_export(
    export_path: Path = typer.Argument(
        ..., exists=True, help="Path to ChatGPT export zip or extracted folder"
    ),
    root: Path = typer.Option(
        Path("chatgpt_corpus"),
        help="Corpus root for parsed conversations, manifest, vectors, and outputs",
    ),
    overwrite: bool = typer.Option(
        False, help="Rewrite parsed conversations even when content hashes match"
    ),
    embed: bool = typer.Option(True, help="Generate/rebuild the FAISS index"),
    model: str = typer.Option(
        "text-embedding-3-small", help="OpenAI embedding model to use"
    ),
):
    """Build or refresh a searchable ChatGPT conversation corpus."""

    result = ingest_chatgpt_export(
        export_path,
        root,
        overwrite=overwrite,
        embed=embed,
        model=model,
    )
    typer.echo(f"Corpus root: {result.root}")
    typer.echo(f"Parsed conversations: {result.parsed_dir}")
    typer.echo(f"Manifest: {result.manifest_path}")
    typer.echo(
        f"Total: {result.total} | Written: {result.written} | "
        f"Skipped unchanged: {result.skipped} | "
        f"Skipped empty: {result.skipped_empty} | Embedded: {result.embedded}"
    )


@app.command("repair-embeddings")
def repair_embeddings(
    root: Path = typer.Option(..., help="Corpus root with parsed ChatGPT transcripts"),
    model: str = typer.Option(
        "text-embedding-3-small", help="OpenAI embedding model to use"
    ),
):
    """Append missing transcript embeddings to an existing corpus index."""

    failure_path = repair_chatgpt_embeddings(root, model=model)
    typer.echo(f"Repaired embeddings for corpus: {root}")
    if failure_path.exists():
        typer.echo(f"Failures remain: {failure_path}")
    else:
        typer.echo("No embedding failures remain.")
