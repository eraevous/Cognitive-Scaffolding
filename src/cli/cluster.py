"""
📦 Module: cli.clustering
- @ai-path: cli.clustering
- @ai-source-file: combined_cli.py
- @ai-role: CLI Entrypoint
- @ai-intent: "Expose the full clustering pipeline via a Typer CLI interface."

🔍 Module Summary:
This module provides a Typer CLI command to trigger the document clustering pipeline. It orchestrates 
dimensionality reduction (UMAP), clustering (HDBSCAN and Spectral), GPT-driven cluster labeling, and saves 
visualizations and metadata. Paths can be optionally configured via a JSON config file.

🗂️ Contents:

| Name      | Type     | Purpose                                     |
|:----------|:---------|:--------------------------------------------|
| cluster   | CLI Command | Run full clustering pipeline and export results. |

🧠 For AI Agents:
- @ai-dependencies: typer, pathlib
- @ai-uses: run_clustering_pipeline, PathConfig
- @ai-tags: cli, clustering, orchestration

⚙️ Meta:
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add Typer interface for clustering entrypoint
- @change-summary: Bind clustering pipeline to CLI command
- @notes: ""

👤 Human Overview:
    - Context: Launch the full clustering process from the command line for rapid dataset analysis.
    - Change Caution: Paths must be configured correctly or results will not save to intended locations.
    - Future Hints: Add options to select clustering algorithm or embedding model dynamically.
"""

from pathlib import Path

import typer

from core.clustering.clustering_steps import run_all_steps
from core.configuration.config_registry import get_path_config

app = typer.Typer()


@app.command()
def run_all(
    embedding_path: Path = typer.Option(
        None, help="Path to the rich_doc_embeddings.json file"
    ),
    metadata_dir: Path = typer.Option(
        None, help="Path to directory with .meta.json files"
    ),
    out_dir: Path = typer.Option(None, help="Directory to save outputs"),
    method: str = "hdbscan",
    model: str = "gpt-4",
):
    """
    Run full clustering pipeline from existing embeddings.
    """
    paths = get_path_config()
    embedding_path = embedding_path or (paths.vector / "rich_doc_embeddings.json")
    metadata_dir = metadata_dir or paths.metadata
    out_dir = out_dir or (paths.output / "cluster_output")

    run_all_steps(
        embedding_path=embedding_path,
        metadata_dir=metadata_dir,
        out_dir=out_dir,
        method=method,
        model=model,
    )
