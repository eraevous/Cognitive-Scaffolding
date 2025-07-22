import typer
from pathlib import Path
from core.config.config_registry import get_path_config
from core.config.path_config import PathConfig
from core.storage.upload_local import prepare_document_for_processing

app = typer.Typer(help="Parse documents into text with optional path overrides")


def _resolve_paths(root: Path | None, raw: Path | None, parsed: Path | None, metadata: Path | None) -> PathConfig:
    base = get_path_config()
    return PathConfig(
        root=root or base.root,
        raw=raw or base.raw,
        parsed=parsed or base.parsed,
        metadata=metadata or base.metadata,
        output=base.output,
        vector=base.vector,
        schema=base.schema,
        semantic_chunking=base.semantic_chunking,
    )


@app.command()
def run(
    input_path: Path = typer.Argument(..., exists=True, readable=True),
    parsed_name: str | None = typer.Option(None, help="Custom name for single file"),
    root: Path | None = typer.Option(None, help="Override root directory"),
    raw_dir: Path | None = typer.Option(None, help="Raw documents directory"),
    parsed_dir: Path | None = typer.Option(None, help="Parsed documents directory"),
    metadata_dir: Path | None = typer.Option(None, help="Metadata directory"),
):
    """Parse a file or all files in a directory."""
    paths = _resolve_paths(root, raw_dir, parsed_dir, metadata_dir)

    if input_path.is_dir():
        for file in sorted(input_path.glob("*")):
            prepare_document_for_processing(file, paths=paths)
    else:
        prepare_document_for_processing(input_path, parsed_name=parsed_name, paths=paths)


if __name__ == "__main__":
    app()
