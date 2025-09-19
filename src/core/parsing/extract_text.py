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
            raise ValueError(f"Unsupported file type: {ext} with error: {e}")
