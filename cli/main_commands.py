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

from core.config.path_config import PathConfig
from core.config.remote_config import RemoteConfig
from core.storage.aws_clients import get_s3_client
from core.storage.s3_utils import save_metadata_s3
from core.utils.upload_utils import upload_file
from core.llm.invoke import summarize_text
from core.parsing.chunk_text import chunk_text
from core.metadata.schema import validate_metadata
from core.metadata.merge import merge_metadata_blocks


def get_parsed_text(name: str, paths: Optional[PathConfig] = None) -> str:
    paths = paths or PathConfig.from_file()
    parsed_path = paths.parsed / name
    return parsed_path.read_text(encoding="utf-8")


def looks_like_chatlog(text: str) -> bool:
    lines = text.lower().splitlines()
    return sum(1 for l in lines[:50] if any(k in l for k in ["user:", "assistant:", "you:", "chatgpt:"])) > 2


def classify(name: str, paths: Optional[PathConfig] = None, remote: Optional[RemoteConfig] = None) -> dict:
    paths = paths or PathConfig.from_file()
    remote = remote or RemoteConfig.from_file()

    text = get_parsed_text(name, paths)
    doc_type = "chatlog" if looks_like_chatlog(text) else "standard"
    metadata = summarize_text(text, doc_type=doc_type, config=remote)

    stub_path = paths.metadata / f"{name}.stub.json"
    if stub_path.exists():
        stub = json.loads(stub_path.read_text("utf-8"))
        metadata.update(stub)

    validate_metadata(metadata)
    save_metadata_s3(remote.bucket_name, f"{remote.prefixes['metadata']}{name}.meta.json", metadata)
    return metadata


def classify_large(name: str, paths: Optional[PathConfig] = None, remote: Optional[RemoteConfig] = None) -> dict:
    paths = paths or PathConfig.from_file()
    remote = remote or RemoteConfig.from_file()

    parsed_name = name if name.endswith(".txt") else Path(name).stem + ".txt"
    content = get_parsed_text(parsed_name, paths)
    chunks = chunk_text(content)

    metadata_blocks = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
        try:
            metadata = summarize_text(chunk, config=remote)
            validate_metadata(metadata)
            metadata_blocks.append(metadata)
        except Exception as e:
            print(f"Chunk {i+1} failed: {e}")

    if not metadata_blocks:
        raise ValueError("No valid metadata returned from chunks.")

    merged = merge_metadata_blocks(metadata_blocks)

    stub_path = paths.metadata / f"{parsed_name}.stub.json"
    if stub_path.exists():
        stub = json.loads(stub_path.read_text("utf-8"))
        merged.update(stub)

    validate_metadata(merged)
    save_metadata_s3(remote.bucket_name, f"{remote.prefixes['metadata']}{parsed_name}.meta.json", merged)
    return merged


def pipeline_from_upload(file_name: str, parsed_name: Optional[str] = None) -> dict:
    upload_file(file_name, parsed_name)
    txt_name = parsed_name or Path(file_name).stem.replace(" ", "_").replace("-", "_").lower() + ".txt"
    return classify(txt_name)
