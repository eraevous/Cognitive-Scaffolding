from pathlib import Path
from core.parsing.openai_export import parse_chatgpt_export

import typer

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
