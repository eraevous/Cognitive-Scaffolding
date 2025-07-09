#__________________________________________________________________
# File: __init__.py
# No docstring found

from .semantic_chunk import semantic_chunk_text
from .topic_segmenter import segment_text, segment_topics, topic_segmenter
from .openai_export import parse_chatgpt_export

__all__ = [
    "semantic_chunk_text",
    "segment_text",
    "parse_chatgpt_export",
]
#__________________________________________________________________
# File: chunk_text.py
"""
📦 Module: core_lib.parsing.chunk_text
- @ai-path: core_lib.parsing.chunk_text
- @ai-source-file: combined_parsing.py
- @ai-role: Chunker
- @ai-intent: "Divide long input text into paragraph-preserving segments for model input size limits."

🔍 Module Summary:
This module provides a utility to divide a long text into manageable chunks, respecting paragraph boundaries 
whenever possible. It ensures that no chunk exceeds a specified maximum character limit, preparing text 
for downstream LLM summarization, classification, or ingestion workflows.

🗂️ Contents:

| Name        | Type     | Purpose                                     |
|:------------|:---------|:--------------------------------------------|
| chunk_text  | Function | Chunk large text while preserving paragraphs when feasible. |

🧠 For AI Agents:
- @ai-dependencies: built-in stdlib (no external dependencies)
- @ai-uses: List, str, text, paragraphs
- @ai-tags: chunking, text-preprocessing, LLM-compatibility

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Initial refactor for paragraph-aware chunking
- @change-summary: Adds max_chars limit and preserves paragraph breaks unless paragraph exceeds chunk size
- @notes: ""

👤 Human Overview:
    - Context: Use this utility when preparing large bodies of text for LLM input, avoiding token overflows.
    - Change Caution: Very large paragraphs will still be split arbitrarily; consider preprocessing for those cases.
    - Future Hints: Extend to support sentence-level chunking fallback if paragraph-level split fails.
"""

"""
📦 Module: core_lib.parsing.chunk_text
- @ai-path: core_lib.parsing.chunk_text
- @ai-source-file: combined_parsing.py
- @ai-role: Chunker
- @ai-intent: "Divide long input text into paragraph-preserving segments for model input size limits."

🔍 Module Summary:
This module provides a utility to divide a long text into manageable chunks, respecting paragraph boundaries 
whenever possible. It ensures that no chunk exceeds a specified maximum character limit, preparing text 
for downstream LLM summarization, classification, or ingestion workflows.

🗂️ Contents:

| Name        | Type     | Purpose                                     |
|:------------|:---------|:--------------------------------------------|
| chunk_text  | Function | Chunk large text while preserving paragraphs when feasible. |

🧠 For AI Agents:
- @ai-dependencies: built-in stdlib (no external dependencies)
- @ai-uses: List, str, text, paragraphs
- @ai-tags: chunking, text-preprocessing, LLM-compatibility

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Initial refactor for paragraph-aware chunking
- @change-summary: Adds max_chars limit and preserves paragraph breaks unless paragraph exceeds chunk size
- @notes: ""

👤 Human Overview:
    - Context: Use this utility when preparing large bodies of text for LLM input, avoiding token overflows.
    - Change Caution: Very large paragraphs will still be split arbitrarily; consider preprocessing for those cases.
    - Future Hints: Extend to support sentence-level chunking fallback if paragraph-level split fails.
"""


from typing import List


def chunk_text(text: str, max_chars: int = 14000) -> List[str]:
    """
    Splits text into chunks, preserving paragraph boundaries when possible.

    @ai-role: chunker
    @ai-intent: "Divide a long document string into multiple manageable text blocks"

    Args:
        text (str): The input text to chunk
        max_chars (int): Maximum characters per chunk

    Returns:
        List[str]: Clean list of text chunks
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(para) > max_chars:
            if current.strip():
                chunks.append(current.strip())
                current = ""
            sub_chunks = [para[i:i+max_chars] for i in range(0, len(para), max_chars)]
            chunks.extend(sub_chunks)
            continue

        if len(current) + len(para) + 2 > max_chars:
            chunks.append(current.strip())
            current = para
        else:
            current += "\n\n" + para

    if current.strip():
        chunks.append(current.strip())

    return [chunk.strip() for chunk in chunks if chunk.strip()]
#__________________________________________________________________
# File: extract_text.py
"""
📦 Module: core_lib.parsing.extract_text
- @ai-path: core_lib.parsing.extract_text
- @ai-source-file: combined_parsing.py
- @ai-role: Parser
- @ai-intent: "Convert files (.txt, .md, .pdf, .docx) into raw text strings for LLM input or downstream processing."

🔍 Module Summary:
This module provides a flexible file extraction utility that reads multiple supported document types and 
returns their raw text content. It supports plain text files (`.txt`), Markdown files (`.md`), PDFs (`.pdf`) 
via PyMuPDF (`fitz`), and Word documents (`.docx`) via `python-docx`. Files with unsupported extensions 
trigger a clear error.

🗂️ Contents:

| Name         | Type     | Purpose                                   |
|:-------------|:---------|:------------------------------------------|
| extract_text | Function | Load and convert text content from various file types. |

🧠 For AI Agents:
- @ai-dependencies: os, markdown, python-docx, fitz
- @ai-uses: Document, ValueError, markdown, fitz, os
- @ai-tags: file-parsing, document-ingestion, preprocessing

⚙️ Meta:
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Added multi-format file parser for extract_text
- @change-summary: Initial version of parser supporting txt, md, pdf, docx
- @notes: ""

👤 Human Overview:
    - Context: Used to turn uploaded or retrieved documents into plain text for downstream classification, chunking, or summarization.
    - Change Caution: Ensure required third-party libraries (`python-docx`, `fitz`, `markdown`) are installed; otherwise functionality may fail silently.
    - Future Hints: Add support for additional formats (e.g., `.epub`, `.html`) or remote file retrieval.
"""

"""
📦 Module: core_lib.parsing.extract_text
- @ai-path: core_lib.parsing.extract_text
- @ai-source-file: combined_parsing.py
- @ai-role: Parser
- @ai-intent: "Convert files (.txt, .md, .pdf, .docx) into raw text strings for LLM input or downstream processing."

🔍 Module Summary:
This module provides a flexible file extraction utility that reads multiple supported document types and 
returns their raw text content. It supports plain text files (`.txt`), Markdown files (`.md`), PDFs (`.pdf`) 
via PyMuPDF (`fitz`), and Word documents (`.docx`) via `python-docx`. Files with unsupported extensions 
trigger a clear error.

🗂️ Contents:

| Name         | Type     | Purpose                                   |
|:-------------|:---------|:------------------------------------------|
| extract_text | Function | Load and convert text content from various file types. |

🧠 For AI Agents:
- @ai-dependencies: os, markdown, python-docx, fitz
- @ai-uses: Document, ValueError, markdown, fitz, os
- @ai-tags: file-parsing, document-ingestion, preprocessing

⚙️ Meta:
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Added multi-format file parser for extract_text
- @change-summary: Initial version of parser supporting txt, md, pdf, docx
- @notes: ""

👤 Human Overview:
    - Context: Used to turn uploaded or retrieved documents into plain text for downstream classification, chunking, or summarization.
    - Change Caution: Ensure required third-party libraries (`python-docx`, `fitz`, `markdown`) are installed; otherwise functionality may fail silently.
    - Future Hints: Add support for additional formats (e.g., `.epub`, `.html`) or remote file retrieval.
"""


import os

import fitz  # PyMuPDF
import markdown
from docx import Document


def extract_text(filepath: str) -> str:
    """
    Extracts and returns raw text content from supported file types.

    @ai-role: entrypoint
    @ai-intent: "Main function to convert documents to plaintext"

    Args:
        filepath (str): Path to the file to extract

    Returns:
        str: Cleaned or raw extracted text

    Raises:
        ValueError: If unsupported file extension is encountered
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    elif ext == ".md":
        with open(filepath, "r", encoding="utf-8") as f:
            return markdown.markdown(f.read())

    elif ext == ".pdf":
        try:
            with fitz.open(filepath) as doc:
                return "\n".join([page.get_text() for page in doc])
        except Exception as e:
            raise ValueError(f"PDF extraction failed with PyMuPDF: {e}")

    elif ext == ".docx":
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])

    else:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Unsupported file type: {ext} with error: {e}")#__________________________________________________________________
# File: normalize.py
"""
📦 Module: core_lib.utils.strings
- @ai-path: core_lib.utils.strings
- @ai-source-file: combined_utils.py
- @ai-role: String Utilities
- @ai-intent: "Standardize filenames and identifiers to lowercase with underscores for safe use across the system."

🔍 Module Summary:
This module provides lightweight string normalization utilities to ensure safe, standardized filenames 
and identifiers across cloud and local systems. It primarily transforms names to lowercase and replaces 
spaces or hyphens with underscores.

🗂️ Contents:

| Name               | Type     | Purpose                                  |
|:-------------------|:---------|:-----------------------------------------|
| normalize_filename | Function | Convert names to lowercase and underscore-separated format. |

🧠 For AI Agents:
- @ai-dependencies: None
- @ai-uses: str.lower(), str.replace()
- @ai-tags: normalization, string-utils, identifier-cleanup

⚙️ Meta:
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add basic string cleaner for identifiers
- @change-summary: Normalize filenames and labels for safe downstream use
- @notes: ""

👤 Human Overview:
    - Context: Ensures consistent naming across document upload, storage, and retrieval pipelines.
    - Change Caution: Original case and formatting are lost; irreversible unless tracked separately.
    - Future Hints: Extend normalization options to support slug generation for web compatibility.
"""

"""
📦 Module: core_lib.utils.strings
- @ai-path: core_lib.utils.strings
- @ai-source-file: combined_utils.py
- @ai-role: String Utilities
- @ai-intent: "Standardize filenames and identifiers to lowercase with underscores for safe use across the system."

🔍 Module Summary:
This module provides lightweight string normalization utilities to ensure safe, standardized filenames 
and identifiers across cloud and local systems. It primarily transforms names to lowercase and replaces 
spaces or hyphens with underscores.

🗂️ Contents:

| Name               | Type     | Purpose                                  |
|:-------------------|:---------|:-----------------------------------------|
| normalize_filename | Function | Convert names to lowercase and underscore-separated format. |

🧠 For AI Agents:
- @ai-dependencies: None
- @ai-uses: str.lower(), str.replace()
- @ai-tags: normalization, string-utils, identifier-cleanup

⚙️ Meta:
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add basic string cleaner for identifiers
- @change-summary: Normalize filenames and labels for safe downstream use
- @notes: ""

👤 Human Overview:
    - Context: Ensures consistent naming across document upload, storage, and retrieval pipelines.
    - Change Caution: Original case and formatting are lost; irreversible unless tracked separately.
    - Future Hints: Extend normalization options to support slug generation for web compatibility.
"""


def normalize_filename(name: str) -> str:
    return name.replace(" ", "_").replace("-", "_").lower()#__________________________________________________________________
# File: openai_export.py
"""
📦 Module: core.parsing.openai_export
- @ai-path: core.parsing.openai_export
- @ai-source-file: openai_export.py
- @ai-role: parser
- @ai-intent: "Parse ChatGPT Data Export zip to extract conversation transcripts and user prompts."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false

This module reads the `conversations.json` file included in an OpenAI ChatGPT
"Data Export" archive and writes each conversation to its own text file.
Additionally, it saves a corresponding file containing only the user messages
for quick prompt reuse or duplicate detection.
"""

"""
📦 Module: core.parsing.openai_export
- @ai-path: core.parsing.openai_export
- @ai-source-file: openai_export.py
- @ai-role: parser
- @ai-intent: "Parse ChatGPT Data Export zip to extract conversation transcripts and user prompts."
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false

This module reads the `conversations.json` file included in an OpenAI ChatGPT
"Data Export" archive and writes each conversation to its own text file.
Additionally, it saves a corresponding file containing only the user messages
for quick prompt reuse or duplicate detection.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import zipfile

from .normalize import normalize_filename


def _load_conversations(export_path: Path) -> List[Dict]:
    """Load conversation list from a zip archive or directory."""
    if export_path.is_dir():
        conv_path = export_path / "conversations.json"
        with conv_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    with zipfile.ZipFile(export_path) as zf:
        with zf.open("conversations.json") as f:
            return json.load(f)


def _extract_messages(convo: Dict) -> Iterable[Tuple[str, str]]:
    """Return ordered (role, text) tuples for a conversation."""
    mapping = convo.get("mapping", {})
    node_id = convo.get("current_node")
    path: List[Tuple[str, str]] = []
    while node_id:
        node = mapping.get(node_id)
        if not node:
            break
        msg = node.get("message")
        if msg and msg.get("author", {}).get("role") != "system":
            role = msg["author"].get("role", "")
            parts = msg.get("content", {}).get("parts") or []
            text = "\n".join(parts)
            path.append((role, text))
        node_id = node.get("parent")
    return reversed(path)


def parse_chatgpt_export(export_path: Path, out_dir: Path) -> List[Dict[str, Path]]:
    """Parse conversations and write text + prompt files.

    Parameters
    ----------
    export_path: Path
        Path to the `.zip` export or the extracted folder.
    out_dir: Path
        Directory to write conversation and prompt files.

    Returns
    -------
    List[Dict[str, Path]]
        List of dictionaries describing output file paths per conversation.
    """

    export_path = Path(export_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir = out_dir / "prompts"
    prompt_dir.mkdir(exist_ok=True)

    conversations = _load_conversations(export_path)
    outputs: List[Dict[str, Path]] = []
    for idx, convo in enumerate(conversations):
        title = convo.get("title") or f"conversation_{idx}"
        slug = normalize_filename(title)[:32]
        convo_file = out_dir / f"{idx:04d}_{slug}.txt"
        prompt_file = prompt_dir / f"{idx:04d}_{slug}_prompts.txt"

        lines = []
        prompts = []
        for role, text in _extract_messages(convo):
            clean = text.strip()
            lines.append(f"{role.upper()}: {clean}")
            if role == "user":
                prompts.append(clean)

        convo_file.write_text("\n".join(lines), encoding="utf-8")
        prompt_file.write_text("\n".join(prompts), encoding="utf-8")
        outputs.append({"conversation": convo_file, "prompts": prompt_file})

    return outputs
#__________________________________________________________________
# File: semantic_chunk.py
# No docstring found

from typing import Any, Dict, List, Sequence

import numpy as np
import tiktoken
import umap
from sklearn.cluster import SpectralClustering
import hdbscan

from core.embeddings.embedder import embed_text
from core.utils.logger import get_logger

logger = get_logger(__name__)


def _cluster_embeddings(embeddings: Sequence[Sequence[float]], method: str) -> List[int]:
    """Cluster embeddings using UMAP + Spectral Clustering or HDBSCAN."""
    X = np.asarray(embeddings, dtype="float32")
    reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=42)
    X_red = reducer.fit_transform(X)

    if method == "spectral":
        try:
            n_clusters = max(2, min(10, len(embeddings)))
            clusterer = SpectralClustering(
                n_clusters=n_clusters,
                affinity="nearest_neighbors",
                assign_labels="discretize",
                random_state=42,
            )
            labels = clusterer.fit_predict(X_red)
        except Exception:
            logger.exception("Spectral clustering failed; falling back to HDBSCAN")
            clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
            labels = clusterer.fit_predict(X_red)
    else:
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
        labels = clusterer.fit_predict(X_red)

    logger.debug("Cluster labels: %s", labels.tolist())
    return labels.tolist()


def semantic_chunk(
    text: str,
    model: str = "text-embedding-3-large",
    window_tokens: int = 256,
    step_tokens: int = 128,
    cluster_method: str = "spectral",
) -> List[Dict[str, Any]]:
    """Return semantic chunk objects with embeddings and metadata."""
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text, disallowed_special=())
    logger.debug("Tokenized into %d tokens", len(tokens))

    windows: List[List[float]] = []
    starts: List[int] = []
    for i in range(0, len(tokens), step_tokens):
        window = tokens[i : i + window_tokens]
        if not window:
            continue
        window_text = enc.decode(window)
        vec = embed_text(window_text, model=model)
        windows.append(vec)
        starts.append(i)
    logger.debug("Created %d windows", len(windows))

    if not windows:
        return [
            {
                "text": text,
                "embedding": embed_text(text, model=model),
                "topic": "topic_0",
                "start": 0,
                "end": len(tokens),
                "cluster_id": 0,
            }
        ]

    labels = _cluster_embeddings(windows, cluster_method)

    segments: List[Dict[str, Any]] = []
    current_start = 0
    current_label = labels[0]
    for idx in range(1, len(starts)):
        if labels[idx] != current_label:
            seg_text = enc.decode(tokens[current_start : starts[idx]])
            segments.append(
                {
                    "text": seg_text,
                    "embedding": embed_text(seg_text, model=model),
                    "topic": f"topic_{current_label}",
                    "start": current_start,
                    "end": starts[idx],
                    "cluster_id": int(current_label),
                }
            )
            current_start = starts[idx]
            current_label = labels[idx]

    seg_text = enc.decode(tokens[current_start: len(tokens)])
    segments.append(
        {
            "text": seg_text,
            "embedding": embed_text(seg_text, model=model),
            "topic": f"topic_{current_label}",
            "start": current_start,
            "end": len(tokens),
            "cluster_id": int(current_label),
        }
    )

    logger.debug("Produced %d segments", len(segments))
    return segments


def semantic_chunk_text(*args, **kwargs) -> List[str]:
    """Compatibility wrapper returning only text chunks."""
    return [c["text"] for c in semantic_chunk(*args, **kwargs)]
#__________________________________________________________________
# File: topic_segmenter.py
"""
Module: core.parsing.topic_segmenter
- @ai-path: core.parsing.topic_segmenter
- @ai-source-file: topic_segmenter.py
- @ai-role: parser
- @ai-intent: "Detect topic boundaries using UMAP + HDBSCAN over window embeddings."
"""

"""
Module: core.parsing.topic_segmenter
- @ai-path: core.parsing.topic_segmenter
- @ai-source-file: topic_segmenter.py
- @ai-role: parser
- @ai-intent: "Detect topic boundaries using UMAP + HDBSCAN over window embeddings."
"""

from typing import Any, Dict, List, Optional

import hdbscan
import numpy as np
import tiktoken
import umap

from .semantic_chunk import semantic_chunk_text
from core.embeddings.embedder import embed_text
from core.utils.logger import get_logger
from .chunk_text import chunk_text

logger = get_logger(__name__)

def topic_segmenter(text: str, model: str = "text-embedding-3-small") -> List[str]:
    """Segment text by topic using semantic chunking with a fallback."""
    chunks = semantic_chunk_text(text, model=model)
    if len(chunks) <= 1:
        return chunk_text(text)
    return chunks

def segment_text(text: str) -> List[str]:
    """Return semantic segments of ``text`` using :func:`semantic_chunk_text`."""
    return semantic_chunk_text(text)

def segment_topics(
    text: str,
    window_tokens: int = 200,
    step_tokens: int = 100,
    cluster_method: str = "hdbscan",
    model: str = "text-embedding-3-small",
    umap_config: Optional[Dict[str, Any]] = None,
    hdbscan_config: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Return topic segments with start/end token indices and cluster IDs."""
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text, disallowed_special=())

    windows: List[List[float]] = []
    starts: List[int] = []
    for i in range(0, len(tokens), step_tokens):
        window = tokens[i : i + window_tokens]
        if not window:
            continue
        window_text = enc.decode(window)
        vec = embed_text(window_text, model=model)
        windows.append(vec)
        starts.append(i)

    if not windows:
        logger.warning("No windows produced for segmentation")
        return [
            {
                "text": text,
                "start": 0,
                "end": len(tokens),
                "cluster_id": 0,
            }
        ]

    logger.info("Embedded %d windows", len(windows))

    X = np.asarray(windows, dtype="float32")
    reducer = umap.UMAP(
        **(
            umap_config
            or {"n_neighbors": 15, "min_dist": 0.1, "random_state": 42}
        )
    )
    X_red = reducer.fit_transform(X)

    if cluster_method != "hdbscan":
        logger.warning("Unsupported cluster_method %s; using hdbscan", cluster_method)

    clusterer = hdbscan.HDBSCAN(
        **(hdbscan_config or {"min_cluster_size": 2})
    )
    labels = clusterer.fit_predict(X_red)

    logger.info(
        "HDBSCAN found %d clusters", len(set(labels)) - (1 if -1 in labels else 0)
    )

    segments: List[Dict[str, Any]] = []
    current_start = 0
    current_label = int(labels[0])
    for idx in range(1, len(starts)):
        if int(labels[idx]) != current_label:
            segments.append(
                {
                    "text": enc.decode(tokens[current_start : starts[idx]]),
                    "start": current_start,
                    "end": starts[idx],
                    "cluster_id": current_label,
                }
            )
            current_start = starts[idx]
            current_label = int(labels[idx])

    segments.append(
        {
            "text": enc.decode(tokens[current_start: len(tokens)]),
            "start": current_start,
            "end": len(tokens),
            "cluster_id": current_label,
        }
    )

    return segments