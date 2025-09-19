# scripts/pipeline.py
from pathlib import Path

from core.config.config_registry import get_path_config
from core.config.path_config import PathConfig
from core.embeddings.embedder import generate_embeddings
from core.logger import get_logger
from core.workflows.main_commands import classify, upload_and_prepare


logger = get_logger(__name__)


def run_full_pipeline(
    input_dir: Path,
    chunked: bool = False,
    overwrite: bool = True,
    method: str = "summary",
    segmentation: str = "semantic",
    paths: PathConfig | None = None,
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
    paths = paths or get_path_config()

    logger.info("Uploading and parsing raw files...")
    for file in sorted(input_dir.glob("*")):
        try:
            upload_and_prepare(file, paths=paths)
        except Exception as e:
            logger.error("Upload failed: %s — %s", file.name, e)

    logger.info("Classifying parsed documents...")
    for file in sorted(paths.parsed.glob("*.txt")):
        name = file.name
        meta_path = paths.metadata / f"{name}.meta.json"
        if meta_path.exists() and not overwrite:
            logger.info("Skipping %s (already classified)", name)
            continue
        try:
            classify(name, chunked=chunked, segmentation=segmentation, paths=paths)
            logger.info("%s classified", name)
        except Exception as e:
            logger.error("Classification failed: %s — %s", name, e)

    logger.info("Generating embeddings and updating vector index...")
    generate_embeddings(
        source_dir=paths.parsed if method != "raw" else paths.raw,
        method=method,
        out_path=paths.root / "rich_doc_embeddings.json",
        segment_mode=paths.semantic_chunking,
    )
    logger.info("Pipeline complete.")
