"""
Module: core_lib.clustering.exporter 
- @ai-path: core_lib.clustering.exporter 
- @ai-source-file: export.py 
- @ai-module: clustering_export 
- @ai-role: result_exporter 
- @ai-entrypoint: export_clusters_and_summary() 
- @ai-intent: "Save clustered document assignments and metadata summaries to disk for analysis and downstream processing."

🔍 Summary:
This function saves the results of clustering to disk. It serializes cluster mappings and document label assignments to JSON files, and builds a metadata-enriched CSV summary file that combines basic document metadata with cluster label assignments.

📦 Inputs:
- cluster_maps (Dict[str, Any]): Mapping of cluster algorithm names to cluster results
- assignments (Dict[str, str]): Flat document ID → cluster label mapping
- umap_df (pd.DataFrame): UMAP 2D projection with document IDs
- metadata_dir (Path): Directory containing `.meta.json` metadata files
- out_dir (Path): Output directory where files are saved

📤 Outputs:
- cluster_map_<method>.json: Cluster maps by method (HDBSCAN, Spectral, etc.)
- cluster_assignments.json: Flattened doc ID to cluster label mapping
- cluster_summary.csv: CSV with doc_id, summary, topics, tags, themes, cluster label

🔗 Related Modules:
- plotting.py → generates UMAP visualization
- labeling.py → generates cluster labels
- schema.py → validates metadata structure (upstream)

🧠 For AI Agents:
- @ai-dependencies: pandas, json, pathlib
- @ai-calls: json.dump(), pd.DataFrame.to_csv()
- @ai-uses: cluster_maps, assignments, umap_df
- @ai-tags: export, clustering, metadata, csv-generation, json-saving

⚙️ Meta: 
- @ai-version: 0.2.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Save clustering outputs and build metadata summary CSV 
- @change-summary: Persist clustered outputs for downstream use and exploration 
- @notes:

🚧 Future Enhancements:
- [ ] Integrate lexical_analysis fields (e.g., top_terms) into summary CSV
- [ ] Support multiple cluster label columns in CSV (hdbscan vs spectral vs other)
- [ ] Optionally validate metadata files against schema before ingesting
"""

# core/clustering/export.py
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict
from core.clustering.cluster_utils import plot_umap_clusters


def export_cluster_data(
    doc_ids: List[str],
    coords: List[List[float]],
    labels: List[int],
    label_map: Dict[str, str],
    out_dir: Path,
    metadata_dir: Path = None
):
    """
    Export cluster plot, labeled assignment map, and cluster CSV.

    Args:
        doc_ids: Document IDs
        coords: 2D UMAP coordinates
        labels: Cluster assignments
        label_map: cluster → label
        out_dir: Output folder
        metadata_dir: Where to read .meta.json (optional, for CSV)
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(coords, columns=["x", "y"])
    df["doc"] = doc_ids
    df["cluster_id"] = labels
    df["cluster_label"] = [label_map.get(f"cluster_{label}", "Unlabeled") if label != -1 else "Noise" for label in labels]

    # Save cluster JSONs
    cluster_map = {}
    for doc, label in zip(doc_ids, labels):
        if label == -1:
            continue
        cluster_map.setdefault(f"cluster_{label}", []).append(doc)

    with open(out_dir / "cluster_map.json", "w") as f:
        json.dump(cluster_map, f, indent=2)

    with open(out_dir / "cluster_labels.json", "w") as f:
        json.dump(label_map, f, indent=2)

    # Save cluster assignments
    df.to_csv(out_dir / "cluster_assignments.csv", index=False)

    # Optional metadata summary
    if metadata_dir:
        records = []
        for row in df.itertuples():
            meta_path = metadata_dir / f"{row.doc}.meta.json"
            if not meta_path.exists():
                continue
            try:
                meta = json.loads(meta_path.read_text("utf-8"))
            except Exception:
                continue
            records.append({
                "doc": row.doc,
                "summary": meta.get("summary", "")[:180],
                "topics": ", ".join(meta.get("topics", [])),
                "tags": ", ".join(meta.get("tags", [])),
                "themes": ", ".join(meta.get("themes", [])),
                "label": row.cluster_label
            })
        pd.DataFrame(records).to_csv(out_dir / "cluster_summary.csv", index=False)

    # Save PNG
    plot_umap_clusters(df, "cluster_label", "UMAP Clusters", out_dir / "umap_plot.png")
    print("✅ Cluster results exported.")
