# Module: core.clustering
> Full clustering subsystem: dimensionality reduction, clustering, GPT-based labeling, visualization, and export.

### 🎯 Intent & Responsibility
- Orchestrate the end-to-end clustering of document embeddings.
- Provide modular components for dimensionality reduction, HDBSCAN/Spectral clustering, semantic labeling using GPT, visual UMAP plots, and metadata-enriched CSV/JSON outputs.

### 📥 Inputs & 📤 Outputs
| Direction | Name           | Type             | Brief Description                                                  |
|-----------|----------------|------------------|----------------------------------------------------------------------|
| 📥 In     | embedding_path | Path              | Path to JSON file of document embeddings                            |
| 📥 In     | metadata_dir   | Path              | Directory of `.meta.json` files used for cluster labeling            |
| 📥 In     | method         | str               | Clustering algorithm: `"hdbscan"` or `"spectral"`                   |
| 📥 In     | model          | str               | GPT model used for cluster labeling (e.g., `gpt-4`)                  |
| 📤 Out    | coords         | np.ndarray        | 2D coordinates from UMAP                                            |
| 📤 Out    | labels         | List[int]         | Cluster assignments from selected algorithm                         |
| 📤 Out    | label_map      | Dict[str, str]    | Cluster ID → human-readable label                                   |
| 📤 Out    | assignments    | Dict[str, str]    | doc_id → semantic cluster label                                     |
| 📤 Out    | umap_df        | pd.DataFrame      | DataFrame with UMAP coords and label columns                        |
| 📤 Out    | cluster_summary.csv | CSV         | Metadata-enriched CSV for analysis                                  |
| 📤 Out    | cluster_map.json     | JSON        | Mapping of clusters to document IDs                                 |
| 📤 Out    | cluster_labels.json  | JSON        | Mapping of cluster ID to GPT label                                  |
| 📤 Out    | umap_plot.png         | PNG         | UMAP scatterplot visualization                                      |

### 🔗 Dependencies
- `umap-learn`, `hdbscan`, `sklearn.cluster` – Clustering and dimensionality reduction
- `openai` – GPT-based cluster labeling
- `pandas`, `matplotlib`, `json`, `pathlib` – Plotting, I/O, and tabular output
- `core.embeddings.loader`, `core.config.config_registry`, `core.clustering.labeling`, `core.clustering.export`, `core.clustering.cluster_utils`

### ⚙️ AI-Memory Tags
- `@ai-assumes:` Embedding vectors and metadata exist and match by doc ID.
- `@ai-breakage:` GPT schema changes or removal of `.meta.json` summaries will break labeling.
- `@ai-risks:` GPT-based labels can be noisy or inconsistent; labeling step is non-deterministic and may incur API cost or rate limits.

### 🗣 Dialogic Notes
- This subsystem is modular: each step (UMAP, clustering, labeling, export) is isolated for independent testing or enhancement.
- Dual-clustering (HDBSCAN + Spectral) provides complementary views—both label sets can be visualized or exported.
- Future improvements could include batched GPT labeling, interactive cluster review UI, and clustering method auto-tuning.
