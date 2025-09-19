# cli/pipeline.py
from pathlib import Path

import typer

from core.clustering.clustering_steps import run_all_steps
from core.config.config_registry import get_path_config
from core.config.path_config import PathConfig
from scripts.pipeline import run_full_pipeline

app = typer.Typer()


def _resolve_paths(
    root: Path | None,
    raw: Path | None,
    parsed: Path | None,
    metadata: Path | None,
    output: Path | None,
) -> PathConfig:
    base = get_path_config()
    return PathConfig(
        root=root or base.root,
        raw=raw or base.raw,
        parsed=parsed or base.parsed,
        metadata=metadata or base.metadata,
        output=output or base.output,
        vector=base.vector,
        schema=base.schema,
        semantic_chunking=base.semantic_chunking,
    )


@app.command()
def run_all(
    input_dir: Path = typer.Option(..., help="Directory with raw input documents"),
    chunked: bool = False,
    segmentation: str = "semantic",
    method: str = "summary",
    cluster_method: str = "hdbscan",
    model: str = "gpt-4",
    root: Path | None = typer.Option(None, help="Override root directory"),
    raw_dir: Path | None = typer.Option(None, help="Raw documents directory"),
    parsed_dir: Path | None = typer.Option(None, help="Parsed documents directory"),
    metadata_dir: Path | None = typer.Option(None, help="Metadata directory"),
    output_dir: Path | None = typer.Option(None, help="Output directory"),
):
    """
    Full ingestion + clustering pipeline:
    1. Upload and parse
    2. Classify
    3. Embed
    4. Cluster, label, export
    """
    paths = _resolve_paths(root, raw_dir, parsed_dir, metadata_dir, output_dir)

    # Steps 1–3
    run_full_pipeline(
        input_dir=input_dir,
        chunked=chunked,
        method=method,
        overwrite=True,
        segmentation=segmentation,
        paths=paths,
    )

    # Step 4
    run_all_steps(
        embedding_path=paths.root / "rich_doc_embeddings.json",
        metadata_dir=paths.metadata,
        out_dir=paths.output / "cluster_output",
        method=cluster_method,
        model=model,
    )
