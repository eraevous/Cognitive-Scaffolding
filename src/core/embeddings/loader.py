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
from pathlib import Path
from typing import List, Tuple, Union

import numpy as np


def _extract_embedding(value: object) -> np.ndarray:
    """Normalize serialized embedding payloads into a 1D numpy array."""

    array = np.asarray(value, dtype=float)
    if array.ndim == 0:
        # Scalar values are unexpected but coerce to a 1-length vector to avoid crashes.
        array = array.reshape(1)
    if array.ndim > 1:
        # Some pipelines may have stored nested lists; flatten to a single vector.
        array = array.reshape(-1)
    return array


def load_embeddings(embedding_path: Union[str, Path]) -> Tuple[List[str], np.ndarray]:
    """
    Load JSON-based document embeddings and return doc IDs and matrix.
    """

    embedding_path = Path(embedding_path)
    with open(embedding_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc_ids = list(data.keys())
    if not doc_ids:
        return doc_ids, np.empty((0, 0), dtype=float)

    vectors: List[np.ndarray] = []
    for doc_id in doc_ids:
        payload = data[doc_id]
        if isinstance(payload, dict):
            if "embedding" in payload:
                payload = payload["embedding"]
            else:
                raise ValueError(
                    f"Embedding payload for '{doc_id}' does not include an 'embedding' field."
                )
        vectors.append(_extract_embedding(payload))

    matrix = np.vstack([np.atleast_2d(vec) for vec in vectors])
    if matrix.ndim == 1:
        matrix = matrix.reshape(1, -1)
    elif matrix.ndim > 2:
        matrix = matrix.reshape(matrix.shape[0], -1)

    return doc_ids, np.asarray(matrix, dtype=float)
