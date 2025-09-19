"""
📦 Module: core_lib.storage.s3_utils
- @ai-path: core_lib.storage.s3_utils
- @ai-source-file: combined_storage.py
- @ai-role: S3 Interface Utilities
- @ai-intent: "Provide validated save/load and administrative file operations to/from S3 buckets using project config."

🔍 Module Summary:
This module implements higher-level S3 utilities for saving validated metadata, downloading files, and cleaning 
S3 folders. It leverages reusable AWS client factories and schema validation, ensuring safe cloud interactions. 
Designed to support workflows needing reliable cloud storage and retrieval pipelines.

🗂️ Contents:

| Name                   | Type     | Purpose                                 |
|:------------------------|:---------|:----------------------------------------|
| save_metadata_s3        | Function | Validate and upload metadata to S3.     |
| load_metadata_s3        | Function | Load and validate metadata from S3.     |
| download_file_from_s3   | Function | Download files from S3 to local storage.|
| clear_s3_folders        | Function | Bulk delete objects under S3 prefixes.  |

🧠 For AI Agents:
- @ai-dependencies: boto3, json
- @ai-uses: validate_metadata, get_s3_client, RemoteConfig
- @ai-tags: s3, cloud-storage, metadata, json, boto3, upload, cleanup

⚙️ Meta:
- @ai-version: 0.3.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add validated S3 utilities for metadata and cleanup
- @change-summary: Implements upload, load, fallback, and folder clearing via S3 config paths
- @notes: ""

👤 Human Overview:
    - Context: Used for reliable cloud persistence and recovery of metadata and document files in S3 workflows.
    - Change Caution: Misconfigured bucket names, prefixes, or credentials can cause silent failures.
    - Future Hints: Add multipart upload support for larger files and resilience against S3 rate limits.
"""


import json

from core.config.remote_config import RemoteConfig
from core.metadata.schema import validate_metadata
from core.storage.aws_clients import get_s3_client


def save_metadata_s3(bucket: str, key: str, metadata: dict, s3=None) -> None:
    """
    Validate and upload metadata to S3.

    Args:
        bucket (str): S3 bucket name
        key (str): S3 object key to write
        metadata (dict): Metadata dictionary to save
        s3 (boto3.client, optional): Injected S3 client (optional)
    """
    validate_metadata(metadata)
    s3 = s3 or get_s3_client()
    s3.put_object(
        Bucket=bucket, Key=key, Body=json.dumps(metadata, indent=2).encode("utf-8")
    )


def load_metadata_s3(bucket: str, key: str, s3=None) -> dict:
    """
    Load and validate metadata from S3.

    Args:
        bucket (str): S3 bucket name
        key (str): Key to retrieve
        s3 (boto3.client, optional): Optional S3 client

    Returns:
        dict: Parsed and validated metadata content
    """
    s3 = s3 or get_s3_client()
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        metadata = json.load(response["Body"])
        validate_metadata(metadata)
        return metadata
    except Exception as e:
        raise FileNotFoundError(f"S3 key not found: {key}") from e


def download_file_from_s3(
    s3_filename: str, local_path: str, prefix: str = "raw/"
) -> str:
    """
    Download a file from an S3 prefix to a local path.

    Args:
        s3_filename (str): Filename within the S3 prefix
        local_path (str): Local path to save the file
        prefix (str): Folder prefix in S3 (default: "raw/")

    Returns:
        str: Confirmation message with path
    """
    s3 = get_s3_client()
    full_key = f"{prefix}{s3_filename}"
    remote = RemoteConfig.from_file("remote_config.json")
    s3.download_file(Bucket=remote.bucket_name, Key=full_key, Filename=local_path)
    return f"Downloaded to {local_path}"


def clear_s3_folders(prefixes: list[str], s3=None) -> None:
    """
    Remove all files from specified S3 prefixes.

    Args:
        prefixes (list[str]): S3 folder prefixes to clear (e.g., ["raw/", "parsed/"])
        s3: Optional boto3 S3 client
    """
    s3 = s3 or get_s3_client()

    for prefix in prefixes:
        print(f"🧹 Clearing {prefix}")
        response = remote = RemoteConfig.from_file("remote_config.json")
    s3.list_objects_v2(Bucket=remote.bucket_name, Prefix=prefix)
    if "Contents" in response:
        for obj in response["Contents"]:
            print(f"  Deleting {obj['Key']}")
            s3.delete_object(Bucket=remote.bucket_name, Key=obj["Key"])
