import typer
from pathlib import Path

from core.configuration.config_registry import get_path_config
from core.configuration.path_config import PathConfig
from core.output.artifacts import write_artifact
from core.synthesis.extractive import synthesize_lexical_query
from core.retrieval.retriever import Retriever
from core.synthesis.summarizer import synthesize_query

app = typer.Typer(help="Synthesize across retrieved corpus material")


def _echo_safe(message: str) -> None:
    typer.echo(message.encode("ascii", errors="replace").decode("ascii"))


def _save_synthesis(
    out: Path | None,
    paths: PathConfig,
    kind: str,
    query: str,
    synthesis: str,
    *,
    k: int,
) -> None:
    if not out:
        return
    lines = [
        f"# {kind.replace('-', ' ').title()}: {query}",
        "",
        f"- k: {k}",
        "",
        synthesis,
    ]
    path = write_artifact(out, paths, kind, query, lines)
    _echo_safe(f"Saved output to {path}")


@app.command("query")
def query_synthesis(
    query: str,
    k: int = typer.Option(8, help="Number of retrieved documents/chunks to use"),
    root: Path | None = typer.Option(None, help="Corpus root to search"),
    max_input_tokens: int = typer.Option(
        12000, help="Approximate token budget for retrieved source text"
    ),
    out: Path | None = typer.Option(None, help="Write synthesis to a file or directory"),
):
    """Search the corpus and summarize the conceptual throughline."""

    paths = PathConfig(root=root) if root else get_path_config()
    retriever = Retriever(paths=paths)
    synthesis = synthesize_query(
        query, retriever, k=k, max_input_tokens=max_input_tokens
    )
    if not synthesis:
        typer.echo("No retrievable text found for that query.")
        raise typer.Exit(1)
    _echo_safe(synthesis)
    _save_synthesis(out, paths, "semantic-synthesis", query, synthesis, k=k)


@app.command("lexical")
def lexical_synthesis(
    query: str,
    root: Path = typer.Option(..., help="ChatGPT corpus root to search"),
    k: int = typer.Option(8, help="Number of local hits to synthesize"),
    out: Path | None = typer.Option(None, help="Write synthesis to a file or directory"),
):
    """Create a local extractive synthesis from lexical search hits."""

    paths = PathConfig(root=root)
    synthesis = synthesize_lexical_query(root, query, k=k)
    if not synthesis:
        typer.echo("No local text found for that query.")
        raise typer.Exit(1)
    _echo_safe(synthesis)
    _save_synthesis(out, paths, "lexical-synthesis", query, synthesis, k=k)
