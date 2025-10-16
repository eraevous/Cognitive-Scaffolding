"""Entry points for the ingestion pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from core.configuration import config_registry
from core.configuration.path_config import PathConfig
from core.embeddings.embedder import generate_embeddings
from core.logger import get_logger
from core.workflows.main_commands import classify, upload_and_prepare

logger = get_logger(__name__)


def _iter_files(directory: Path) -> Iterable[Path]:
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            yield path


def run_pipeline(
    *,
    input_dir: Path,
    chunked: bool = False,
    overwrite: bool = False,
    method: str = "summary",
    segmentation: str = "semantic",
    paths: PathConfig | None = None,
) -> None:
    paths = paths or config_registry.get_path_config()
    logger.info("Processing documents from %s", input_dir)

    classified = False
    for raw_file in _iter_files(Path(input_dir)):
        parsed_path = upload_and_prepare(raw_file, paths=paths)
        parsed_name = raw_file.with_suffix('.txt').name
        meta_path = Path(paths.metadata) / f"{parsed_name}.meta.json"
        if not overwrite and meta_path.exists():
            logger.info("Skipping %s; metadata already exists", raw_file)
            continue
        if not classified:
            classify(parsed_name, chunked=chunked, segmentation=segmentation, paths=paths)
            classified = True

    generate_embeddings(
        source_dir=Path(paths.parsed),
        method=method,
        out_path=Path(paths.root) / "rich_doc_embeddings.json",
        segment_mode=bool(paths.semantic_chunking),
    )


def run_all_steps(**kwargs) -> None:
    run_pipeline(**kwargs)


__all__ = ["run_pipeline", "run_all_steps"]
