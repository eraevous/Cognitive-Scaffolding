"""
Module: core_lib.embeddings.loader 
- @ai-path: core_lib.embeddings.loader 
- @ai-source-file: embedding.py 
- @ai-module: embeddings_loader 
- @ai-role: data_loader 
- @ai-entrypoint: load_embeddings() 
- @ai-intent: "Load document embeddings from a JSON file into a doc ID list and NumPy matrix for clustering."

🔍 Summary:
This function loads precomputed document embeddings stored in JSON format. It parses the mapping of document IDs to embedding vectors and returns both the list of document IDs and a 2D NumPy array of embeddings for downstream clustering or semantic analysis.

📦 Inputs:
- embedding_path (str | Path): Path to a `.json` file containing {doc_id: embedding_vector} mapping

📤 Outputs:
- Tuple[List[str], np.ndarray]:
    - doc_ids: List of document identifiers
    - X: NumPy array of shape (n_documents, embedding_dim)

🔗 Related Modules:
- clustering.algorithms → consumes the embeddings for clustering
- clustering.pipeline → orchestrates loading and clustering

🧠 For AI Agents:
- @ai-dependencies: json, numpy
- @ai-calls: json.load(), numpy.array()
- @ai-uses: embedding_path, data
- @ai-tags: embeddings, data-loading, numpy, document-ids

⚙️ Meta: 
- @ai-version: 0.1.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Load embedding JSON as doc ID list and embedding matrix @change-summary: Add JSON-to-NumPy embedding loader for clustering input 
- @notes:

🚧 Future Enhancements:
- [ ] Add support for `.jsonl`, `.csv`, and other formats
- [ ] Add schema validation to ensure embeddings are well-formed
- [ ] Add support for lazy-loading or memory-mapped embeddings
"""


import json
import numpy as np
from pathlib import Path
from typing import Tuple, List, Union
from core.config.config_registry import get_remote_config, get_path_config

def load_embeddings(embedding_path: Union[str, Path] = None) -> Tuple[List[str], np.ndarray]:
    embedding_path = Path(embedding_path) if embedding_path else get_path_config().root / "rich_doc_embeddings.json"
    
    with open(embedding_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc_ids = list(data.keys())
    X = np.array([data[doc_id] for doc_id in doc_ids])
    return doc_ids, X