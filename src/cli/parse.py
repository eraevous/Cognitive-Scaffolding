"""CLI helpers for converting raw documents into parsed text."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import typer

from core.configuration import config_registry
from core.configuration.path_config import PathConfig
from core.storage.upload_local import prepare_document_for_processing

app = typer.Typer(add_completion=False, help="Document parsing utilities")


def _iter_sources(path: Path) -> Iterable[Path]:
    if path.is_file():
        yield path
    else:
        for candidate in sorted(path.iterdir()):
            if candidate.is_file():
                yield candidate


def _apply_overrides(
    base: PathConfig,
    *,
    root: Path | None,
    raw_dir: Path | None,
    parsed_dir: Path | None,
    metadata_dir: Path | None,
) -> PathConfig:
    kwargs = {
        "root": root or base.root,
        "raw": raw_dir or base.raw,
        "parsed": parsed_dir or base.parsed,
        "metadata": metadata_dir or base.metadata,
        "output": base.output,
        "vector": base.vector,
        "schema": base.schema,
        "semantic_chunking": base.semantic_chunking,
    }
    return PathConfig(**kwargs)


@app.command()
def run(
    input_path: Path = typer.Argument(..., exists=True),
    parsed_name: str | None = typer.Option(None, help="Name for the parsed output when a single file is provided"),
    root: Path | None = typer.Option(None, help="Override project root"),
    raw_dir: Path | None = typer.Option(None, help="Override raw directory"),
    parsed_dir: Path | None = typer.Option(None, help="Override parsed directory"),
    metadata_dir: Path | None = typer.Option(None, help="Override metadata directory"),
) -> None:
    """Parse documents from ``input_path`` and emit metadata stubs."""

    base = config_registry.get_path_config()
    paths = _apply_overrides(base, root=root, raw_dir=raw_dir, parsed_dir=parsed_dir, metadata_dir=metadata_dir)

    for source in _iter_sources(input_path):
        stub = prepare_document_for_processing(source, parsed_name=parsed_name if input_path.is_file() else None, paths=paths)
        typer.echo(stub["parsed_path"])


__all__ = ["app", "run"]
