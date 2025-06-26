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
def classify_all(chunked: bool = False, overwrite: bool = False):
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
            classify(name, chunked=chunked)
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
def ingest_all(directory: Path, chunked: bool = False):
    """Full pipeline: upload, parse, classify for all files in directory."""
    for file in sorted(directory.glob("*")):
        try:
            print(f"🚀 Ingesting {file.name}...")
            parsed_name = None  # Optional override name
            result = pipeline_from_upload(file, parsed_name=parsed_name)
            print(f"✅ Metadata: {result.get('summary', '')[:100]}...")
        except Exception as e:
            print(f"❌ Error during ingestion of {file.name}: {e}")
