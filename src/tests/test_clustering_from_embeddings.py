import pytest

from core.clustering.clustering_steps import (
    run_clustering,
    run_dimensionality_reduction,
    run_export,
    run_labeling,
)
from core.config.config_registry import get_path_config
from core.config.path_config import PathConfig
from core.logger import get_logger
from core.workflows.main_commands import classify

logger = get_logger(__name__)

pytest.skip("Skipping heavy clustering test", allow_module_level=True)


def test_clustering_from_embeddings(tmp_path, monkeypatch):
    logger.info("Testing clustering from existing embeddings...")
    paths = get_path_config()
    embedding_path = paths.root / "rich_doc_embeddings.json"
    metadata_dir = paths.metadata
    out_dir = paths.output / "test_output"

    if not embedding_path.exists() or embedding_path.stat().st_size == 0:
        pytest.skip("embedding file missing")

    logger.info("Using %s for testing.", embedding_path)
    logger.info("Using %s for testing.", metadata_dir)
    paths = get_path_config()
    embedding_path = paths.root / "rich_doc_embeddings.json"
    metadata_dir = paths.metadata
    out_dir = paths.output / "test_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    doc_ids, X, coords = run_dimensionality_reduction(embedding_path)
    labels = run_clustering(X, method="spectral")
    label_map = run_labeling(doc_ids, labels, metadata_dir)
    run_export(doc_ids, coords, labels, label_map, out_dir, metadata_dir)

    # exercise classification path on a minimal sample
    pc = PathConfig(root=tmp_path)
    pc.parsed.mkdir(parents=True, exist_ok=True)
    pc.metadata.mkdir(parents=True, exist_ok=True)
    sample_file = pc.parsed / "sample.txt"
    sample_file.write_text("Cats purr. " * 20 + "Dogs bark. " * 20)

    monkeypatch.setattr("core.config.config_registry.get_path_config", lambda: pc)
    monkeypatch.setattr(
        "core.parsing.semantic_chunk.embed_text",
        lambda text, model="text-embedding-3-small": [0.0],
    )
    monkeypatch.setattr(
        "core.workflows.main_commands.summarize_text",
        lambda text, doc_type="standard": {
            "summary": text[:10],
            "topics": ["x"],
            "tags": [],
            "themes": [],
            "priority": 1,
            "tone": "info",
            "stage": "draft",
            "depth": "low",
            "category": doc_type,
        },
    )
    metadata = classify(sample_file.name, chunked=True)
    assert isinstance(metadata, dict)
    assert pc.metadata.joinpath(f"{sample_file.name}.meta.json").exists()

    assert out_dir.joinpath("cluster_map.json").exists()
    assert out_dir.joinpath("cluster_labels.json").exists()
    assert out_dir.joinpath("cluster_assignments.csv").exists()
    assert out_dir.joinpath("cluster_summary.csv").exists()
    assert out_dir.joinpath("umap_plot.png").exists()
    logger.info("Clustering from existing embeddings succeeded.")


if __name__ == "__main__":
    test_clustering_from_embeddings()
