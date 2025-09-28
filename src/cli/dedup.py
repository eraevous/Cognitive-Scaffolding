from pathlib import Path

import typer

from core.configuration.config_registry import get_path_config
from core.utils.dedup import dedup_lines_in_folder

app = typer.Typer()


@app.command()
def dedup_prompts(
    prompt_dir: Path = typer.Option(None, help="Directory with prompt text files"),
    out_file: Path = typer.Option(None, help="Output file for unique lines"),
) -> None:
    """Deduplicate lines across prompt files."""
    paths = get_path_config()
    if prompt_dir is None:
        prompt_dir = Path(paths.parsed) / "prompts"
    if out_file is None:
        out_file = Path("dedup.txt")
    dedup_lines_in_folder(prompt_dir, out_file)
    typer.echo(f"✅ Wrote deduped lines to {out_file}")
