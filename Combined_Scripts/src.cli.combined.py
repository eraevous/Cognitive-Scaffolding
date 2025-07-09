#__________________________________________________________________
# File: __init__.py
# No docstring found

#__________________________________________________________________
# File: agent.py
# No docstring found

import typer

from core.agent_hub import run_agents

app = typer.Typer()


@app.command()
def run(prompt: str, roles: str = "synthesizer"):  # comma-separated
    """Run a simple multi-agent loop with given roles."""
    role_list = [r.strip() for r in roles.split(",") if r.strip()]
    run_agents(prompt, role_list)
#__________________________________________________________________
# File: batch_ops.py
"""
Module: cli/batch_ops.py 

- @ai-path: cli.batch_ops 
- @ai-source-file: combined_cli.py 
- @ai-module: batch_cli 
- @ai-role: cli_batch_controller 
- @ai-entrypoint: classify_all(), recover_failed(), clean_corrupt_meta(), upload_all(), clear_s3(), organize_all() 
- @ai-intent: "Provide CLI commands for classification recovery, file uploads, metadata validation, and S3 cleanup."

🔍 Summary:
This section defines higher-level CLI commands for batch workflows and admin tasks. It enables robust recovery from failed classification runs, validates or deletes corrupt `.meta.json` files, uploads files with parsed text, organizes metadata by cluster labels, and resets specific folders in S3.

📦 Inputs:
- config_file (Path): Path to config file specifying directory layout
- cluster_file (Path): Optional cluster map to use for `organize_all`
- prefixes (str): Comma-separated list of S3 prefixes for `clear_s3`

📤 Outputs:
- Updates `.meta.json` files
- Organizes metadata into subfolders
- Removes invalid metadata
- Uploads raw/parsed files to S3
- Clears targeted S3 prefixes

🔗 Related Modules:
- main_commands → used by classify commands
- combined_utils → upload logic
- storage.s3_utils → used by `clear_s3`
- metadata.schema → used to validate `.meta.json`

🧠 For AI Agents:
- @ai-dependencies: typer, json, pathlib
- @ai-calls: classify(), upload_file(), validate_metadata(), clear_s3_folders()
- @ai-uses: PathConfig, cluster_map, stub_dir
- @ai-tags: cli, batch, recovery, organization, metadata, upload, S3

⚙️ Meta: 
- @ai-version: 0.4.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Add batch classify/upload/recover/reset commands to CLI 
- @change-summary: Add fault-tolerant CLI workflow support for metadata classification 
- @notes: 
"""

"""
Module: cli/batch_ops.py 

- @ai-path: cli.batch_ops 
- @ai-source-file: combined_cli.py 
- @ai-module: batch_cli 
- @ai-role: cli_batch_controller 
- @ai-entrypoint: classify_all(), recover_failed(), clean_corrupt_meta(), upload_all(), clear_s3(), organize_all() 
- @ai-intent: "Provide CLI commands for classification recovery, file uploads, metadata validation, and S3 cleanup."

🔍 Summary:
This section defines higher-level CLI commands for batch workflows and admin tasks. It enables robust recovery from failed classification runs, validates or deletes corrupt `.meta.json` files, uploads files with parsed text, organizes metadata by cluster labels, and resets specific folders in S3.

📦 Inputs:
- config_file (Path): Path to config file specifying directory layout
- cluster_file (Path): Optional cluster map to use for `organize_all`
- prefixes (str): Comma-separated list of S3 prefixes for `clear_s3`

📤 Outputs:
- Updates `.meta.json` files
- Organizes metadata into subfolders
- Removes invalid metadata
- Uploads raw/parsed files to S3
- Clears targeted S3 prefixes

🔗 Related Modules:
- main_commands → used by classify commands
- combined_utils → upload logic
- storage.s3_utils → used by `clear_s3`
- metadata.schema → used to validate `.meta.json`

🧠 For AI Agents:
- @ai-dependencies: typer, json, pathlib
- @ai-calls: classify(), upload_file(), validate_metadata(), clear_s3_folders()
- @ai-uses: PathConfig, cluster_map, stub_dir
- @ai-tags: cli, batch, recovery, organization, metadata, upload, S3

⚙️ Meta: 
- @ai-version: 0.4.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Add batch classify/upload/recover/reset commands to CLI 
- @change-summary: Add fault-tolerant CLI workflow support for metadata classification 
- @notes: 
"""

from pathlib import Path

import typer

from core.config.config_registry import get_path_config
from core.workflows.main_commands import (classify, pipeline_from_upload,
                                          upload_and_prepare)

app = typer.Typer()

@app.command()
def classify_all(
    chunked: bool = False,
    overwrite: bool = False,
    segmentation: str = "semantic",
):
    """Classify all parsed files in the system."""
    paths = get_path_config()
    for file in sorted(paths.parsed.glob("*.txt")):
        name = file.name
        meta_path = paths.metadata / f"{name}.meta.json"

        if meta_path.exists() and not overwrite:
            print(f"🟡 Skipping {name} (already classified)")
            continue

        try:
            print(f"🔍 Classifying {name}...")
            classify(name, chunked=chunked, segmentation=segmentation)
            print(f"✅ Done: {name}")
        except Exception as e:
            print(f"❌ Error: {name} — {e}")


@app.command()
def upload_all(directory: Path):
    """Upload and parse all files in the given local directory."""
    for file in sorted(directory.glob("*")):
        try:
            print(f"📤 Uploading {file.name}...")
            upload_and_prepare(file)
        except Exception as e:
            print(f"❌ Failed on {file.name}: {e}")


@app.command()
def ingest_all(
    directory: Path,
    chunked: bool = False,
    segmentation: str = "semantic",
):
    """Full pipeline: upload, parse, classify for all files in directory."""
    for file in sorted(directory.glob("*")):
        try:
            print(f"🚀 Ingesting {file.name}...")
            parsed_name = None  # Optional override name
            result = pipeline_from_upload(
                file,
                parsed_name=parsed_name,
                segmentation=segmentation,
            )
            print(f"✅ Metadata: {result.get('summary', '')[:100]}...")
        except Exception as e:
            print(f"❌ Error during ingestion of {file.name}: {e}")
#__________________________________________________________________
# File: classify.py
"""
📦 Module: cli.classification
- @ai-path: cli.classification
- @ai-source-file: combined_cli.py
- @ai-role: CLI Entrypoint
- @ai-intent: "Expose classification and summarization routines as Typer CLI commands."

🔍 Module Summary:
This module provides Typer CLI commands to classify documents via Lambda-based Claude summarization. 
It supports both individual document classification and automated chunked classification for larger inputs. 
It is intended for fast integration into scalable document processing pipelines.

🗂️ Contents:

| Name           | Type     | Purpose                             |
|:---------------|:---------|:------------------------------------|
| classify       | CLI Command | Classify a single document using Claude summarization. |
| classify_large | CLI Command | Classify large documents by chunking and merging results. |

🧠 For AI Agents:
- @ai-dependencies: typer
- @ai-uses: main_commands.classify, main_commands.classify_large
- @ai-tags: cli, classification, summarization, Lambda, chunking

⚙️ Meta:
- @ai-version: 0.3.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add Typer commands for classification
- @change-summary: CLI passthrough to classify and classify_large workflows
- @notes: ""

👤 Human Overview:
    - Context: Classify new documents directly from the command line without needing manual uploads or processing.
    - Change Caution: Large document classification is chunk-based; be aware of chunking limits and recombination logic.
    - Future Hints: Allow manual override of chunk size or prompt template via CLI options.
"""

"""
📦 Module: cli.classification
- @ai-path: cli.classification
- @ai-source-file: combined_cli.py
- @ai-role: CLI Entrypoint
- @ai-intent: "Expose classification and summarization routines as Typer CLI commands."

🔍 Module Summary:
This module provides Typer CLI commands to classify documents via Lambda-based Claude summarization. 
It supports both individual document classification and automated chunked classification for larger inputs. 
It is intended for fast integration into scalable document processing pipelines.

🗂️ Contents:

| Name           | Type     | Purpose                             |
|:---------------|:---------|:------------------------------------|
| classify       | CLI Command | Classify a single document using Claude summarization. |
| classify_large | CLI Command | Classify large documents by chunking and merging results. |

🧠 For AI Agents:
- @ai-dependencies: typer
- @ai-uses: main_commands.classify, main_commands.classify_large
- @ai-tags: cli, classification, summarization, Lambda, chunking

⚙️ Meta:
- @ai-version: 0.3.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add Typer commands for classification
- @change-summary: CLI passthrough to classify and classify_large workflows
- @notes: ""

👤 Human Overview:
    - Context: Classify new documents directly from the command line without needing manual uploads or processing.
    - Change Caution: Large document classification is chunk-based; be aware of chunking limits and recombination logic.
    - Future Hints: Allow manual override of chunk size or prompt template via CLI options.
"""



import typer

from core.workflows.main_commands import classify

app = typer.Typer()

@app.command()
def classify_one(
    name: str,
    chunked: bool = False,
    segmentation: str = "semantic",
):
    """Classify a single document (optionally in chunked mode)."""
    result = classify(name, chunked=chunked, segmentation=segmentation)
    print("✅ Metadata saved.")
    print(result)
#__________________________________________________________________
# File: cluster.py
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
from core.config.config_registry import get_path_config

app = typer.Typer()

@app.command()
def run_all(
    embedding_path: Path = typer.Option(None, help="Path to the rich_doc_embeddings.json file"),
    metadata_dir: Path = typer.Option(None, help="Path to directory with .meta.json files"),
    out_dir: Path = typer.Option(None, help="Directory to save outputs"),
    method: str = "hdbscan",
    model: str = "gpt-4"
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
        model=model
    )
#__________________________________________________________________
# File: embed.py
# No docstring found

# cli/embed.py
from pathlib import Path

import typer

from core.embeddings.embedder import generate_embeddings
from core.config.config_registry import get_path_config

app = typer.Typer()

@app.command()
def all(
    method: str = typer.Option("summary", help="Which text source to embed: parsed, summary, raw, meta"),
    out_path: Path = typer.Option(None, help="Output path for embeddings JSON file")
):
    """
    Generate embeddings from parsed text, summaries, or raw content.
    """    
    paths = get_path_config()
    generate_embeddings(method=method, out_path=out_path, segment_mode=paths.semantic_chunking)#__________________________________________________________________
# File: main.py
# No docstring found

import typer

import cli.batch_ops as batch_ops
import cli.classify as classify
import cli.cluster as cluster
import cli.embed as embed
import cli.pipeline as pipeline
import cli.tokens as tokens
import cli.search as search
import cli.agent as agent

app = typer.Typer()

app.add_typer(classify.app, name="classify")
app.add_typer(batch_ops.app, name="batch")
app.add_typer(embed.app, name="embed")
app.add_typer(cluster.app, name="cluster")
app.add_typer(pipeline.app, name="pipeline")
app.add_typer(tokens.app, name="tokens")
app.add_typer(search.app, name="search")
app.add_typer(agent.app, name="agent")

if __name__ == "__main__":
    app()
#__________________________________________________________________
# File: organize.py
""" 
Module: core_lib.metadata.organize
- @ai-path: core_lib.metadata.organize
- @ai-source-file: core_lib/metadata/organize.py
- @ai-module: organize
- @ai-role: Metadata-based File Organizer
- @ai-entrypoint: false
- @ai-intent: "Organizes files into structured output directories based on metadata-derived categories or optional clustering assignments."

🔍 Summary:
Organizes files into categorized folders based on metadata or provided clustering labels. It loads metadata for the given filename, determines the target category, moves parsed and source files accordingly, and copies associated metadata. Handles missing files with warnings and ensures category folders are created safely.

📦 Inputs:

- name (str): Base filename (without extension) to organize.
- cluster_map (Dict[str, str]): Optional mapping of filename keys to cluster categories.
- meta_dir (Path): Directory containing metadata files (default "metadata/").
- parsed_dir (Path): Directory containing parsed text files (default "parsed/").
- raw_dir (Path): Directory containing raw source files (default "raw/").
- out_dir (Path): Directory where organized files are placed (default "organized/").

📤 Outputs:

- None: The function operates via file system side effects (moving, copying, printing status).

🔗 Related Modules:

- core_lib.metadata.io (for `load_metadata` function)

🧠 For AI Agents:

- @ai-dependencies: pathlib.Path, shutil, json
- @ai-calls: load_metadata, Path.exists, Path.mkdir, Path.replace, shutil.copy
- @ai-uses: Path, shutil
- @ai-tags: organization, clustering, metadata, file management

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: 
- @change-summary: Initial structured documentation
- @notes: 
"""

""" 
Module: core_lib.metadata.organize
- @ai-path: core_lib.metadata.organize
- @ai-source-file: core_lib/metadata/organize.py
- @ai-module: organize
- @ai-role: Metadata-based File Organizer
- @ai-entrypoint: false
- @ai-intent: "Organizes files into structured output directories based on metadata-derived categories or optional clustering assignments."

🔍 Summary:
Organizes files into categorized folders based on metadata or provided clustering labels. It loads metadata for the given filename, determines the target category, moves parsed and source files accordingly, and copies associated metadata. Handles missing files with warnings and ensures category folders are created safely.

📦 Inputs:

- name (str): Base filename (without extension) to organize.
- cluster_map (Dict[str, str]): Optional mapping of filename keys to cluster categories.
- meta_dir (Path): Directory containing metadata files (default "metadata/").
- parsed_dir (Path): Directory containing parsed text files (default "parsed/").
- raw_dir (Path): Directory containing raw source files (default "raw/").
- out_dir (Path): Directory where organized files are placed (default "organized/").

📤 Outputs:

- None: The function operates via file system side effects (moving, copying, printing status).

🔗 Related Modules:

- core_lib.metadata.io (for `load_metadata` function)

🧠 For AI Agents:

- @ai-dependencies: pathlib.Path, shutil, json
- @ai-calls: load_metadata, Path.exists, Path.mkdir, Path.replace, shutil.copy
- @ai-uses: Path, shutil
- @ai-tags: organization, clustering, metadata, file management

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: 
- @change-summary: Initial structured documentation
- @notes: 
"""


import json
import shutil
from pathlib import Path
from typing import Dict

from core.metadata.io import load_metadata


def organize_file(name: str, cluster_map: Dict[str, str] = {}, 
                  meta_dir: Path = Path("metadata"),
                  parsed_dir: Path = Path("parsed"),
                  raw_dir: Path = Path("raw"),
                  out_dir: Path = Path("organized")) -> None:
    """
    Organize a file into a folder based on its metadata or clustering label.

    Args:
        name (str): Parsed filename (without extension).
        cluster_map (Dict[str, str]): Optional cluster labels for doc IDs.
        meta_dir (Path): Directory containing metadata.
        parsed_dir (Path): Directory of parsed .txt files.
        raw_dir (Path): Directory of raw source files.
        out_dir (Path): Output folder for organization.
    """
    meta_path = meta_dir / f"{name}.meta.json"
    if not meta_path.exists():
        print(f"[red]No metadata found for {name}[/red]")
        return

    meta = load_metadata(name, meta_dir)

    name_key = Path(name).stem.lower()
    cluster_label = cluster_map.get(name_key)
    category = cluster_label or meta.get("category", "uncategorized")
    safe_category = category.lower().replace(" ", "_")

    organized_path = out_dir / safe_category
    organized_path.mkdir(parents=True, exist_ok=True)

    parsed_file = Path(meta.get("parsed_file", f"{name_key}.txt")).name
    parsed_src = parsed_dir / parsed_file
    parsed_dst = organized_path / parsed_file
    if parsed_src.exists():
        parsed_src.replace(parsed_dst)
        print(f"[green]Moved parsed file to {parsed_dst}[/green]")
    else:
        print(f"[yellow]Parsed file missing: {parsed_src}[/yellow]")

    source_file = meta.get("source_file")
    if source_file:
        source_name = Path(source_file).name
        source_src = raw_dir / source_name
        source_dst = organized_path / source_name
        if source_src.exists():
            source_src.replace(source_dst)
            print(f"[cyan]Moved source file to {source_dst}[/cyan]")
        else:
            print(f"[yellow]Source file missing: {source_src}[/yellow]")

    shutil.copy(meta_path, organized_path / meta_path.name)
    print(f"[blue]Copied metadata to {organized_path / meta_path.name}[/blue]")
#__________________________________________________________________
# File: pipeline.py
# No docstring found

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
    segmentation: str = "semantic",
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
        overwrite=True,
        segmentation=segmentation,
    )

    # Step 4
    run_all_steps(
        embedding_path=paths.root / "rich_doc_embeddings.json",
        metadata_dir=paths.metadata,
        out_dir=paths.output / "cluster_output",
        method=cluster_method,
        model=model
    )
#__________________________________________________________________
# File: search.py
# No docstring found

import typer

from core.retrieval.retriever import Retriever
from core.utils.logger import get_logger

app = typer.Typer()
logger = get_logger(__name__)


@app.command()
def semantic(query: str, k: int = 5):
    """Return top-k document IDs matching the query."""
    retriever = Retriever()
    logger.info("Running semantic search for: %s", query)
    hits = retriever.query(query, k=k)
    for doc_id, score in hits:
        print(doc_id, f"{score:.3f}")
#__________________________________________________________________
# File: tokens.py
# No docstring found

import json, typer
from pathlib import Path
from core.analysis.token_stats import TokenStats

# 👇  absolute path to the repo-local default
DEFAULT_CFG = Path(__file__).parent.parent / "core" / "config" / "path_config.json"

app = typer.Typer(help="Token-count utilities")

@app.command("summary")
def summary(
    config_file: Path = typer.Option(
        DEFAULT_CFG,                        # <- uses your repo file by default
        exists=True,
        help="path_config.json (root / parsed keys). "
             "Pass a different file to override.",
    ),
    tokenizer: str = typer.Option("tiktoken:gpt-4o-mini"),
    show_hist: bool = False,
):
    """
    Count tokens in every *.txt under  <root>/<parsed>/…  using the paths config.
    """
    cfg = json.loads(config_file.read_text())

    try:
        parsed_dir = Path(cfg["root"]) / cfg["parsed"]
    except KeyError as e:
        typer.echo(f"❌ config missing key {e}", err=True)
        raise typer.Exit(1)

    stats = TokenStats.from_dir(parsed_dir, "*.txt", tokenizer)
    typer.echo(stats.describe())

    if show_hist and stats.counts:
        import numpy as np
        hist, edges = np.histogram(stats.counts, bins=10)
        for h, (lo, hi) in zip(hist, zip(edges[:-1], edges[1:])):
            bar = "█" * int(h / hist.max() * 30)
            typer.echo(f"{int(lo):>6,}–{int(hi):>6,} | {bar} {h}")

@app.command("spite")
def recite():
    from zen_of_spite import spite_verses
    print("\n".join(f"• {v}" for v in spite_verses))#__________________________________________________________________
# File: upload.py
# No docstring found

#__________________________________________________________________
# File: upload_utils.py
"""
📦 Module: core_lib.utils.upload_utils
- @ai-path: core_lib.utils.upload_utils
- @ai-source-file: combined_utils.py
- @ai-role: Uploader Utilities
- @ai-intent: "Upload local files to S3 with parsed versions and register metadata stubs for classification."

🔍 Module Summary:
This module consolidates file upload logic into S3 workflows. It handles uploading raw and parsed documents, 
generates `.stub.json` metadata mappings, and uploads those stubs for downstream classification. 
Resilient against parse errors and supports configurable local/remote paths.

🗂️ Contents:

| Name               | Type     | Purpose                                          |
|:-------------------|:---------|:-------------------------------------------------|
| save_upload_stub    | Function | Save and upload stub metadata linking source and parsed files. |
| upload_file         | Function | Upload a file (raw and parsed) and generate its stub. |

🧠 For AI Agents:
- @ai-dependencies: boto3, pathlib, json
- @ai-uses: extract_text, PathConfig, RemoteConfig, get_s3_client
- @ai-tags: upload, s3, stub-metadata, document-pipeline

⚙️ Meta:
- @ai-version: 0.4.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Move upload_file and stub generation to shared utils
- @change-summary: Consolidated upload flow with robust metadata stub registration
- @notes: ""

👤 Human Overview:
    - Context: Needed when submitting documents to cloud processing pipelines while preserving raw/parsed linkage.
    - Change Caution: If stub uploads fail but document uploads succeed, system integrity may degrade silently.
    - Future Hints: Extend stub format to include upload timestamps, original size, or content hash for better validation.
"""

"""
📦 Module: core_lib.utils.upload_utils
- @ai-path: core_lib.utils.upload_utils
- @ai-source-file: combined_utils.py
- @ai-role: Uploader Utilities
- @ai-intent: "Upload local files to S3 with parsed versions and register metadata stubs for classification."

🔍 Module Summary:
This module consolidates file upload logic into S3 workflows. It handles uploading raw and parsed documents, 
generates `.stub.json` metadata mappings, and uploads those stubs for downstream classification. 
Resilient against parse errors and supports configurable local/remote paths.

🗂️ Contents:

| Name               | Type     | Purpose                                          |
|:-------------------|:---------|:-------------------------------------------------|
| save_upload_stub    | Function | Save and upload stub metadata linking source and parsed files. |
| upload_file         | Function | Upload a file (raw and parsed) and generate its stub. |

🧠 For AI Agents:
- @ai-dependencies: boto3, pathlib, json
- @ai-uses: extract_text, PathConfig, RemoteConfig, get_s3_client
- @ai-tags: upload, s3, stub-metadata, document-pipeline

⚙️ Meta:
- @ai-version: 0.4.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Move upload_file and stub generation to shared utils
- @change-summary: Consolidated upload flow with robust metadata stub registration
- @notes: ""

👤 Human Overview:
    - Context: Needed when submitting documents to cloud processing pipelines while preserving raw/parsed linkage.
    - Change Caution: If stub uploads fail but document uploads succeed, system integrity may degrade silently.
    - Future Hints: Extend stub format to include upload timestamps, original size, or content hash for better validation.
"""


import json
from pathlib import Path

from core.config.path_config import PathConfig
from core.config.remote_config import RemoteConfig
from core.parsing.extract_text import extract_text
from core.storage.aws_clients import get_s3_client


def save_upload_stub(source_file: str, parsed_file: str, ext: str, paths: PathConfig, remote: RemoteConfig):
    s3 = get_s3_client(region=remote.region)

    stub = {
        "source_file": source_file,
        "parsed_file": parsed_file,
        "source_ext": ext
    }

    stub_filename = Path(parsed_file).name + ".stub.json"
    local_path = paths.metadata / stub_filename
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(json.dumps(stub, indent=2), encoding="utf-8")
    print(f"💾 Saved stub locally: {local_path}")

    s3.put_object(
        Bucket=remote.bucket_name,
        Key=f"{remote.prefixes['stub']}{stub_filename}",
        Body=json.dumps(stub, indent=2).encode("utf-8")
    )
    print(f"📤 Uploaded stub to: s3://{remote.bucket_name}/{remote.prefixes['stub']}{stub_filename}")

    return stub


def upload_file(file_name: str, parsed_name: str = None, paths: PathConfig = None, remote: RemoteConfig = None):
    remote = remote or RemoteConfig.from_file(Path(__file__).parent.parent / "config" / "remote_config.json")
    paths = paths or PathConfig.from_file(Path(__file__).parent.parent / "config" / "path_config.json")
    s3 = get_s3_client(region=remote.region)

    file_path = paths.raw / file_name
    original_name = file_path.name
    parsed_name = parsed_name or file_path.stem.replace(" ", "_").replace("-", "_").lower() + ".txt"

    # Upload original to raw/
    s3.upload_file(str(file_path), remote.bucket_name, f"{remote.prefixes['raw']}{original_name}")
    print(f"📤 Uploaded original to: s3://{remote.bucket_name}/{remote.prefixes['raw']}{original_name}")

    try:
        text = extract_text(str(file_path))
    except Exception as e:
        print(f"❌ Failed to parse file {original_name}: {e}")
        return

    s3.put_object(
        Bucket=remote.bucket_name,
        Key=f"{remote.prefixes['parsed']}{parsed_name}",
        Body=text.encode("utf-8")
    )
    print(f"📤 Uploaded parsed version to: s3://{remote.bucket_name}/{remote.prefixes['parsed']}{parsed_name}")

    return save_upload_stub(
        source_file=f"{remote.prefixes['raw']}{original_name}",
        parsed_file=f"{remote.prefixes['parsed']}{parsed_name}",
        ext=file_path.suffix.lower().lstrip("."),
        paths=paths,
        remote=remote
    )