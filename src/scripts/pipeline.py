from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from core.configuration.config_registry import get_path_config
from core.configuration.path_config import PathConfig
from core.logger import get_logger
from core.metadata.schema import validate_metadata

logger = get_logger(__name__)

PIPELINE_STAGES = ("upload", "chunk", "classify", "embed", "cluster")
_STAGE_INDEX = {name: idx for idx, name in enumerate(PIPELINE_STAGES)}


def upload_and_prepare(*args, **kwargs):
    from core.workflows.main_commands import upload_and_prepare as _upload

    return _upload(*args, **kwargs)


def classify(*args, **kwargs):
    from core.workflows.main_commands import classify as _classify

    return _classify(*args, **kwargs)


def prepare_chunk_plan(*args, **kwargs):
    from core.workflows.main_commands import prepare_chunk_plan as _prepare

    return _prepare(*args, **kwargs)


def load_chunk_metadata(*args, **kwargs):
    from core.workflows.main_commands import load_chunk_metadata as _load

    return _load(*args, **kwargs)


def generate_embeddings(*args, **kwargs):
    from core.embeddings.embedder import generate_embeddings as _generate

    return _generate(*args, **kwargs)


def _setup_pipeline_logger(paths: PathConfig) -> tuple[logging.Handler, Path]:
    log_dir = paths.root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"pipeline-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.log"

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(handler)
    logger.info("Detailed pipeline log: %s", log_path)
    return handler, log_path


def _teardown_pipeline_logger(handler: logging.Handler) -> None:
    logger.removeHandler(handler)
    handler.close()


def _stage_enabled(start_from: str, stage: str) -> bool:
    return _STAGE_INDEX[start_from] <= _STAGE_INDEX[stage]


def _resolve_input_files(input_dir: Path) -> List[Path]:
    return sorted(path for path in input_dir.rglob("*") if path.is_file())


def _run_upload_stage(paths: PathConfig, input_dir: Path) -> None:
    files_to_upload = _resolve_input_files(input_dir)
    if not files_to_upload:
        logger.info("No new files discovered under %s", input_dir)
        return

    logger.info("Uploading %d document(s) from %s", len(files_to_upload), input_dir)
    for file in files_to_upload:
        try:
            upload_and_prepare(file, paths=paths)
            logger.info("Prepared %s", file.name)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Failed to prepare %s: %s", file, exc, exc_info=True)


def _run_chunk_stage(
    paths: PathConfig,
    *,
    chunked: bool,
    segmentation: str,
) -> Dict[str, List[Dict[str, object]]]:
    chunk_cache: Dict[str, List[Dict[str, object]]] = {}
    parsed_files = sorted(paths.parsed.glob("*.txt"))
    if not parsed_files:
        logger.info("No parsed documents available for chunking")
        return chunk_cache

    segmentation_mode = segmentation.lower()
    for parsed_file in parsed_files:
        name = parsed_file.name
        try:
            doc_type, records = prepare_chunk_plan(
                name,
                chunked=chunked,
                segmentation="semantic"
                if segmentation_mode == "semantic"
                else "paragraph",
                paths=paths,
            )
            chunk_cache[name] = records
            strategy = records[0]["strategy"] if records else "single"
            logger.info(
                "Chunked %s (%s) into %d %s segment(s)",
                name,
                doc_type,
                len(records),
                strategy,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Chunking failed for %s: %s", name, exc, exc_info=True)
    return chunk_cache


def _load_chunk_cache(paths: PathConfig) -> Dict[str, List[Dict[str, object]]]:
    cache: Dict[str, List[Dict[str, object]]] = {}
    for parsed_file in sorted(paths.parsed.glob("*.txt")):
        name = parsed_file.name
        records = load_chunk_metadata(name, paths=paths)
        if records:
            cache[name] = records
        else:
            logger.warning("Chunk metadata missing for %s; will regenerate on demand", name)
    return cache


def _run_classification_stage(
    paths: PathConfig,
    *,
    overwrite: bool,
    chunked: bool,
    segmentation: str,
    chunk_cache: Dict[str, List[Dict[str, object]]],
) -> None:
    parsed_files = sorted(paths.parsed.glob("*.txt"))
    if not parsed_files:
        logger.info("No parsed documents available for classification")
        return

    segmentation_mode = segmentation.lower()
    for parsed_file in parsed_files:
        name = parsed_file.name
        meta_path = paths.metadata / f"{name}.meta.json"
        if meta_path.exists() and not overwrite:
            logger.info("Skipping classification for %s (metadata exists)", name)
            continue

        try:
            records = chunk_cache.get(name)
            classify(
                name,
                chunked=chunked,
                segmentation="semantic"
                if segmentation_mode == "semantic"
                else "paragraph",
                paths=paths,
                chunk_records=records,
            )
            logger.info(
                "Classified %s using %d chunk(s)",
                name,
                len(records) if records else 1,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("Classification failed for %s: %s", name, exc, exc_info=True)


def _run_embedding_stage(paths: PathConfig, method: str) -> None:
    logger.info("Generating embeddings using %s content", method)
    try:
        generate_embeddings(
            source_dir=paths.parsed if method != "raw" else paths.raw,
            method=method,
            out_path=paths.root / "rich_doc_embeddings.json",
            segment_mode=paths.semantic_chunking,
        )
        logger.info("Embeddings stored at %s", paths.root / "rich_doc_embeddings.json")
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Embedding generation failed: %s", exc, exc_info=True)
        raise


def _run_cluster_stage(
    paths: PathConfig,
    *,
    cluster_method: str,
    label_model: str,
) -> None:
    embedding_path = paths.root / "rich_doc_embeddings.json"
    if not embedding_path.exists():
        logger.warning(
            "Embedding file %s is missing; skipping clustering stage", embedding_path
        )
        return

    try:
        from core.embeddings.loader import load_embeddings
        from core.clustering.algorithms import cluster_embeddings, reduce_dimensions
        from core.clustering.labeling import label_clusters
        from core.clustering.export import export_cluster_data
    except ModuleNotFoundError as exc:  # pragma: no cover - optional deps
        logger.warning("Clustering dependencies unavailable: %s", exc)
        return

    try:
        doc_ids, matrix = load_embeddings(embedding_path)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Failed to load embeddings: %s", exc, exc_info=True)
        return

    if not doc_ids:
        logger.info("Embedding store is empty; skipping clustering stage")
        return

    try:
        coords = reduce_dimensions(matrix)
        labels = cluster_embeddings(matrix, method=cluster_method)
        label_list = [int(label) for label in labels.tolist()]
    except ModuleNotFoundError as exc:  # pragma: no cover - optional deps
        logger.warning("Clustering dependency missing: %s", exc)
        return
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Clustering computation failed: %s", exc, exc_info=True)
        return

    try:
        label_map = label_clusters(doc_ids, label_list, paths.metadata, model=label_model, preview=False)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Cluster labeling failed: %s", exc, exc_info=True)
        label_map = {f"cluster_{label}": f"cluster_{label}" for label in set(label_list) if label != -1}

    try:
        export_cluster_data(
            doc_ids,
            coords.tolist(),
            label_list,
            label_map,
            paths.output / "cluster_output",
            paths.metadata,
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Failed to export clustering artefacts: %s", exc, exc_info=True)

    _update_metadata_with_clusters(doc_ids, label_list, label_map, paths, cluster_method)
    logger.info("Clustering stage complete (%d document(s))", len(doc_ids))


def _update_metadata_with_clusters(
    doc_ids: List[str],
    labels: List[int],
    label_map: Dict[str, str],
    paths: PathConfig,
    method: str,
) -> None:
    for doc_id, label in zip(doc_ids, labels):
        meta_path = paths.metadata / f"{doc_id}.meta.json"
        if not meta_path.exists():
            continue

        try:
            metadata = json.loads(meta_path.read_text("utf-8"))
        except Exception:  # pragma: no cover - defensive logging
            logger.warning("Unable to load metadata for %s to attach cluster info", doc_id)
            continue

        if label == -1:
            cluster_info = {"id": "noise", "label": "Noise", "method": method}
        else:
            cluster_id = f"cluster_{label}"
            cluster_info = {
                "id": cluster_id,
                "label": label_map.get(cluster_id, cluster_id),
                "method": method,
            }

        metadata["cluster"] = cluster_info
        try:
            validate_metadata(metadata)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Cluster update for %s failed schema validation: %s", doc_id, exc)
        meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def run_pipeline(
    input_dir: Path,
    chunked: bool = False,
    overwrite: bool = True,
    method: str = "summary",
    segmentation: str = "semantic",
    paths: PathConfig | None = None,
    start_from: str = "upload",
    cluster_method: str = "hdbscan",
    label_model: str = "gpt-5-nano",
) -> None:
    """Run the full document processing pipeline.

    Args:
        input_dir: Folder containing source documents.
        chunked: Force chunking even if under context window.
        overwrite: Reclassify documents that already have metadata.
        method: Embedding source text (parsed, summary, raw, meta).
        segmentation: Chunking strategy (semantic or paragraph).
        start_from: Pipeline stage to start at when resuming work.
        cluster_method: Clustering algorithm (hdbscan or spectral).
        label_model: OpenAI model used for cluster labeling.
    """

    paths = paths or get_path_config()
    start_key = start_from.lower()
    if start_key not in _STAGE_INDEX:
        raise ValueError(
            f"Unknown pipeline stage '{start_from}'. Valid stages: {', '.join(PIPELINE_STAGES)}"
        )

    handler, _ = _setup_pipeline_logger(paths)
    chunk_cache: Dict[str, List[Dict[str, object]]] = {}
    try:
        if _stage_enabled(start_key, "upload"):
            _run_upload_stage(paths, input_dir)
        else:
            logger.info("Skipping upload stage (start_from=%s)", start_from)

        if _stage_enabled(start_key, "chunk"):
            chunk_cache = _run_chunk_stage(
                paths,
                chunked=chunked,
                segmentation=segmentation,
            )
        else:
            logger.info("Skipping chunk stage (start_from=%s)", start_from)
            chunk_cache = _load_chunk_cache(paths)

        if _stage_enabled(start_key, "classify"):
            _run_classification_stage(
                paths,
                overwrite=overwrite,
                chunked=chunked,
                segmentation=segmentation,
                chunk_cache=chunk_cache,
            )
        else:
            logger.info("Skipping classification stage (start_from=%s)", start_from)

        if _stage_enabled(start_key, "embed"):
            _run_embedding_stage(paths, method)
        else:
            logger.info("Skipping embedding stage (start_from=%s)", start_from)

        if _stage_enabled(start_key, "cluster"):
            _run_cluster_stage(
                paths,
                cluster_method=cluster_method,
                label_model=label_model,
            )
        else:
            logger.info("Skipping clustering stage (start_from=%s)", start_from)
    finally:
        _teardown_pipeline_logger(handler)

    logger.info("Pipeline complete.")
