from pathlib import Path

import typer

from core.configuration.config_registry import get_path_config
from core.parsing import parse_chatgpt_export

app = typer.Typer()


@app.command()
def parse(export_zip: Path, out_dir: Path = None):
    """Parse a ChatGPT export ZIP into conversation text files."""
    paths = get_path_config()
    out = out_dir or paths.parsed / "chatgpt_export"
    parse_chatgpt_export(export_zip, out)
