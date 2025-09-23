# scripts/pipeline.py
from pathlib import Path

from core.config.config_registry import get_path_config
from core.config.path_config import PathConfig
from core.logger import get_logger

logger = get_logger(__name__)


def upload_and_prepare(*args, **kwargs):
    from core.workflows.main_commands import upload_and_prepare as _upload

    return _upload(*args, **kwargs)


def classify(*args, **kwargs):
    from core.workflows.main_commands import classify as _classify

    return _classify(*args, **kwargs)


def generate_embeddings(*args, **kwargs):
    from core.embeddings.embedder import generate_embeddings as _generate

    return _generate(*args, **kwargs)


def upload_file(file: Path, paths: PathConfig) -> None:
    """Upload and prepare a single file for downstream processing."""
    try:
        upload_and_prepare(file, paths=paths)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Upload failed: %s — %s", file.name, exc)


def classify_document(
    file: Path,
    *,
    chunked: bool,
    segmentation: str,
    overwrite: bool,
    paths: PathConfig,
) -> None:
    """Classify a parsed document if classification is required."""
    name = file.name
    meta_path = paths.metadata / f"{name}.meta.json"
    if meta_path.exists() and not overwrite:
        logger.info("Skipping %s (already classified)", name)
        return

    try:
        classify(name, chunked=chunked, segmentation=segmentation, paths=paths)
        logger.info("%s classified", name)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Classification failed: %s — %s", name, exc)


def embed_document(*, method: str, paths: PathConfig) -> None:
    """Generate embeddings for the processed corpus."""
    logger.info("Generating embeddings and updating vector index...")
    generate_embeddings(
        source_dir=paths.parsed if method != "raw" else paths.raw,
        method=method,
        out_path=paths.root / "rich_doc_embeddings.json",
        segment_mode=paths.semantic_chunking,
    )


def run_pipeline(
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
        upload_file(file, paths=paths)

    logger.info("Classifying parsed documents...")
    for file in sorted(paths.parsed.glob("*.txt")):
        classify_document(
            file,
            chunked=chunked,
            segmentation=segmentation,
            overwrite=overwrite,
            paths=paths,
        )

    embed_document(method=method, paths=paths)
    logger.info("Pipeline complete.")
