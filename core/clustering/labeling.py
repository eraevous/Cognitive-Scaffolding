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

    return label_map