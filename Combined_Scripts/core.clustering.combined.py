#__________________________________________________________________
# File: __init__.py
# No docstring found


#__________________________________________________________________
# File: algorithms.py
# No docstring found

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
#__________________________________________________________________
# File: assignments.py
# No docstring found

#__________________________________________________________________
# File: cluster_helpers.py
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
print("📋 cluster_summary.csv saved.")#__________________________________________________________________
# File: cluster_runner.py
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
    n_spectral_clusters: int = 24
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
        random_state=42
    ).fit(X)
    labels_spec = spec.labels_

    return umap_coords, labels_hdb, labels_spec#__________________________________________________________________
# File: cluster_utils.py
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

from pathlib import Path
from typing import Dict, List

# core/clustering/utils.py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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
#__________________________________________________________________
# File: clustering_steps.py
# No docstring found

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
#__________________________________________________________________
# File: export.py
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
from pathlib import Path
from typing import Dict, List

import pandas as pd

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
#__________________________________________________________________
# File: labeling.py
"""
Module: core_lib.clustering.labeling 
- @ai-path: core_lib.clustering.labeling 
- @ai-source-file: labeling.py 
- @ai-module: cluster_labeling 
- @ai-role: gpt_labeler 
- @ai-entrypoint: label_clusters_with_gpt() 
- @ai-intent: "Use a GPT model to generate short semantic labels for document clusters."

🔍 Summary:
This function sends each document cluster to a GPT model and requests a short semantic label (2–6 words) summarizing the cluster. It builds a prompt based on the cluster's document IDs or names and returns a mapping of cluster IDs to generated labels.

📦 Inputs:
- clusters (Dict[str, List[str]]): Mapping of cluster IDs to lists of document IDs
- model (str): OpenAI model name (default: "gpt-4")
- preview (bool): If True, prints cluster labels as they are generated

📤 Outputs:
- Dict[str, str]: Mapping of cluster ID to generated label

🔗 Related Modules:
- export.py → uses these labels for flattened doc_id mappings
- cluster_runner → applies labels after clustering

🧠 For AI Agents:
- @ai-dependencies: openai, json
- @ai-calls: openai.ChatCompletion.create()
- @ai-uses: clusters, cluster_id, doc list
- @ai-tags: gpt, labeling, clustering, summarization, openai

⚙️ Meta: 
- @ai-version: 0.2.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Generate GPT-based cluster labels from document groupings 
- @change-summary: Smart label generation for cluster visualization and reporting 
- @notes:

🚧 Future Enhancements:
- [ ] Batch multiple clusters into one GPT call to reduce API costs
- [ ] Allow retrying failed or low-confidence label generations
- [ ] Add label cleaning (e.g., max character limits, safe character filtering)
"""

"""
Module: core_lib.clustering.labeling 
- @ai-path: core_lib.clustering.labeling 
- @ai-source-file: labeling.py 
- @ai-module: cluster_labeling 
- @ai-role: gpt_labeler 
- @ai-entrypoint: label_clusters_with_gpt() 
- @ai-intent: "Use a GPT model to generate short semantic labels for document clusters."

🔍 Summary:
This function sends each document cluster to a GPT model and requests a short semantic label (2–6 words) summarizing the cluster. It builds a prompt based on the cluster's document IDs or names and returns a mapping of cluster IDs to generated labels.

📦 Inputs:
- clusters (Dict[str, List[str]]): Mapping of cluster IDs to lists of document IDs
- model (str): OpenAI model name (default: "gpt-4")
- preview (bool): If True, prints cluster labels as they are generated

📤 Outputs:
- Dict[str, str]: Mapping of cluster ID to generated label

🔗 Related Modules:
- export.py → uses these labels for flattened doc_id mappings
- cluster_runner → applies labels after clustering

🧠 For AI Agents:
- @ai-dependencies: openai, json
- @ai-calls: openai.ChatCompletion.create()
- @ai-uses: clusters, cluster_id, doc list
- @ai-tags: gpt, labeling, clustering, summarization, openai

⚙️ Meta: 
- @ai-version: 0.2.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Generate GPT-based cluster labels from document groupings 
- @change-summary: Smart label generation for cluster visualization and reporting 
- @notes:

🚧 Future Enhancements:
- [ ] Batch multiple clusters into one GPT call to reduce API costs
- [ ] Allow retrying failed or low-confidence label generations
- [ ] Add label cleaning (e.g., max character limits, safe character filtering)
"""

# core/clustering/labeling.py
import json
from typing import Dict, List

from openai import OpenAI

from core.config.config_registry import get_remote_config


def label_clusters(
    doc_ids: List[str],
    labels: List[int],
    metadata_dir,
    model: str = "gpt-4",
    preview: bool = True
) -> Dict[str, str]:
    """
    Generate GPT labels for each cluster.

    Args:
        doc_ids: List of document IDs
        labels: Cluster assignments (same order as doc_ids)
        metadata_dir: Path to .meta.json files
        model: OpenAI model
        preview: Whether to print live output

    Returns:
        cluster_id → label
    """
    # Build cluster → [titles] mapping
    cluster_map = {}
    for doc, label in zip(doc_ids, labels):
        if label == -1:
            continue
        meta_path = metadata_dir / f"{doc}.meta.json"
        if not meta_path.exists():
            continue
        try:
            meta = json.loads(meta_path.read_text("utf-8"))
            title = meta.get("summary") or "Untitled"
        except Exception:
            title = "Untitled"
        cluster_map.setdefault(f"cluster_{label}", []).append(title)

    # Init GPT
    config = get_remote_config()
    client = OpenAI(api_key=config.openai_api_key)

    label_map = {}
    for cluster_id, docs in cluster_map.items():
        prompt = f"""You are an expert in document summarization and thematic clustering.
    Here are summaries of documents in a cluster:
    {json.dumps(docs, indent=2)}
    Give a short 2–6 word descriptive label for this cluster:
    """
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            label = response.choices[0].message.content.strip()
        except Exception as e:
            label = "Unlabeled"
            print(f"❌ {cluster_id}: {e}")
        label_map[cluster_id] = label
        if preview:
            print(f"{cluster_id}: {label}")

    return label_map#__________________________________________________________________
# File: pipeline.py
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


def cluster_dict(labels, doc_ids):
    out = {}
    for label, doc in zip(labels, doc_ids):
        if label == -1:
            continue
        out.setdefault(f"cluster_{label}", []).append(doc)
    return out


def run_clustering_pipeline(
    embedding_path: Path = Path("rich_doc_embeddings.json"),
    metadata_dir: Path = Path("metadata"),
    out_dir: Path = Path("output")
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
    umap_df["cluster_hdb"] = [assignments_hdb.get(doc.lower(), "Noise") for doc in doc_ids]
    umap_df["cluster_spec"] = [assignments_spec.get(doc.lower(), "Unknown") for doc in doc_ids]

    plot_umap_clusters(umap_df, "cluster_hdb", "UMAP - HDBSCAN Clusters", str(out_dir / "umap_hdbscan.png"))
    plot_umap_clusters(umap_df, "cluster_spec", "UMAP - Spectral Clusters", str(out_dir / "umap_spectral.png"))

    export_clusters_and_summary(
        cluster_maps={"hdbscan": clusters_hdb, "spectral": clusters_spec},
        assignments=assignments_hdb,
        umap_df=umap_df,
        metadata_dir=metadata_dir,
        out_dir=out_dir
    )