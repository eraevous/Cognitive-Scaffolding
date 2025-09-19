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
            sub_chunks = [
                para[i : i + max_chars] for i in range(0, len(para), max_chars)
            ]
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
