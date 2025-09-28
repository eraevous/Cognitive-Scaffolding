"""
Module: core_lib.clustering.cluster_runner 
- @ai-path: core_lib.clustering.cluster_runner 
- @ai-source-file: combined_clustering.py 
- @ai-module: cluster_runner 
- @ai-role: clustering_engine 
- @ai-entrypoint: cluster_embeddings() 
- @ai-intent: "Run dimensionality reduction and clustering over document embeddings."

🔍 Summary:
This function runs dimensionality reduction (UMAP) on a set of document embeddings, followed by two clustering methods: HDBSCAN for density-based groups and Spectral Clustering for contrastive segmentation. It returns the 2D layout and labels for downstream visualization and label generation.

📦 Inputs:
- X (np.ndarray): High-dimensional document embeddings
- umap_config (dict): UMAP configuration (e.g., n_neighbors, min_dist)
- n_spectral_clusters (int): Number of clusters for Spectral Clustering

📤 Outputs:
- Tuple[np.ndarray, np.ndarray, np.ndarray]:
    - umap_coords: 2D coordinates after UMAP
    - labels_hdb: Cluster labels from HDBSCAN
    - labels_spec: Cluster labels from Spectral Clustering

🔗 Related Modules:
- run_clustering_pipeline → wraps this as part of full CLI pipeline
- cluster_viz → visualizes returned umap_coords and labels
- gpt_labeling → maps labels to GPT-based descriptors

🧠 For AI Agents:
- @ai-dependencies: hdbscan, umap-learn, sklearn.cluster
- @ai-calls: UMAP.fit_transform, HDBSCAN.fit, SpectralClustering.fit
- @ai-uses: X, umap_config, n_spectral_clusters
- @ai-tags: clustering, embeddings, umap, hdbscan, spectral

⚙️ Meta: 
- @ai-version: 0.3.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Add UMAP + dual clustering over embeddings 
- @change-summary: Define embedding-to-labels transformation for clustering pipeline 
- @notes: 
"""

from typing import Tuple

import hdbscan
import numpy as np
import umap
from sklearn.cluster import SpectralClustering


def cluster_embeddings(
    X: np.ndarray,
    umap_config: dict = {"random_state": 42},
    n_spectral_clusters: int = 24,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Apply UMAP, HDBSCAN, and Spectral clustering to embedding vectors.

    Args:
        X (np.ndarray): Input embedding matrix
        umap_config (dict): Keyword args for UMAP constructor
        n_spectral_clusters (int): Number of clusters for SpectralClustering

    Returns:
        Tuple of (umap_coords, hdb_labels, spectral_labels)
    """
    reducer = umap.UMAP(**umap_config)
    umap_coords = reducer.fit_transform(X)

    hdb = hdbscan.HDBSCAN(min_cluster_size=4, prediction_data=True).fit(X)
    labels_hdb = hdb.labels_

    spec = SpectralClustering(
        n_clusters=n_spectral_clusters,
        affinity="nearest_neighbors",
        assign_labels="kmeans",
        random_state=42,
    ).fit(X)
    labels_spec = spec.labels_

    return umap_coords, labels_hdb, labels_spec
