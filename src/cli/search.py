from typing import Any

from pathlib import Path

import typer

from core.configuration.config_registry import get_path_config
from core.configuration.path_config import PathConfig
from core.logger import get_logger
from core.output.artifacts import write_artifact
from core.retrieval.lexical import search_chatgpt_corpus
from core.retrieval.retriever import Retriever

app = typer.Typer()
logger = get_logger(__name__)


def _echo_safe(message: str) -> None:
    typer.echo(message.encode("ascii", errors="replace").decode("ascii"))


def _md_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


@app.command()
def semantic(
    query: str,
    k: int = 5,
    root: Path | None = typer.Option(None, help="Corpus root to search"),
    text: bool = typer.Option(False, help="Include retrieved chunk text"),
    aggregate: bool = typer.Option(False, help="Group chunks by source document"),
    out: Path | None = typer.Option(None, help="Write results to a file or directory"),
    index_name: str = typer.Option("default", help="Vector index profile to search"),
):
    """Return top-k document IDs matching the query."""
    paths = PathConfig(root=root) if root else get_path_config()
    retriever = Retriever(paths=paths, vector_name=index_name)
    logger.info("Running semantic search for: %s", query)
    hits = retriever.query_rich(query, k=k, return_text=text, aggregate=aggregate)
    lines = [
        f"# Semantic Search: {query}",
        "",
        f"- k: {k}",
        f"- aggregate: {aggregate}",
        f"- include_text: {text}",
        "",
        "| score | source | title | snippet |",
        "| --- | --- | --- | --- |",
    ]
    for hit in hits:
        label = hit["doc_id"]
        if hit.get("chunk"):
            label = f"{label}:{hit['chunk']}"
        base = f"{float(hit['score']):.3f}\t{label}\t{hit['title']}"
        snippet = ""
        if text:
            snippet = " ".join(str(hit.get("text", "")).split())[:500]
            base = f"{base}\t{snippet}"
        lines.append(
            f"| {float(hit['score']):.3f} | `{_md_cell(label)}` | "
            f"{_md_cell(hit['title'])} | {_md_cell(snippet)} |"
        )
        _echo_safe(base)
    if out:
        path = write_artifact(out, paths, "semantic-search", query, lines)
        _echo_safe(f"Saved output to {path}")


@app.command("file")
def semantic_file(
    file_path: Path,
    k: int = 5,
    root: Path | None = typer.Option(None, help="Corpus root to search"),
    text: bool = typer.Option(False, help="Include retrieved chunk text"),
    aggregate: bool = typer.Option(False, help="Group chunks by source document"),
    out: Path | None = typer.Option(None, help="Write results to a file or directory"),
    index_name: str = typer.Option("default", help="Vector index profile to search"),
):
    """Return top-k IDs similar to the text contained in ``file_path``."""
    paths = PathConfig(root=root) if root else get_path_config()
    retriever = Retriever(paths=paths, vector_name=index_name)
    logger.info("Running semantic search for file: %s", file_path)
    hits = retriever.query_file_rich(
        file_path, k=k, return_text=text, aggregate=aggregate
    )
    lines = [
        f"# Semantic File Search: {file_path}",
        "",
        f"- k: {k}",
        f"- aggregate: {aggregate}",
        f"- include_text: {text}",
        "",
        "| score | source | title | snippet |",
        "| --- | --- | --- | --- |",
    ]
    for hit in hits:
        label = hit["doc_id"]
        if hit.get("chunk"):
            label = f"{label}:{hit['chunk']}"
        base = f"{float(hit['score']):.3f}\t{label}\t{hit['title']}"
        snippet = ""
        if text:
            snippet = " ".join(str(hit.get("text", "")).split())[:500]
            base = f"{base}\t{snippet}"
        _echo_safe(base)
        lines.append(
            f"| {float(hit['score']):.3f} | `{_md_cell(label)}` | "
            f"{_md_cell(hit['title'])} | {_md_cell(snippet)} |"
        )
    if out:
        path = write_artifact(
            out, paths, "semantic-file-search", file_path.stem, lines
        )
        _echo_safe(f"Saved output to {path}")


@app.command("lexical")
def lexical(
    query: str,
    root: Path = typer.Option(..., help="ChatGPT corpus root to search"),
    k: int = typer.Option(10, help="Number of local hits to return"),
    out: Path | None = typer.Option(None, help="Write results to a file or directory"),
):
    """Search parsed ChatGPT transcripts locally without API calls."""

    paths = PathConfig(root=root)
    hits = search_chatgpt_corpus(root, query, k=k)
    lines = [
        f"# Lexical Search: {query}",
        "",
        f"- k: {k}",
        "",
        "| score | source | title | snippet |",
        "| --- | --- | --- | --- |",
    ]
    for hit in hits:
        _echo_safe(f"{hit.score:.3f}\t{hit.doc_id}\t{hit.title}\t{hit.snippet}")
        lines.append(
            f"| {hit.score:.3f} | `{_md_cell(hit.doc_id)}` | "
            f"{_md_cell(hit.title)} | {_md_cell(hit.snippet)} |"
        )
    if out:
        path = write_artifact(out, paths, "lexical-search", query, lines)
        _echo_safe(f"Saved output to {path}")
