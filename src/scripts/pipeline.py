# scripts/pipeline.py
from pathlib import Path

from core.config.config_registry import get_path_config
from core.embeddings.embedder import generate_embeddings
from core.workflows.main_commands import classify, upload_and_prepare


def run_full_pipeline(
    input_dir: Path,
    chunked: bool = False,
    overwrite: bool = True,
    method: str = "summary"
):
    """
    Full ingestion pipeline:
    1. Upload + parse
    2. Classify
    3. Generate embeddings
    
    Args:
        input_dir (Path): Folder containing source documents
        chunked (bool): Use chunking for classification
        overwrite (bool): Reclassify even if .meta.json exists
        method (str): Text source for embeddings: parsed, summary, raw, meta
    """
    paths = get_path_config()

    print("📤 Uploading and parsing raw files...")
    for file in sorted(input_dir.glob("*")):
        try:
            upload_and_prepare(file)
        except Exception as e:
            print(f"❌ Upload failed: {file.name} — {e}")

    print("🧠 Classifying parsed documents...")
    for file in sorted(paths.parsed.glob("*.txt")):
        name = file.name
        meta_path = paths.metadata / f"{name}.meta.json"
        if meta_path.exists() and not overwrite:
            print(f"⏭️ Skipping {name} (already classified)")
            continue
        try:
            classify(name, chunked=chunked)
            print(f"✅ {name} classified")
        except Exception as e:
            print(f"❌ Classification failed: {name} — {e}")

    print("📊 Generating embeddings and updating vector index...")
    generate_embeddings(method=method)
    print("✅ Pipeline complete.")
