"""
Module: core_lib.clustering.cluster_helpers
- @ai-path: core_lib.clustering.cluster_helpers
- @ai-source-file: combined_clustering.py
- @ai-module: cluster_helpers
- @ai-role: clustering_utils
- @ai-entrypoint: label_clusters_with_gpt(), plot_umap_clusters()
- @ai-intent: "Group documents, label clusters using GPT, and visualize clustering results."

🔍 Summary:
This module provides helper functions for the clustering pipeline:
- `cluster_dict` builds cluster → document mappings
- `label_clusters_with_gpt` queries OpenAI to assign human-readable labels to clusters
- `plot_umap_clusters` visualizes clusters in 2D UMAP space

📦 Inputs:
- labels (list): List of predicted cluster labels
- clusters (Dict[str, List[str]]): Cluster-to-doc mapping
- model (str): OpenAI model name
- preview (bool): If True, print GPT outputs
- df (DataFrame): DataFrame containing UMAP 2D coordinates
- label_col (str): Column name for cluster labels
- title (str): Plot title
- out_file (str): Save location for UMAP plot

📤 Outputs:
- cluster_dict → Dict[str, List[str]]
- label_clusters_with_gpt → Dict[str, str] (cluster_id → label)
- plot_umap_clusters → Saves plot image to disk

🔗 Related Modules:
- cluster_runner → runs full clustering
- gpt_labeling → alternative approaches to labeling clusters
- cluster_viz → uses UMAP plotting

🧠 For AI Agents:
- @ai-dependencies: openai, matplotlib, json, numpy
- @ai-calls: openai.ChatCompletion.create, plt.scatter(), plt.savefig()
- @ai-uses: cluster_id, doc_ids, label_map
- @ai-tags: clustering, GPT-labeling, visualization, UMAP

⚙️ Meta:
- @ai-version: 0.3.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add cluster helpers (labeling, plotting) to pipeline
- @change-summary: Build tools for labeling and visualizing document clusters
- @notes: 
"""

import json
from pathlib import Path

import hdbscan
import matplotlib.pyplot as plt
import numpy as np
import openai
import pandas as pd
import umap
from sklearn.cluster import SpectralClustering
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

# 📂 CONFIG
embedding_path = Path("rich_doc_embeddings.json")
metadata_dir = META_PREFIX
openai.api_key = OPENAI_API_KEY

# 🧠 Load embeddings
with open(embedding_path, "r", encoding="utf-8") as f:
    embeddings = json.load(f)

doc_ids = list(embeddings.keys())
X = np.array([embeddings[k] for k in doc_ids])

# 📉 Dimensionality reduction
reducer = umap.UMAP(random_state=42)
X_umap = reducer.fit_transform(X)

# 📊 Save doc_id → UMAP
umap_df = pd.DataFrame(X_umap, columns=["x", "y"])
umap_df["doc"] = doc_ids

# 🔗 HDBSCAN clustering
hdb = hdbscan.HDBSCAN(min_cluster_size=4, prediction_data=True).fit(X)
labels_hdb = hdb.labels_

# 🔗 Spectral clustering
n_clusters = 24  # tweakable
spec = SpectralClustering(n_clusters=n_clusters, affinity="nearest_neighbors", assign_labels="kmeans").fit(X)
labels_spec = spec.labels_

# 🔁 Utility: cluster to dict
def cluster_dict(labels):
    out = {}
    for label, doc in zip(labels, doc_ids):
        if label == -1:
            continue
        out.setdefault(f"cluster_{label}", []).append(doc)
    return out

clusters_hdb = cluster_dict(labels_hdb)
clusters_spec = cluster_dict(labels_spec)

# 💬 Smart GPT labels
def label_clusters_with_gpt(clusters, model="gpt-4", preview=True):
    smart_labels = {}
    for cluster_id, docs in clusters.items():
        prompt = f"""You are an expert in information design and semantic clustering.

These are document topics:

{json.dumps(docs, indent=2)}

Provide a short (2–6 words) high-level label for this cluster:"""

        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        label = response.choices[0].message.content.strip()
        smart_labels[cluster_id] = label
        if preview:
            print(f"{cluster_id}: {label}")
    return smart_labels

smart_labels_hdb = label_clusters_with_gpt(clusters_hdb)
smart_labels_spec = label_clusters_with_gpt(clusters_spec)

# 🧠 Doc-level assignment
def flatten_cluster_map(cluster_map, label_map):
    flat = {}
    for cluster_id, docs in cluster_map.items():
        label = label_map.get(cluster_id, cluster_id)
        for doc in docs:
            flat[doc.lower()] = label
    return flat

assignments_hdb = flatten_cluster_map(clusters_hdb, smart_labels_hdb)
assignments_spec = flatten_cluster_map(clusters_spec, smart_labels_spec)

# 💾 Save JSON maps
Path("output").mkdir(exist_ok=True)

with open("output/cluster_map_hdbscan.json", "w") as f:
    json.dump(clusters_hdb, f, indent=2)
with open("output/cluster_map_spectral.json", "w") as f:
    json.dump(clusters_spec, f, indent=2)
with open("output/cluster_assignments_hdb.json", "w") as f:
    json.dump(assignments_hdb, f, indent=2)
with open("output/cluster_assignments_spectral.json", "w") as f:
    json.dump(assignments_spec, f, indent=2)

print("✅ Cluster maps saved.")

# 📊 Label UMAP data
umap_df["cluster_hdb"] = [assignments_hdb.get(doc.lower(), "Noise") for doc in doc_ids]
umap_df["cluster_spec"] = [assignments_spec.get(doc.lower(), "Unknown") for doc in doc_ids]

# 📈 UMAP plot with labels
def plot_umap_clusters(df, label_col, title, out_file):
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
    plt.show()

plot_umap_clusters(umap_df, "cluster_hdb", "UMAP - HDBSCAN Smart Clusters", "output/umap_hdbscan.png")
plot_umap_clusters(umap_df, "cluster_spec", "UMAP - Spectral Smart Clusters", "output/umap_spectral.png")

# 📋 Export metadata + cluster label to CSV
records = []
for doc in doc_ids:
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
        "cluster_hdb": assignments_hdb.get(doc.lower(), "Noise"),
        "cluster_spec": assignments_spec.get(doc.lower(), "Unknown"),
    })

pd.DataFrame(records).to_csv("output/cluster_summary.csv", index=False)
print("📋 cluster_summary.csv saved.")