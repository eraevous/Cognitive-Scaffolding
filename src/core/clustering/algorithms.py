# core/clustering/algorithms.py
from typing import Literal

import numpy as np
from sklearn.cluster import SpectralClustering

try:
    import hdbscan  # type: ignore[import]
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    hdbscan = None  # type: ignore[assignment]

try:
    import umap  # type: ignore[import]
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    umap = None  # type: ignore[assignment]


def reduce_dimensions(
    X: np.ndarray, n_neighbors: int = 15, min_dist: float = 0.1, random_state: int = 42
) -> np.ndarray:
    """Apply UMAP to reduce high-dimensional data to 2D with guardrails."""

    if umap is None:  # pragma: no cover - exercised when dependency missing
        raise ModuleNotFoundError(
            "umap-learn is required for dimensionality reduction but is not installed."
        )

    embeddings = np.asarray(X, dtype=float)
    if embeddings.ndim == 0:
        embeddings = embeddings.reshape(0, 0)
    elif embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)

    n_samples = embeddings.shape[0]
    if n_samples == 0:
        return np.empty((0, 2), dtype=float)
    if n_samples == 1:
        return np.zeros((1, 2), dtype=float)

    adjusted_neighbors = max(1, min(n_neighbors, 15, n_samples - 1))
    reducer = umap.UMAP(
        n_neighbors=adjusted_neighbors, min_dist=min_dist, random_state=random_state
    )
    return reducer.fit_transform(embeddings)


def cluster_embeddings(
    X: np.ndarray,
    method: Literal["hdbscan", "spectral"] = "hdbscan",
    min_cluster_size: int = 4,
    n_clusters: int = 24,
    random_state: int = 42,
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
    embeddings = np.asarray(X, dtype=float)
    if embeddings.ndim == 0:
        embeddings = embeddings.reshape(0, 0)
    elif embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)

    n_samples = embeddings.shape[0]
    if n_samples == 0:
        return np.empty((0,), dtype=int)

    if method == "hdbscan":
        if hdbscan is None:  # pragma: no cover - optional dependency
            raise ModuleNotFoundError(
                "hdbscan is required for HDBSCAN clustering but is not installed."
            )

        if n_samples < max(1, min_cluster_size):
            return np.zeros((n_samples,), dtype=int)

        model = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, prediction_data=True)
        return model.fit_predict(embeddings)

    if method == "spectral":
        if n_samples <= 2:
            return np.zeros((n_samples,), dtype=int)

        cluster_count = max(2, min(n_clusters, n_samples - 1))
        model = SpectralClustering(
            n_clusters=cluster_count,
            affinity="nearest_neighbors",
            assign_labels="kmeans",
            random_state=random_state,
        )
        return model.fit_predict(embeddings)

    raise ValueError(f"Unsupported clustering method: {method}")
