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


import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any


def export_clusters_and_summary(
    cluster_maps: Dict[str, Any],
    assignments: Dict[str, str],
    umap_df: pd.DataFrame,
    metadata_dir: Path,
    out_dir: Path
) -> None:
    """
    Save cluster maps, assignments, and a labeled metadata summary CSV.

    Args:
        cluster_maps (Dict[str, Any]): e.g. {"hdb": clusters_hdb, "spec": clusters_spec}
        assignments (Dict[str, str]): doc → label
        umap_df (pd.DataFrame): must include doc_id and UMAP coords
        metadata_dir (Path): path to all metadata files
        out_dir (Path): output folder
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save cluster maps
    for name, data in cluster_maps.items():
        with open(out_dir / f"cluster_map_{name}.json", "w") as f:
            json.dump(data, f, indent=2)

    with open(out_dir / "cluster_assignments.json", "w") as f:
        json.dump(assignments, f, indent=2)

    # Build CSV
    records = []
    for doc in umap_df["doc"]:
        meta_path = metadata_dir / f"{doc}.meta.json"
        if not meta_path.exists():
            continue
        with open(meta_path, "r", encoding="utf-8") as f:
            try:
                meta = json.load(f)
            except:
                continue
        records.append({
            "doc": doc,
            "category": meta.get("category"),
            "summary": meta.get("summary", "")[:180],
            "topics": ", ".join(meta.get("topics", [])),
            "tags": ", ".join(meta.get("tags", [])),
            "themes": ", ".join(meta.get("themes", [])),
            "cluster_label": assignments.get(doc.lower(), "Unknown")
        })

    pd.DataFrame(records).to_csv(out_dir / "cluster_summary.csv", index=False)
    print("✅ Cluster data exported.")
