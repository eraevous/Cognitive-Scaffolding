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


from core.config.path_config import PathConfig
from core.config.remote_config import RemoteConfig
from core.storage.aws_clients import get_s3_client
from core.utils.lambda_summary import (
    invoke_summary,
    invoke_chatlog_summary,
    unpack_lambda_claude_result
)
from core.metadata.schema import validate_metadata
from core.storage.s3_utils import save_metadata_s3
from pathlib import Path
import json


remote = RemoteConfig.from_file(Path(__file__).parent.parent / "config" / "remote_config.json")
s3_meta_path = lambda name: f"{remote.prefixes['metadata']}{name}.meta.json"


def classify(name: str, paths: PathConfig = None, remote: RemoteConfig = None) -> dict:
    """
    Classify a single parsed document (chatlog or regular) and save metadata to S3.

    Args:
        name (str): Name of parsed file (txt only)
        paths (PathConfig): Optional paths to override default config
        remote (RemoteConfig): Optional AWS config to override default

    Returns:
        dict: Final validated metadata block
    """
    paths = paths or PathConfig.from_file("path_config.json")
    
    if isinstance(remote, (str, Path)):
        remote = RemoteConfig.from_file(remote)
    elif remote is None:
        remote = RemoteConfig.from_file(Path(__file__).parent.parent / "config" / "remote_config.json")


    s3 = get_s3_client(region=remote.region)

    key = f"{paths.parsed.name}/{name}"
    print(f"\nKey = {key}\nBucket = {remote.bucket_name}")
    response = s3.get_object(Bucket=remote.bucket_name, Key=key)
    content = response["Body"].read().decode("utf-8")

    def looks_like_chatlog(text: str) -> bool:
        lines = text.lower().splitlines()
        return sum(1 for l in lines[:50] if any(k in l for k in ["user:", "assistant:", "you:", "chatgpt:"])) > 2

    # Summarize
    raw = invoke_chatlog_summary(name) if looks_like_chatlog(content) else invoke_summary(name)
    metadata = json.loads(raw) if isinstance(raw, str) else raw
    validate_metadata(metadata)

    # Attach stub if available
    stub_path = paths.metadata / f"{name}.stub.json"
    if stub_path.exists():
        stub = json.loads(stub_path.read_text(encoding="utf-8"))
        metadata.update(stub)

    s3_key = f"{paths.metadata.name}/{name}.meta.json"
    save_metadata_s3(remote.bucket_name, s3_key, metadata, s3=s3)

    return metadata

def classify_large(name: str, paths: PathConfig = PathConfig()) -> dict:
    """
    Classify a large file in multiple chunks and upload merged metadata to S3.

    Args:
        name (str): Raw or parsed filename

    Returns:
        dict: Final merged metadata block
    """
    parsed_name = resolve_parsed_filename(name)
    content = get_parsed_text(parsed_name)
    chunks = chunk_text(content)

    metadata_blocks = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            continue
        if len(chunk) > 16000:
            continue

        chunk_name = f"{Path(name).stem}_chunk{i+1}.txt"
        raw = invoke_summary(chunk_name, override_text=chunk)
        try:
            meta = json.loads(raw)
            validate_metadata(meta)
            metadata_blocks.append(meta)
        except Exception as e:
            print(f"Failed to classify chunk {i+1}: {e}")

    if not metadata_blocks:
        raise ValueError("No valid metadata returned from chunk classification")

    merged = merge_metadata_blocks(metadata_blocks)

    # Attach stub
    stub_path = paths.metadata / f"{parsed_name}.stub.json"
    if stub_path.exists():
        stub = json.loads(stub_path.read_text(encoding="utf-8"))
        merged.update(stub)

    save_metadata_s3(remote.bucket_name, s3_meta_path(parsed_name), merged)
    return merged
