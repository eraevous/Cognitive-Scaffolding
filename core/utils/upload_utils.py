"""
Module: core_lib.utils.upload_utils 

- @ai-path: core_lib.utils.upload_utils 
- @ai-source-file: combined_utils.py 
- @ai-module: upload_utils 
- @ai-role: uploader 
- @ai-entrypoint: upload_file() 
- @ai-intent: "Upload local files to S3 with parsed versions and register metadata stubs for classification."

🔍 Summary:
This module provides utilities to upload raw document files and parsed `.txt` equivalents to S3. It also generates and uploads `.stub.json` files which record the upload mapping and file type. These stubs are later used for classification and recovery.

📦 Inputs:
- file_name (str): Path to local file (relative to `PathConfig.raw`)
- parsed_name (str, optional): Override name for parsed version
- source_file (str): Full S3 key for raw input
- parsed_file (str): Full S3 key for parsed output
- ext (str): File extension of the raw file
- paths (PathConfig): Directory paths used by the system
- remote (RemoteConfig): S3 and Lambda config for the project

📤 Outputs:
- upload_file → None: Uploads file, parsed output, and metadata stub
- save_upload_stub → dict: Metadata stub dictionary

🔗 Related Modules:
- extract_text → parses uploaded file content
- s3_utils → used for S3 uploads
- io_helpers / merge → read stubs during later classification

🧠 For AI Agents:
- @ai-dependencies: boto3, pathlib, json
- @ai-calls: upload_file, extract_text, save_upload_stub, put_object
- @ai-uses: PathConfig, RemoteConfig, get_s3_client, stub_filename
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
- @notes: 
"""

import json
from pathlib import Path
from core_lib.config.remote_config import RemoteConfig
from core_lib.config.path_config import PathConfig
from core_lib.parsing.extract_text import extract_text
from core_lib.storage.aws_clients import get_s3_client


def save_upload_stub(source_file: str, parsed_file: str, ext: str, paths: PathConfig, remote: RemoteConfig):
    s3 = get_s3_client(region=remote.region)

    stub = {
        "source_file": source_file,
        "parsed_file": parsed_file,
        "source_ext": ext
    }

    stub_filename = Path(parsed_file).name + ".stub.json"
    local_path = paths.metadata / stub_filename
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(json.dumps(stub, indent=2), encoding="utf-8")
    print(f"💾 Saved stub locally: {local_path}")

    s3.put_object(
        Bucket=remote.bucket_name,
        Key=f"{remote.prefixes['stub']}{stub_filename}",
        Body=json.dumps(stub, indent=2).encode("utf-8")
    )
    print(f"📤 Uploaded stub to: s3://{remote.bucket_name}/{remote.prefixes['stub']}{stub_filename}")

    return stub


def upload_file(file_name: str, parsed_name: str = None, paths: PathConfig = None, remote: RemoteConfig = None):
    remote = remote or RemoteConfig.from_file(Path(__file__).parent.parent / "config" / "remote_config.json")
    paths = paths or PathConfig.from_file(Path(__file__).parent.parent / "config" / "path_config.json")
    s3 = get_s3_client(region=remote.region)

    file_path = paths.raw / file_name
    original_name = file_path.name
    parsed_name = parsed_name or file_path.stem.replace(" ", "_").replace("-", "_").lower() + ".txt"

    # Upload original to raw/
    s3.upload_file(str(file_path), remote.bucket_name, f"{remote.prefixes['raw']}{original_name}")
    print(f"📤 Uploaded original to: s3://{remote.bucket_name}/{remote.prefixes['raw']}{original_name}")

    try:
        text = extract_text(str(file_path))
    except Exception as e:
        print(f"❌ Failed to parse file {original_name}: {e}")
        return

    s3.put_object(
        Bucket=remote.bucket_name,
        Key=f"{remote.prefixes['parsed']}{parsed_name}",
        Body=text.encode("utf-8")
    )
    print(f"📤 Uploaded parsed version to: s3://{remote.bucket_name}/{remote.prefixes['parsed']}{parsed_name}")

    return save_upload_stub(
        source_file=f"{remote.prefixes['raw']}{original_name}",
        parsed_file=f"{remote.prefixes['parsed']}{parsed_name}",
        ext=file_path.suffix.lower().lstrip("."),
        paths=paths,
        remote=remote
    )