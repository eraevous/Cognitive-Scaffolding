"""
Module: core_lib.workflows.main_commands 
- @ai-path: core_lib.workflows.main_commands 
- @ai-source-file: main_commands.py 
- @ai-module: main_commands 
- @ai-role: classifier 
- @ai-entrypoint: classify(), classify_large() 
- @ai-intent: "Classify parsed documents (or chunks of documents) using LLM-based Lambda summarization."

🔍 Summary:
This module contains two core functions to classify documents. `classify()` supports direct classification of single parsed files or chat logs, while `classify_large()` supports chunked classification for longer documents and merges the results. Both rely on Claude Lambda summarization and return validated `.meta.json`.

📦 Inputs:
- name (str): Filename of the parsed document (or raw for large mode)
- paths (PathConfig): Config for raw, parsed, and metadata directories
- remote (RemoteConfig, optional): AWS credentials and bucket names

📤 Outputs:
- dict: Validated metadata dictionary saved to S3

🔗 Related Modules:
- lambda_summary → sends chunks or full files to Claude Lambda
- chunk_text → used to split long documents
- merge_metadata_blocks → merges multiple chunk-level results
- schema → validates output
- s3_utils → saves final `.meta.json`

🧠 For AI Agents:
- @ai-dependencies: json, boto3, pathlib
- @ai-calls: invoke_summary(), invoke_chatlog_summary(), chunk_text(), validate_metadata(), save_metadata_s3()
- @ai-uses: PathConfig, RemoteConfig, stub_path
- @ai-tags: summarization, metadata, classification, S3, chunking, schema-validation

⚙️ Meta: 
- @ai-version: 0.3.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Move classify/classify_large logic from CLI into shared main_commands module 
- @change-summary: Refactor classification into reusable backend for CLI + batch 
- @notes: 
"""

import json
from pathlib import Path
from typing import Optional

from core.config.config_registry import get_path_config, get_remote_config
from core.llm.invoke import summarize_text
from core.metadata.merge import merge_metadata_blocks
from core.metadata.schema import validate_metadata
from core.parsing.chunk_text import chunk_text
from core.storage.upload_local import upload_file

MAX_CHARS = 16000

def get_parsed_text(name: str) -> str:
    paths = get_path_config()
    parsed_path = paths.parsed / name
    return parsed_path.read_text(encoding="utf-8")

def looks_like_chatlog(text: str) -> bool:
    lines = text.lower().splitlines()
    return sum(1 for l in lines[:50] if any(k in l for k in ["user:", "assistant:", "you:", "chatgpt:"])) > 2

def classify(name: str, chunked: bool = False) -> dict:
    paths = get_path_config()
    parsed_path = paths.parsed / name
    text = parsed_path.read_text(encoding="utf-8")

    doc_type = "chatlog" if looks_like_chatlog(text) else "standard"

    if not chunked and len(text) <= MAX_CHARS:
        metadata = summarize_text(text, doc_type=doc_type)
    else:
        chunks = chunk_text(text)
        block_results = [summarize_text(chunk, doc_type=doc_type) for chunk in chunks if chunk.strip()]
        metadata = merge_metadata_blocks(block_results)

    # Merge with stub if present
    stub_path = paths.metadata / f"{name}.stub.json"
    if stub_path.exists():
        stub = json.loads(stub_path.read_text("utf-8"))
        metadata.update(stub)

    validate_metadata(metadata)

    out_path = paths.metadata / f"{name}.meta.json"
    out_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata

def upload_metadata_to_s3(name: str, metadata: dict):
    from core.config.remote_config import RemoteConfig
    from core.storage.s3_utils import save_metadata_s3
    remote = get_remote_config()
    key = f"{remote.prefixes['metadata']}{name}.meta.json"
    save_metadata_s3(remote.bucket_name, key, metadata)

def upload_and_prepare(file_name: str, parsed_name: Optional[str] = None):
    upload_file(file_name, parsed_name)

def pipeline_from_upload(file_name: str, parsed_name: Optional[str] = None) -> dict:
    upload_and_prepare(file_name, parsed_name)
    txt_name = parsed_name or Path(file_name).stem.replace(" ", "_").replace("-", "_").lower() + ".txt"
    metadata = classify(txt_name)
    return metadata