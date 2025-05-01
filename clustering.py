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


import typer
from pathlib import Path
from core_lib.clustering.clustering_runner import run_clustering_pipeline
from core_lib.config.path_config import PathConfig

app = typer.Typer()

@app.command()
def cluster(
    embedding_path: Path = Path("rich_doc_embeddings.json"),
    metadata_dir: Path = Path("metadata"),
    out_dir: Path = Path("output"),
    config_file: Path = typer.Option(None, help="Optional config file for flexible paths")
):
    """Run UMAP, clustering, labeling, and export."""
    paths = PathConfig.from_file(config_file) if config_file else PathConfig()

    run_clustering_pipeline(
        embedding_path=embedding_path,
        metadata_dir=paths.metadata,
        out_dir=paths.output
    )