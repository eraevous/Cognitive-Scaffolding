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


import openai
import json
from typing import Dict, List


def label_clusters_with_gpt(
    clusters: Dict[str, List[str]],
    model: str = "gpt-4",
    preview: bool = True
) -> Dict[str, str]:
    """
    Label clusters using GPT-4 summarization.

    Args:
        clusters (Dict[str, List[str]]): Cluster ID → list of doc_ids
        model (str): OpenAI model name (default: "gpt-4")
        preview (bool): Whether to print labels live

    Returns:
        Dict[str, str]: Cluster ID → label
    """
    smart_labels = {}

    for cluster_id, docs in clusters.items():
        prompt = f"""You are an expert in information design and semantic clustering.

These are document topics:

{json.dumps(docs, indent=2)}

Provide a short (2–6 words) high-level label for this cluster:
"""

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
