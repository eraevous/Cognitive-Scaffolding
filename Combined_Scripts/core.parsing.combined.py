#__________________________________________________________________
# File: __init__.py
# No docstring found


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
    return name.replace(" ", "_").replace("-", "_").lower()