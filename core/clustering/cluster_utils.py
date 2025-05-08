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

from typing import Dict, List


def flatten_cluster_map(
    cluster_map: Dict[str, List[str]],
    label_map: Dict[str, str]
) -> Dict[str, str]:
    """
    Flatten cluster ID mappings and attach labels per document.

    Args:
        cluster_map (Dict[str, List[str]]): cluster_id → [doc_ids]
        label_map (Dict[str, str]): cluster_id → cluster label

    Returns:
        Dict[str, str]: doc_id → assigned label
    """
    flat = {}
    for cluster_id, docs in cluster_map.items():
        label = label_map.get(cluster_id, cluster_id)
        for doc in docs:
            flat[doc.lower()] = label
    return flat