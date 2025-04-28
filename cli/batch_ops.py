"""
📦 Module: cli.batch_ops
- @ai-path: cli.batch_ops
- @ai-source-file: combined_cli.py
- @ai-role: CLI Batch Controller
- @ai-intent: "Provide CLI commands for classification recovery, file uploads, metadata validation, and S3 cleanup."

🔍 Module Summary:
This module defines high-level batch workflow commands for document metadata pipelines. It supports recovery 
of failed classifications, validation and cleaning of corrupt metadata, organizing metadata by cluster, 
uploading document files, and clearing S3 folders via Typer CLI commands.

🗂️ Contents:

| Name                  | Type     | Purpose                                          |
|:----------------------|:---------|:-------------------------------------------------|
| organize_all          | CLI Command | Organize documents into subfolders by cluster.     |
| classify_all          | CLI Command | Batch classify all unprocessed documents.         |
| recover_failed        | CLI Command | Retry classification for stubbed but failed files.|
| clean_corrupt_meta    | CLI Command | Remove invalid `.meta.json` metadata files.       |
| upload_all            | CLI Command | Upload raw and parsed files to S3 with stubs.     |
| clear_s3              | CLI Command | Clear specified folders in S3 bucket.             |

🧠 For AI Agents:
- @ai-dependencies: typer, json, pathlib
- @ai-uses: classify, upload_file, validate_metadata, clear_s3_folders
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
- @notes: ""

👤 Human Overview:
    - Context: Manage large-scale metadata workflows with fault-tolerance, from classification to cloud upload.
    - Change Caution: Ensure that directory paths and S3 prefixes match expectations to avoid accidental deletion.
    - Future Hints: Add dry-run modes for organize, classify, and clear_s3 for safer batch operations.
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
