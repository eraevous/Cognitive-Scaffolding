# tests/test_clustering_from_embeddings.py
from pathlib import Path

print("importing pathlib")
from core.config.config_registry import get_path_config

print("importing config_registry")
from core.clustering.clustering_steps import (run_clustering,
                                              run_dimensionality_reduction,
                                              run_export, run_labeling)

print("importing clustering_steps")


def test_clustering_from_embeddings():
    print("🧪 Testing clustering from existing embeddings...")
    paths = get_path_config()
    embedding_path = paths.root / "rich_doc_embeddings.json"
    metadata_dir = paths.metadata
    out_dir = paths.output / "test_output"

    print(f"Using {embedding_path} for testing.")
    print(f"Using {metadata_dir} for testing.")
    paths = get_path_config()
    embedding_path = paths.root / "rich_doc_embeddings.json"
    metadata_dir = paths.metadata
    out_dir = paths.output / "test_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    doc_ids, X, coords = run_dimensionality_reduction(embedding_path)
    labels = run_clustering(X, method="spectral")
    label_map = run_labeling(doc_ids, labels, metadata_dir)
    run_export(doc_ids, coords, labels, label_map, out_dir, metadata_dir)

    assert out_dir.joinpath("cluster_map.json").exists()
    assert out_dir.joinpath("cluster_labels.json").exists()
    assert out_dir.joinpath("cluster_assignments.csv").exists()
    assert out_dir.joinpath("cluster_summary.csv").exists()
    assert out_dir.joinpath("umap_plot.png").exists()
    print("✅ Clustering from existing embeddings succeeded.")


if __name__ == "__main__":
    test_clustering_from_embeddings()