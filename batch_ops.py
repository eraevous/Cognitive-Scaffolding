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

import typer
from pathlib import Path
import json
from core_lib.metadata.organize import organize_file
from core_lib.metadata.schema import validate_metadata
from core_lib.workflows.main_commands import classify
from core_lib.storage.s3_utils import save_metadata_s3, clear_s3_folders
from config import BUCKET_NAME, META_PREFIX
from core_lib.storage.upload_utils import upload_file

from core_lib.config.path_config import PathConfig

def load_paths(config_file: Path = None) -> PathConfig:
    if config_file and config_file.exists():
        return PathConfig.from_file(config_file)
    return PathConfig()

app = typer.Typer()

@app.command()
def organize_all(
    cluster_file: Path = typer.Option(None, help="Optional cluster assignment JSON")
, config_file: Path = typer.Option(None, help="Optional path config file")):
    """Organize all documents using their metadata (and optional cluster map)."""
    cluster_map = {}
    if cluster_file and cluster_file.exists():
        with open(cluster_file, "r") as f:
            cluster_map = json.load(f)

    paths = load_paths(config_file)
    meta_dir = paths.metadata
    for meta_path in meta_dir.glob("*.meta.json"):
        doc_id = meta_path.stem.replace(".meta", "")
        organize_file(doc_id, cluster_map)
    print("✅ All files organized.")

@app.command()
def classify_all(config_file: Path = typer.Option(None, help="Optional path config file")):
    """Classify all parsed documents in `parsed/` without `.meta.json` output yet."""
    paths = load_paths(config_file)
    parsed_dir = paths.parsed
    meta_dir = paths.metadata
    paths = load_paths(config_file)
    meta_dir = paths.metadata
    done = {f.stem.replace(".meta", "") for f in meta_dir.glob("*.meta.json")}

    for txt_file in parsed_dir.glob("*.txt"):
        name = txt_file.name
        if name in done:
            continue
        try:
            classify(name)
        except Exception as e:
            print(f"❌ Failed to classify {name}: {e}")

    print("✅ All unclassified files processed.")

@app.command()
def recover_failed(config_file: Path = typer.Option(None, help="Optional path config file")):
    """Re-attempt classification of files with stubs but no valid metadata."""
    paths = load_paths(config_file)
    stub_dir = paths.metadata
    for stub_file in stub_dir.glob("*.stub.json"):
        name = stub_file.stem.replace(".stub", "")
        meta_file = stub_dir / f"{name}.meta.json"
        if not meta_file.exists():
            print(f"🔁 Retrying: {name}")
            try:
                classify(name)
            except Exception as e:
                print(f"❌ Still failed on {name}: {e}")

    print("🔄 Recovery attempt complete.")

@app.command()
def clean_corrupt_meta(config_file: Path = typer.Option(None, help="Optional path config file")):
    """Remove `.meta.json` files that fail schema validation."""
    meta_dir = Path("metadata")
    for meta_file in meta_dir.glob("*.meta.json"):
        try:
            data = json.loads(meta_file.read_text("utf-8"))
            validate_metadata(data)
        except Exception as e:
            print(f"🧹 Removing {meta_file.name}: {e}")
            meta_file.unlink()

    print("🧼 Corrupt metadata cleaned.")

@app.command()
def upload_all(config_file: Path = typer.Option(None, help="Optional path config file")):
    """Upload all raw files and generate parsed + stub metadata."""
    paths = load_paths(config_file)
    for file in paths.raw.glob("*.*"):
        try:
            upload_file(str(file))
        except Exception as e:
            print(f"❌ Failed to upload {file.name}: {e}")

    print("✅ Upload complete.")


@app.command()
def clear_s3(prefixes: str = typer.Option("raw/,parsed/,metadata/", help="Comma-separated S3 prefixes to clear")):
    """Delete all objects under given S3 prefixes."""
    prefix_list = [p.strip() for p in prefixes.split(",") if p.strip()]
    clear_s3_folders(prefix_list)
    print("✅ S3 folders cleared.")
