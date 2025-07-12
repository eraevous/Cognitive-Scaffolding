#__________________________________________________________________
# File: embedder.py
# No docstring found

# core/embeddings/embedder.py
import json
from pathlib import Path
from typing import Dict, List, Literal

import openai

from core.config.config_registry import get_path_config, get_remote_config


def embed_text(text: str, model: str = "text-embedding-3-small") -> list[float]:
    config = get_remote_config()
    client = openai.OpenAI(api_key=config.openai_api_key)
    response = client.embeddings.create(input=text, model=model)
    return response.data[0].embedding


def generate_embeddings(
    source_dir: Path = None,
    method: Literal["parsed", "summary", "raw", "meta"] = "parsed",
    out_path: Path = None,
    model: str = "text-embedding-3-small"
) -> None:
    paths = get_path_config()

    # Use correct directories from config
    if method in ["summary", "meta"]:
        source_dir = source_dir or paths.metadata
    elif method == "parsed":
        source_dir = source_dir or paths.parsed
    elif method == "raw":
        source_dir = source_dir or paths.raw
    else:
        raise ValueError(f"Unknown method: {method}")
    
    print(f"Generating embeddings from {source_dir} using method: {method}")


    out_path = out_path or (paths.output / "rich_doc_embeddings.json")

    embeddings: Dict[str, List[float]] = {}

    pattern = "*.meta.json" if method in ["meta", "summary"] else "*.txt"
    for file in sorted(source_dir.glob(pattern)):
        doc_id = file.stem

        if method == "parsed":
            text = file.read_text(encoding="utf-8")
        elif method == "raw":
            raw_path = paths.raw / file.name
            text = raw_path.read_text(encoding="utf-8") if raw_path.exists() else ""
        elif method == "summary" or method == "meta":
            try:
                print(f"🔍 Reading metadata from {file.name}...")
                meta = json.loads(file.read_text("utf-8"))
                text = meta.get("summary", "")
            except Exception:
                continue
        else:
            raise ValueError(f"Unsupported method: {method}")

        if not text.strip():
            print(f"⚠️ Skipping empty: {file.name}")
            continue

        try:
            vector = embed_text(text, model=model)
            embeddings[doc_id] = vector
        except Exception as e:
            print(f"❌ Failed embedding {file.name}: {e}")

    out_path.write_text(json.dumps(embeddings, indent=2))
    print(f"✅ Saved {len(embeddings)} embeddings to {out_path}")#__________________________________________________________________
# File: loader.py
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

from core.config.config_registry import get_path_config, get_remote_config


def load_embeddings(embedding_path: Union[str, Path] = None) -> Tuple[List[str], np.ndarray]:
    embedding_path = Path(embedding_path) if embedding_path else get_path_config().root / "rich_doc_embeddings.json"
    
    with open(embedding_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc_ids = list(data.keys())
    X = np.array([data[doc_id] for doc_id in doc_ids])
    return doc_ids, X