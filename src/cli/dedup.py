"""Typer command exposing prompt deduplication."""

from __future__ import annotations

from pathlib import Path

import typer

from core.configuration import config_registry
from core.utils.dedup import dedup_lines_in_folder

app = typer.Typer(add_completion=False, help="Prompt deduplication utilities")


def _default_output(paths) -> Path:
    return Path(paths.output) / "deduplicated_prompts.txt"


@app.command()
def prompts(
    prompt_dir: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True),
    out_file: Path | None = typer.Option(None, help="Destination for deduplicated prompts"),
) -> None:
    """Write unique prompt lines from ``prompt_dir`` to ``out_file``."""

    paths = config_registry.get_path_config()
    destination = out_file or _default_output(paths)
    result = dedup_lines_in_folder(prompt_dir, output_file=destination)
    typer.echo(str(result))


__all__ = ["app", "prompts"]
