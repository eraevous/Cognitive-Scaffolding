"""
📦 Module: core_lib.utils.upload_utils
- @ai-path: core_lib.utils.upload_utils
- @ai-source-file: combined_utils.py
- @ai-role: Uploader Utilities
- @ai-intent: "Upload local files to S3 with parsed versions and register metadata stubs for classification."

🔍 Module Summary:
This module consolidates file upload logic into S3 workflows. It handles uploading raw and parsed documents, 
generates `.stub.json` metadata mappings, and uploads those stubs for downstream classification. 
Resilient against parse errors and supports configurable local/remote paths.

🗂️ Contents:

| Name               | Type     | Purpose                                          |
|:-------------------|:---------|:-------------------------------------------------|
| save_upload_stub    | Function | Save and upload stub metadata linking source and parsed files. |
| upload_file         | Function | Upload a file (raw and parsed) and generate its stub. |

🧠 For AI Agents:
- @ai-dependencies: boto3, pathlib, json
- @ai-uses: extract_text, PathConfig, RemoteConfig, get_s3_client
- @ai-tags: upload, s3, stub-metadata, document-pipeline

⚙️ Meta:
- @ai-version: 0.4.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Move upload_file and stub generation to shared utils
- @change-summary: Consolidated upload flow with robust metadata stub registration
- @notes: ""

👤 Human Overview:
    - Context: Needed when submitting documents to cloud processing pipelines while preserving raw/parsed linkage.
    - Change Caution: If stub uploads fail but document uploads succeed, system integrity may degrade silently.
    - Future Hints: Extend stub format to include upload timestamps, original size, or content hash for better validation.
"""


import json
from pathlib import Path

from core.config import PATH_CONFIG_PATH, REMOTE_CONFIG_PATH, PathConfig, RemoteConfig
from core.logger import get_logger
from core.parsing.extract_text import extract_text
from core.storage.aws_clients import get_s3_client

logger = get_logger(__name__)


def save_upload_stub(
    source_file: str,
    parsed_file: str,
    ext: str,
    paths: PathConfig,
    remote: RemoteConfig,
):
    s3 = get_s3_client(region=remote.region)

    stub = {"source_file": source_file, "parsed_file": parsed_file, "source_ext": ext}

    stub_filename = Path(parsed_file).name + ".stub.json"
    local_path = paths.metadata / stub_filename
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(json.dumps(stub, indent=2), encoding="utf-8")
    logger.info("Saved stub locally: %s", local_path)

    s3.put_object(
        Bucket=remote.bucket_name,
        Key=f"{remote.prefixes['stub']}{stub_filename}",
        Body=json.dumps(stub, indent=2).encode("utf-8"),
    )
    logger.info(
        "Uploaded stub to: s3://%s/%s%s",
        remote.bucket_name,
        remote.prefixes["stub"],
        stub_filename,
    )

    return stub


def upload_file(
    file_name: str,
    parsed_name: str = None,
    paths: PathConfig = None,
    remote: RemoteConfig = None,
):
    remote = remote or RemoteConfig.from_file(REMOTE_CONFIG_PATH)
    paths = paths or PathConfig.from_file(PATH_CONFIG_PATH)
    s3 = get_s3_client(region=remote.region)

    file_path = paths.raw / file_name
    original_name = file_path.name
    parsed_name = (
        parsed_name
        or file_path.stem.replace(" ", "_").replace("-", "_").lower() + ".txt"
    )

    # Upload original to raw/
    s3.upload_file(
        str(file_path), remote.bucket_name, f"{remote.prefixes['raw']}{original_name}"
    )
    logger.info(
        "Uploaded original to: s3://%s/%s%s",
        remote.bucket_name,
        remote.prefixes["raw"],
        original_name,
    )

    try:
        text = extract_text(str(file_path))
    except Exception as e:
        logger.error("Failed to parse file %s: %s", original_name, e)
        return

    s3.put_object(
        Bucket=remote.bucket_name,
        Key=f"{remote.prefixes['parsed']}{parsed_name}",
        Body=text.encode("utf-8"),
    )
    logger.info(
        "Uploaded parsed version to: s3://%s/%s%s",
        remote.bucket_name,
        remote.prefixes["parsed"],
        parsed_name,
    )

    return save_upload_stub(
        source_file=f"{remote.prefixes['raw']}{original_name}",
        parsed_file=f"{remote.prefixes['parsed']}{parsed_name}",
        ext=file_path.suffix.lower().lstrip("."),
        paths=paths,
        remote=remote,
    )
