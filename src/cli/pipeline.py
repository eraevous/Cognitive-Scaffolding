# cli/pipeline.py
from pathlib import Path

import typer

from core.clustering.clustering_steps import run_all_steps
from core.config.config_registry import get_path_config
from scripts.pipeline import run_full_pipeline

app = typer.Typer()

@app.command()
def run_all(
    input_dir: Path = typer.Option(..., help="Directory with raw input documents"),
    chunked: bool = False,
    method: str = "summary",
    cluster_method: str = "hdbscan",
    model: str = "gpt-4"
):
    """
    Full ingestion + clustering pipeline:
    1. Upload and parse
    2. Classify
    3. Embed
    4. Cluster, label, export
    """
    paths = get_path_config()

    # Steps 1–3
    run_full_pipeline(
        input_dir=input_dir,
        chunked=chunked,
        method=method,
        overwrite=True
    )

    # Step 4
    run_all_steps(
        embedding_path=paths.root / "rich_doc_embeddings.json",
        metadata_dir=paths.metadata,
        out_dir=paths.output / "cluster_output",
        method=cluster_method,
        model=model
    )
