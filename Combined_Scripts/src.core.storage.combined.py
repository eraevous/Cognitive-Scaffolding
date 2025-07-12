#__________________________________________________________________
# File: __init__.py
# No docstring found


#__________________________________________________________________
# File: aws_clients.py
"""
📦 Module: core_lib.storage.aws_clients
- @ai-path: core_lib.storage.aws_clients
- @ai-source-file: combined_storage.py
- @ai-role: AWS Client Provider
- @ai-intent: "Provide reusable, profile-aware boto3 clients for AWS service access."

🔍 Module Summary:
This module defines simple factory functions to initialize `boto3` clients for AWS services like S3 and Lambda. 
Clients can be configured with optional AWS profiles (e.g., for local dev) and target regions (default "us-east-1"), 
supporting flexibility across deployment environments.

🗂️ Contents:

| Name              | Type     | Purpose                               |
|:------------------|:---------|:--------------------------------------|
| get_s3_client      | Function | Create a boto3 client for Amazon S3.  |
| get_lambda_client  | Function | Create a boto3 client for AWS Lambda. |

🧠 For AI Agents:
- @ai-dependencies: boto3
- @ai-uses: Session, client
- @ai-tags: boto3, aws, cloud, s3, lambda

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add reusable AWS session client functions
- @change-summary: Initialize boto3 clients with optional profile and region support
- @notes: ""

👤 Human Overview:
    - Context: Used when consistent, optionally profile-scoped AWS clients are needed across modules.
    - Change Caution: Ensure AWS credentials and profile configurations are managed securely.
    - Future Hints: Extend to support additional AWS services if needed (e.g., DynamoDB, SNS).
"""

"""
📦 Module: core_lib.storage.aws_clients
- @ai-path: core_lib.storage.aws_clients
- @ai-source-file: combined_storage.py
- @ai-role: AWS Client Provider
- @ai-intent: "Provide reusable, profile-aware boto3 clients for AWS service access."

🔍 Module Summary:
This module defines simple factory functions to initialize `boto3` clients for AWS services like S3 and Lambda. 
Clients can be configured with optional AWS profiles (e.g., for local dev) and target regions (default "us-east-1"), 
supporting flexibility across deployment environments.

🗂️ Contents:

| Name              | Type     | Purpose                               |
|:------------------|:---------|:--------------------------------------|
| get_s3_client      | Function | Create a boto3 client for Amazon S3.  |
| get_lambda_client  | Function | Create a boto3 client for AWS Lambda. |

🧠 For AI Agents:
- @ai-dependencies: boto3
- @ai-uses: Session, client
- @ai-tags: boto3, aws, cloud, s3, lambda

⚙️ Meta:
- @ai-version: 0.2.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add reusable AWS session client functions
- @change-summary: Initialize boto3 clients with optional profile and region support
- @notes: ""

👤 Human Overview:
    - Context: Used when consistent, optionally profile-scoped AWS clients are needed across modules.
    - Change Caution: Ensure AWS credentials and profile configurations are managed securely.
    - Future Hints: Extend to support additional AWS services if needed (e.g., DynamoDB, SNS).
"""


from typing import Optional

import boto3


def get_s3_client(profile: Optional[str] = None, region: str = "us-east-1") -> boto3.client:
    """
    Create and return a boto3 S3 client.

    Args:
        profile (str, optional): AWS CLI profile name
        region (str): AWS region

    Returns:
        boto3.client: Initialized S3 client
    """
    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        session = boto3.Session(region_name=region)

    return session.client("s3")


def get_lambda_client(profile: Optional[str] = None, region: str = "us-east-1") -> boto3.client:
    """
    Create and return a boto3 Lambda client.

    Args:
        profile (str, optional): AWS CLI profile name
        region (str): AWS region

    Returns:
        boto3.client: Initialized Lambda client
    """
    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        session = boto3.Session(region_name=region)

    return session.client("lambda")#__________________________________________________________________
# File: local.py
"""
📦 Module: core_lib.storage.local_utils
- @ai-path: core_lib.storage.local_utils
- @ai-source-file: combined_storage.py
- @ai-role: File I/O Utilities
- @ai-intent: "Read and write local JSON files to support metadata storage and configuration."

🔍 Module Summary:
This module provides simple helper functions for saving and loading dictionaries to and from JSON files on disk, 
using UTF-8 encoding. Intended for use cases like metadata caching, configuration persistence, and 
intermediate storage in local environments.

🗂️ Contents:

| Name        | Type     | Purpose                              |
|:------------|:---------|:-------------------------------------|
| save_json   | Function | Save a dictionary as a JSON file.    |
| load_json   | Function | Load a dictionary from a JSON file.  |

🧠 For AI Agents:
- @ai-dependencies: json, pathlib
- @ai-uses: Path, open, dump, load
- @ai-tags: json, file-io, metadata, utility

⚙️ Meta:
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add JSON load/save utilities for local disk persistence
- @change-summary: Standardize file-based JSON I/O
- @notes: ""

👤 Human Overview:
    - Context: Useful for persisting lightweight data structures locally between processing stages.
    - Change Caution: Paths should be validated externally to avoid writing over critical files.
    - Future Hints: Add atomic save operations or backup file support for better resilience.
"""

"""
📦 Module: core_lib.storage.local_utils
- @ai-path: core_lib.storage.local_utils
- @ai-source-file: combined_storage.py
- @ai-role: File I/O Utilities
- @ai-intent: "Read and write local JSON files to support metadata storage and configuration."

🔍 Module Summary:
This module provides simple helper functions for saving and loading dictionaries to and from JSON files on disk, 
using UTF-8 encoding. Intended for use cases like metadata caching, configuration persistence, and 
intermediate storage in local environments.

🗂️ Contents:

| Name        | Type     | Purpose                              |
|:------------|:---------|:-------------------------------------|
| save_json   | Function | Save a dictionary as a JSON file.    |
| load_json   | Function | Load a dictionary from a JSON file.  |

🧠 For AI Agents:
- @ai-dependencies: json, pathlib
- @ai-uses: Path, open, dump, load
- @ai-tags: json, file-io, metadata, utility

⚙️ Meta:
- @ai-version: 0.1.0
- @ai-generated: true
- @ai-verified: false

📝 Human Collaboration:
- @human-reviewed: false
- @human-edited: false
- @last-commit: Add JSON load/save utilities for local disk persistence
- @change-summary: Standardize file-based JSON I/O
- @notes: ""

👤 Human Overview:
    - Context: Useful for persisting lightweight data structures locally between processing stages.
    - Change Caution: Paths should be validated externally to avoid writing over critical files.
    - Future Hints: Add atomic save operations or backup file support for better resilience.
"""



import json
from pathlib import Path
from typing import Union


def save_json(path: Union[str, Path], data: dict) -> None:
    """
    Save a dictionary as pretty-printed JSON to a file.

    @ai-role: saver
    @ai-intent: "Write JSON content from a dict to a file"

    Args:
        path (Union[str, Path]): Destination file path
        data (dict): Data to save
    """
    path = Path(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(path: Union[str, Path]) -> dict:
    """
    Load JSON data from a file and return as a dict.

    @ai-role: loader
    @ai-intent: "Read file contents and parse into dict"

    Args:
        path (Union[str, Path]): Path to JSON file

    Returns:
        dict: Loaded JSON data
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)#__________________________________________________________________
# File: s3_utils.py
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
from pathlib import Path

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
        Bucket=bucket,
        Key=key,
        Body=json.dumps(metadata, indent=2).encode("utf-8")
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


def download_file_from_s3(s3_filename: str, local_path: str, prefix: str = "raw/") -> str:
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
            s3.delete_object(Bucket=remote.bucket_name, Key=obj["Key"])#__________________________________________________________________
# File: upload_local.py
# No docstring found

import json
from pathlib import Path

from core.config.config_registry import get_path_config
from core.config.path_config import PathConfig
from core.parsing.extract_text import extract_text

paths = get_path_config()

def prepare_document_for_processing(
    file_path: Path,
    parsed_name: str = None,
) -> dict:
    """
    Convert a raw document into parsed text and save a stub locally.

    Args:
        file_path (Path): Full path to the raw file
        parsed_name (str): Optional override for parsed .txt filename
        paths (PathConfig): Directory configuration

    Returns:
        dict: Stub metadata linking source and parsed files
    """
    file_path = Path(file_path) 
    paths.raw.mkdir(parents=True, exist_ok=True)
    paths.parsed.mkdir(parents=True, exist_ok=True)
    paths.metadata.mkdir(parents=True, exist_ok=True)

    original_name = file_path.name
    parsed_name = parsed_name or file_path.stem.replace(" ", "_").replace("-", "_").lower() + ".txt"

    # Copy raw file
    dest_raw = paths.raw / original_name
    dest_raw.write_bytes(file_path.read_bytes())

    # Extract text and save parsed file
    try:
        text = extract_text(str(file_path))
    except Exception as e:
        raise ValueError(f"Failed to extract text from {original_name}: {e}")

    dest_parsed = paths.parsed / parsed_name
    dest_parsed.write_text(text, encoding="utf-8")

    # Write stub
    stub = {
        "source_file": str(dest_raw),
        "parsed_file": str(dest_parsed),
        "source_ext": file_path.suffix.lower().lstrip(".")
    }

    stub_file = paths.metadata / f"{parsed_name}.stub.json"
    stub_file.write_text(json.dumps(stub, indent=2), encoding="utf-8")

    print(f"Saved stub locally: {stub_file}")
    print(f"Uploaded parsed version to: {dest_parsed}")

    return stub


def upload_file(
    file_path: Path,
    parsed_name: str = None,
) -> dict:
    """
    Alias for prepare_document_for_processing.
    Maintained for compatibility with legacy calls.
    """
    return prepare_document_for_processing(file_path, parsed_name)#__________________________________________________________________
# File: upload_s3.py
# No docstring found

import json
from pathlib import Path

from core.config.config_registry import get_path_config
from core.config.path_config import PathConfig
from core.config.remote_config import RemoteConfig
from core.parsing.extract_text import extract_text
from core.storage.aws_clients import get_s3_client

paths = get_path_config()


def upload_file_to_s3(
    file_path: Path,
    parsed_name: str = None,
    remote: RemoteConfig = None
) -> dict:
    """
    Alias for push_document_to_s3.
    Maintained for compatibility with legacy calls.
    """
    return push_document_to_s3(file_path, parsed_name, paths, remote)


def push_document_to_s3(
    file_path: Path,
    parsed_name: str = None,
    remote: RemoteConfig = None
) -> dict:
    """
    Upload raw + parsed file to S3, along with a metadata stub.

    Args:
        file_path (Path): Full path to local document
        parsed_name (str): Optional name override for parsed .txt
        paths (PathConfig): Local path configuration
        remote (RemoteConfig): AWS config

    Returns:
        dict: Uploaded stub metadata
    """
    remote = remote or RemoteConfig.from_file()
    s3 = get_s3_client(region=remote.region)

    original_name = file_path.name
    parsed_name = parsed_name or file_path.stem.replace(" ", "_").replace("-", "_").lower() + ".txt"

    text = extract_text(str(file_path))

    # Upload raw
    s3.upload_file(str(file_path), remote.bucket_name, f"{remote.prefixes['raw']}{original_name}")

    # Upload parsed
    s3.put_object(
        Bucket=remote.bucket_name,
        Key=f"{remote.prefixes['parsed']}{parsed_name}",
        Body=text.encode("utf-8")
    )

    stub = {
        "source_file": f"s3://{remote.bucket_name}/{remote.prefixes['raw']}{original_name}",
        "parsed_file": f"s3://{remote.bucket_name}/{remote.prefixes['parsed']}{parsed_name}",
        "source_ext": file_path.suffix.lower().lstrip(".")
    }

    s3.put_object(
        Bucket=remote.bucket_name,
        Key=f"{remote.prefixes['stub']}{parsed_name}.stub.json",
        Body=json.dumps(stub, indent=2).encode("utf-8")
    )

    return stub

