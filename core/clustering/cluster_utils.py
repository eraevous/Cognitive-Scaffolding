"""
Module: core_lib.clustering.cluster_utils 
- @ai-path: core_lib.clustering.cluster_utils 
- @ai-source-file: combined_clustering.py 
- @ai-module: cluster_utils 
- @ai-role: mapping_normalizer 
- @ai-entrypoint: flatten_cluster_map() 
- @ai-intent: "Convert clustered document groupings into a flat doc_id → label dictionary."

🔍 Summary:
This function transforms a hierarchical cluster mapping (cluster ID → list of document IDs) into a flat dictionary mapping each document ID directly to its assigned human-readable label. It uses a label map to lookup the cluster name.

📦 Inputs:
- cluster_map (Dict[str, List[str]]): Map from cluster IDs to lists of document IDs
- label_map (Dict[str, str]): Map from cluster IDs to cluster labels

📤 Outputs:
- Dict[str, str]: Flat document ID to label mapping

🔗 Related Modules:
- gpt_labeling → produces the label_map
- cluster_viz → optionally uses flattened doc_id → label for coloring

🧠 For AI Agents:
- @ai-dependencies: None
- @ai-calls: dict.items(), dict.get(), str.lower()
- @ai-uses: cluster_map, label_map
- @ai-tags: flattening, mapping, cluster-to-label, document-indexing

⚙️ Meta: 
- @ai-version: 0.1.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Flatten cluster-to-doc mappings after labeling @change-summary: Create simple document lookup for downstream uses 
- @notes:
"""

# core/clustering/utils.py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List


def cluster_dict(labels: List[int], doc_ids: List[str]) -> Dict[str, List[str]]:
    """
    Create cluster_id → list of doc_ids mapping.
    """
    out = {}
    for label, doc in zip(labels, doc_ids):
        if label == -1:
            continue
        out.setdefault(f"cluster_{label}", []).append(doc)
    return out


def flatten_cluster_map(
    cluster_map: Dict[str, List[str]],
    label_map: Dict[str, str]
) -> Dict[str, str]:
    """
    Flatten cluster ID mappings and attach labels per document.
    """
    flat = {}
    for cluster_id, docs in cluster_map.items():
        label = label_map.get(cluster_id, cluster_id)
        for doc in docs:
            flat[doc.lower()] = label
    return flat


def plot_umap_clusters(
    df: pd.DataFrame,
    label_col: str,
    title: str,
    out_file: Path
):
    """
    Generate and save a UMAP cluster plot.
    """
    plt.figure(figsize=(14, 10))
    labels = df[label_col].unique()
    colors = plt.get_cmap("tab20")(np.linspace(0, 1, len(labels)))

    for i, label in enumerate(labels):
        sub = df[df[label_col] == label]
        plt.scatter(sub["x"], sub["y"], label=label, alpha=0.7, s=50, color=colors[i % len(colors)])

    plt.legend(loc='best', fontsize=9)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()
