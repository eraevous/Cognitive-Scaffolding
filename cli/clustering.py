"""
Module: cli/clustering.py 

- @ai-path: cli.clustering 
- @ai-source-file: combined_cli.py 
- @ai-module: clustering_cli 
- @ai-role: cli_entrypoint 
- @ai-entrypoint: cluster() 
- @ai-intent: "Expose the full clustering pipeline via a Typer CLI interface."

🔍 Summary:
This CLI command triggers the clustering pipeline that applies dimensionality reduction, runs HDBSCAN and Spectral clustering, generates smart GPT-based labels, and saves results to disk. Optional path configuration can be provided via a config file.

📦 Inputs:
- embedding_path (Path): Path to JSON of document embeddings
- metadata_dir (Path): Directory with `.meta.json` metadata files
- out_dir (Path): Where to save clustering output
- config_file (Path): Optional path to a JSON config for dynamic directory resolution

📤 Outputs:
- UMAP visualizations
- Cluster assignment maps
- Labeled CSV summary

🔗 Related Modules:
- clustering_runner → core pipeline logic
- path_config → used to resolve paths from config_file

🧠 For AI Agents:
- @ai-dependencies: typer, pathlib
- @ai-calls: run_clustering_pipeline(), PathConfig.from_file()
- @ai-uses: typer.Option, @app.command
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
- @notes: 
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