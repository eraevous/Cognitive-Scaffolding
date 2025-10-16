"""Typer CLI entry point for the ingestion pipeline."""

from __future__ import annotations

from pathlib import Path

import typer

from core.configuration import config_registry
from core.configuration.path_config import PathConfig
from scripts.pipeline import run_all_steps, run_pipeline

app = typer.Typer(add_completion=False)


def get_path_config() -> PathConfig:
    return config_registry.get_path_config()


@app.command()
def main(
    input_dir: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True),
    chunked: bool = typer.Option(False, help="Use chunked summarisation"),
    overwrite: bool = typer.Option(False, help="Recreate metadata when it already exists"),
    method: str = typer.Option("summary", help="Embedding source method"),
    segmentation: str = typer.Option("semantic", help="Segmentation strategy"),
) -> None:
    paths = get_path_config()
    run_pipeline(
        input_dir=input_dir,
        chunked=chunked,
        overwrite=overwrite,
        method=method,
        segmentation=segmentation,
        paths=paths,
    )


__all__ = ["app", "get_path_config", "run_pipeline", "run_all_steps"]
