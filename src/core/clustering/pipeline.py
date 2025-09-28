"""
Module: core_lib.clustering.pipeline 
- @ai-path: core_lib.clustering.pipeline 
- @ai-source-file: combined_clustering.py 
- @ai-module: pipeline 
- @ai-role: clustering_pipeline 
- @ai-entrypoint: run_clustering_pipeline() 
- @ai-intent: "Load embeddings, cluster documents, label clusters using GPT, and export visual and tabular summaries."

🔍 Summary:
This function orchestrates the entire document clustering pipeline:
- Loads document embeddings from a JSON file
- Reduces embeddings to 2D with UMAP
- Clusters documents using both HDBSCAN and Spectral Clustering
- Labels each cluster using a GPT model for semantic descriptions
- Flattens cluster assignments into doc_id → label mappings
- Visualizes clusters on a UMAP scatter plot
- Exports cluster maps, document label assignments, and a metadata-enhanced CSV summary

📦 Inputs:
- embedding_path (Path): Path to embeddings JSON file (default: "rich_doc_embeddings.json")
- metadata_dir (Path): Directory containing `.meta.json` files for documents (default: "metadata/")
- out_dir (Path): Output directory for saving cluster maps, plots, and summaries (default: "output/")

📤 Outputs:
- JSON cluster maps (HDBSCAN + Spectral)
- JSON flattened document label mappings
- PNG visualizations (UMAP plots)
- CSV metadata summaries with cluster labels

🔗 Related Modules:
- embedding.py → loads embeddings
- algorithms.py → UMAP + clustering
- labeling.py → GPT label generation
- assignments.py → flatten cluster mapping
- plotting.py → UMAP cluster visualizations
- export.py → saves final cluster results

🧠 For AI Agents:
- @ai-dependencies: pandas, numpy, hdbscan, sklearn, openai, matplotlib, pathlib
- @ai-calls: load_embeddings(), cluster_embeddings(), label_clusters_with_gpt(), flatten_cluster_map(), plot_umap_clusters(), export_clusters_and_summary()
- @ai-uses: doc_ids, umap_coords, cluster maps, label assignments
- @ai-tags: clustering, embeddings, GPT-labeling, visualization, export, UMAP

⚙️ Meta: 
- @ai-version: 0.4.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Clean full clustering pipeline orchestration 
- @change-summary: Modularize loading, clustering, labeling, visualization, and exporting into pipeline entrypoint 
- @notes:

🚧 Future Enhancements:
- [ ] Allow optional GPT model and temperature overrides
- [ ] Validate embeddings and metadata file consistency early
- [ ] Parallelize GPT labeling across clusters to reduce latency
- [ ] Add summary JSON file describing clustering settings and results
"""


from pathlib import Path

import pandas as pd
from clustering.algorithms import cluster_embeddings
from clustering.assignments import flatten_cluster_map
from clustering.embedding import load_embeddings
from clustering.export import export_clusters_and_summary
from clustering.labeling import label_clusters_with_gpt
from clustering.plotting import plot_umap_clusters

from core.config import LOCAL_METADATA_DIR, LOCAL_OUTPUT_DIR


def cluster_dict(labels, doc_ids):
    out = {}
    for label, doc in zip(labels, doc_ids):
        if label == -1:
            continue
        out.setdefault(f"cluster_{label}", []).append(doc)
    return out


def run_clustering_pipeline(
    embedding_path: Path = Path("rich_doc_embeddings.json"),
    metadata_dir: Path = LOCAL_METADATA_DIR,
    out_dir: Path = LOCAL_OUTPUT_DIR,
):
    doc_ids, X = load_embeddings(embedding_path)
    X_umap, labels_hdb, labels_spec = cluster_embeddings(X)

    clusters_hdb = cluster_dict(labels_hdb, doc_ids)
    clusters_spec = cluster_dict(labels_spec, doc_ids)

    smart_labels_hdb = label_clusters_with_gpt(clusters_hdb)
    smart_labels_spec = label_clusters_with_gpt(clusters_spec)

    assignments_hdb = flatten_cluster_map(clusters_hdb, smart_labels_hdb)
    assignments_spec = flatten_cluster_map(clusters_spec, smart_labels_spec)

    # Build shared UMAP dataframe
    umap_df = pd.DataFrame(X_umap, columns=["x", "y"])
    umap_df["doc"] = doc_ids
    umap_df["cluster_hdb"] = [
        assignments_hdb.get(doc.lower(), "Noise") for doc in doc_ids
    ]
    umap_df["cluster_spec"] = [
        assignments_spec.get(doc.lower(), "Unknown") for doc in doc_ids
    ]

    plot_umap_clusters(
        umap_df,
        "cluster_hdb",
        "UMAP - HDBSCAN Clusters",
        str(out_dir / "umap_hdbscan.png"),
    )
    plot_umap_clusters(
        umap_df,
        "cluster_spec",
        "UMAP - Spectral Clusters",
        str(out_dir / "umap_spectral.png"),
    )

    export_clusters_and_summary(
        cluster_maps={"hdbscan": clusters_hdb, "spectral": clusters_spec},
        assignments=assignments_hdb,
        umap_df=umap_df,
        metadata_dir=metadata_dir,
        out_dir=out_dir,
    )
