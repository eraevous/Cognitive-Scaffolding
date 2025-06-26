# scripts/clustering_steps.py
from pathlib import Path
from typing import List

from core.clustering.algorithms import cluster_embeddings, reduce_dimensions
from core.clustering.cluster_utils import cluster_dict
from core.clustering.export import export_cluster_data
from core.clustering.labeling import label_clusters
from core.embeddings.loader import load_embeddings


def run_dimensionality_reduction(embedding_path: Path):
    """Reduce document embeddings to 2D coordinates using UMAP."""
    doc_ids, X = load_embeddings(embedding_path)
    coords = reduce_dimensions(X)
    return doc_ids, X, coords


def run_clustering(X, method: str = "hdbscan") -> List[int]:
    """Run clustering algorithm (HDBSCAN or Spectral)."""
    return cluster_embeddings(X, method=method)


def run_labeling(doc_ids: List[str], labels: List[int], metadata_dir: Path, model: str = "gpt-4") -> dict:
    """Generate GPT cluster labels."""
    return label_clusters(doc_ids, labels, metadata_dir, model=model)


def run_export(
    doc_ids: List[str],
    coords: List[List[float]],
    labels: List[int],
    label_map: dict,
    out_dir: Path,
    metadata_dir: Path = None
):
    """Export results to CSV, PNG, and label map."""
    export_cluster_data(doc_ids, coords, labels, label_map, out_dir, metadata_dir)

def run_all_steps(
    embedding_path: Path,
    metadata_dir: Path,
    out_dir: Path,
    method: str = "hdbscan",
    model: str = "gpt-4"
):
    """Run the full clustering flow with modular components."""
    doc_ids, X, coords = run_dimensionality_reduction(embedding_path)
    labels = run_clustering(X, method=method)
    label_map = run_labeling(doc_ids, labels, metadata_dir, model=model)
    run_export(doc_ids, coords, labels, label_map, out_dir, metadata_dir)
