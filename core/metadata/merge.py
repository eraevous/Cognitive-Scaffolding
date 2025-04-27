"""
Module: core_lib.metadata.merge 

- @ai-path: core_lib.metadata.merge 
- @ai-source-file: combined_metadata.py 
- @ai-module: merge 
- @ai-role: metadata_aggregator 
- @ai-entrypoint: merge_metadata_blocks(), resolve_parsed_filename() 
- @ai-intent: "Combine segmented metadata chunks into one unified dict and resolve filename identity from stubs."

🔍 Summary: 
Provides two key utilities for downstream classification workflows:
- `merge_metadata_blocks` merges chunked metadata dictionaries (e.g. from `classify_large`) by averaging, unioning, and majority-voting values.
- `resolve_parsed_filename` inspects stub files to find the `.txt` output for a given raw input document.

📦 Inputs:
- blocks (List[Dict]): Partial metadata outputs from classification
- raw_or_parsed (str): Filename from original source
- stub_dir (str): Location to search for `.stub.json` files

📤 Outputs:
- merge_metadata_blocks → Dict: Final consolidated metadata
- resolve_parsed_filename → str: Parsed `.txt` filename

🔗 Related Modules:
- classify_large → generates block metadata
- io.py → saves/loads merged results
- stub_writer → produces stub inputs for resolution

🧠 For AI Agents:
- @ai-dependencies: json, pathlib, collections
- @ai-calls: Counter, most_common, json.load, glob, open, Path, flatten
- @ai-uses: ValueError, FileNotFoundError, stub, summary, category
- @ai-tags: metadata-merging, filename-resolution, pipeline-support

⚙️ Meta: 
- @ai-version: 0.2.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Add chunk metadata merge + filename resolution logic 
- @change-summary: Created post-classification tools to consolidate metadata and map filenames 
- @notes: 
"""


import json
from pathlib import Path
from collections import Counter
from typing import List, Dict

def merge_metadata_blocks(blocks: List[Dict]) -> Dict:
    """
    Merge multiple metadata blocks (from chunked summarization) into a single unified metadata dict.

    @ai-role: merger
    @ai-intent: "Combine multiple partial metadata objects into one"

    Args:
        blocks (List[Dict]): List of metadata dictionaries.

    Returns:
        Dict: Merged metadata dictionary.

    Raises:
        ValueError: If no valid blocks are provided.
    """
    if not blocks:
        raise ValueError("No valid metadata blocks to merge.")

    def flatten(key: str) -> List:
        return list({x for block in blocks for x in block.get(key, [])})

    summary = " ".join(block.get("summary", "") for block in blocks)
    topics = flatten("topics")
    tags = flatten("tags")
    themes = flatten("themes")
    priority = round(sum(block.get("priority", 3) for block in blocks) / len(blocks))

    def most_common(key: str) -> str:
        return Counter(block.get(key, "") for block in blocks).most_common(1)[0][0]

    return {
        "summary": summary.strip(),
        "topics": topics,
        "tags": tags,
        "themes": themes,
        "priority": priority,
        "tone": most_common("tone"),
        "stage": most_common("stage"),
        "depth": most_common("depth"),
        "category": most_common("category")
    }

def resolve_parsed_filename(raw_or_parsed: str, stub_dir: str = "metadata") -> str:
    """
    Resolves a filename (raw or parsed) into its parsed .txt equivalent by inspecting stub files.

    @ai-role: filename resolver
    @ai-intent: "Translate raw input filename into its parsed .txt target using stub metadata"

    Args:
        raw_or_parsed (str): Filename of the raw or parsed file.
        stub_dir (str): Directory where stub files are stored.

    Returns:
        str: Filename of the parsed .txt file.

    Raises:
        FileNotFoundError: If no matching stub is found.
    """
    name = Path(raw_or_parsed).name

    if name.endswith(".txt"):
        return name

    stub_path = Path(stub_dir)
    for stub_file in stub_path.glob("*.stub.json"):
        with open(stub_file, "r", encoding="utf-8") as f:
            stub = json.load(f)
        if Path(stub.get("source_file", "")).name.lower() == name.lower():
            return Path(stub["parsed_file"]).name

    raise FileNotFoundError(f"No stub found for raw file '{name}'")