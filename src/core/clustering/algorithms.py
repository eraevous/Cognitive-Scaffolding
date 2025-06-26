# core/clustering/algorithms.py
from typing import Literal

import hdbscan
import numpy as np
import umap
from sklearn.cluster import SpectralClustering


def reduce_dimensions(X: np.ndarray, n_neighbors: int = 15, min_dist: float = 0.1, random_state: int = 42) -> np.ndarray:
    """
    Apply UMAP to reduce high-dimensional data to 2D.
    """
    reducer = umap.UMAP(n_neighbors=n_neighbors, min_dist=min_dist, random_state=random_state)
    return reducer.fit_transform(X)


def cluster_embeddings(
    X: np.ndarray,
    method: Literal["hdbscan", "spectral"] = "hdbscan",
    min_cluster_size: int = 4,
    n_clusters: int = 24,
    random_state: int = 42
) -> np.ndarray:
    """
    Cluster high-dimensional embeddings using specified algorithm.

    Args:
        X (np.ndarray): Input embedding matrix
        method (str): Clustering method ("hdbscan" or "spectral")
        min_cluster_size (int): Minimum size for HDBSCAN clusters
        n_clusters (int): Cluster count for spectral
        random_state (int): Seed for reproducibility

    Returns:
        np.ndarray: Cluster labels
    """
    if method == "hdbscan":
        model = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, prediction_data=True)
        return model.fit_predict(X)
    elif method == "spectral":
        model = SpectralClustering(
            n_clusters=n_clusters,
            affinity="nearest_neighbors",
            assign_labels="kmeans",
            random_state=random_state
        )
        return model.fit_predict(X)
    else:
        raise ValueError(f"Unsupported clustering method: {method}")
