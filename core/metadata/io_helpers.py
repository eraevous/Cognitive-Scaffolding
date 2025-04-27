"""
Module: core_lib.metadata.io_helpers 

- @ai-path: core_lib.metadata.io_helpers 
- @ai-source-file: combined_metadata.py 
- @ai-module: io_helpers 
- @ai-role: parsed_text_resolver 
- @ai-entrypoint: get_parsed_text() 
- @ai-intent: "Return parsed document content by resolving from local file, stub + raw reparsing, or S3 fallback."

🔍 Summary: Attempts to return the parsed text content for a document. It first checks for a local parsed `.txt` file. If missing, it looks for a metadata stub that links to the original raw file and attempts to re-parse it. As a last resort, it downloads the parsed file from S3 using the standard remote config. This function ensures maximum recovery and fault tolerance during preprocessing.

📦 Inputs:
- name (str): Base document name (with or without `.txt`)

📤 Outputs:
- str: Full parsed text content of the file

🔗 Related Modules:
- extract_text → used to regenerate missing parsed files
- s3_utils → used for download fallback
- upload_utils → writes stub pointing to parsed/raw locations

🧠 For AI Agents:
- @ai-dependencies: pathlib, json, fitz, extract_text, boto3
- @ai-calls: exists, read_text, extract_text, download_file, get_s3_client, open, json.load
- @ai-uses: Path, remote.prefixes, parsed_path, stub_path, raw_path
- @ai-tags: fallback, resilience, file-recovery, S3-aware

⚙️ Meta: 
- @ai-version: 0.2.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Added fallback logic to retrieve missing parsed text 
- @change-summary: Implements stub and S3 fallback for document parsing 
- @notes: 
"""


import json
from pathlib import Path
from core_lib.config.remote_config import RemoteConfig
from core_lib.parsing.extract_text import extract_text
from core_lib.storage.s3_utils import get_s3_client


remote = RemoteConfig.from_file(Path(__file__).parent.parent / "config" / "remote_config.json")

def get_parsed_text(name: str) -> str:
    parsed_path = Path(remote.prefixes["parsed"]) / name
    stub_path = Path(remote.prefixes["metadata"]) / f"{name}.stub.json"

    if parsed_path.exists():
        return parsed_path.read_text(encoding="utf-8")

    if stub_path.exists():
        with stub_path.open("r", encoding="utf-8") as f:
            stub = json.load(f)

        raw_file = Path(stub["source_file"]).name
        raw_path = Path(remote.prefixes["raw"]) / raw_file

        if raw_path.exists():
            print(f"♻️ Re-parsing from raw file: {raw_file}")
            text = extract_text(str(raw_path))
            parsed_path.write_text(text, encoding="utf-8")
            return text

    print(f"⬇️ Downloading parsed file from S3: {name}")
    s3 = get_s3_client()
    s3.download_file(Bucket=remote.bucket_name, Key=f"{remote.prefixes['parsed']}{name}", Filename=str(parsed_path))
    return parsed_path.read_text(encoding="utf-8")