"""
Module: core_lib.parsing.extract_text 

- @ai-path: core_lib.parsing.extract_text 
- @ai-source-file: combined_parsing.py 
- @ai-module: extract_text 
- @ai-role: parser 
- @ai-entrypoint: extract_text() 
- @ai-intent: "Convert files (.txt, .md, .pdf, .docx) into raw text strings for LLM input or downstream processing."

🔍 Summary: This function loads a document from disk and returns its content as a single string. It detects file type by extension and selects the appropriate parser: `.txt` is read as plain text, `.md` is converted using `markdown`, `.pdf` is extracted via PyMuPDF (`fitz`), and `.docx` files use the `python-docx` library. Unsupported formats raise a `ValueError`.

📦 Inputs:
- filepath (str): Path to the input file. Supported formats include `.txt`, `.md`, `.pdf`, and `.docx`.

📤 Outputs:
- str: The extracted raw or cleaned text content.

🔗 Related Modules:
- chunk_text → splits this output into LLM-sized chunks
- lambda_summary → uses output as input for Claude summarization
- upload_utils → triggers this for uploaded files

🧠 For AI Agents:
- @ai-dependencies: os, markdown, python-docx, fitz
- @ai-calls: splitext, open, read, markdown, Document, get_text
- @ai-uses: Document, ValueError, markdown, fitz, os
- @ai-tags: file-parsing, document-ingestion, preprocessing

⚙️ Meta: 
- @ai-version: 0.1.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Added multi-format file parser for extract_text @change-summary: Initial version of parser supporting txt, md, pdf, docx 
- @notes: 
"""

import os
from docx import Document
import markdown
import fitz  # PyMuPDF

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
        text = ""
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
        return text

    elif ext == ".docx":
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])

    else:
        raise ValueError(f"Unsupported file type: {ext}")