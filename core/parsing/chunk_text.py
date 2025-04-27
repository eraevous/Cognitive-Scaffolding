""" 
Module: core_lib.parsing.chunk_text 

- @ai-path: core_lib.parsing.chunk_text 
- @ai-source-file: combined_parsing.py 
- @ai-module: chunk_text 
- @ai-role: chunker 
- @ai-entrypoint: chunk_text 
- @ai-intent: "Divide long input text into paragraph-preserving segments for model input size limits."

🔍 Summary: This function splits a large text input into smaller chunks that do not exceed a specified character count. It respects paragraph boundaries where feasible, but will slice large paragraphs if necessary. Used to prepare text for LLM summarization or classification in size-constrained contexts.

📦 Inputs:
- text (str): The full text document to be divided into chunks.
- max_chars (int): The maximum character length allowed per chunk (default is 14,000).

📤 Outputs:
- List[str]: Cleaned list of chunked text strings under the `max_chars` limit.

🔗 Related Modules:
- extract_text → provides raw input
- classify_large → uses chunks as unit for metadata generation

🧠 For AI Agents:
- @ai-dependencies: built-in stdlib (no external deps)
- @ai-calls: split, strip, append, extend, range, len
- @ai-uses: List, str, text, chunks, paragraphs
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
- @notes: 
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
