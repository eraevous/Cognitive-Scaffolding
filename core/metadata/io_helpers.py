"""
📦 Module: core_lib.metadata.io_helpers
- @ai-path: core_lib.metadata.io_helpers
- @ai-source-file: combined_metadata.py
- @ai-role: Parsed Text Resolver
- @ai-intent: "Return parsed document content by resolving from local file, stub + raw reparsing, or S3 fallback."

🔍 Module Summary:
This module provides a fault-tolerant system for retrieving parsed document text. It first checks for local 
parsed files, then tries regenerating from raw sources if metadata stubs exist, and finally attempts S3 
downloads if necessary. This ensures robust handling of missing or incomplete parsed data during preprocessing.

🗂️ Contents:

| Name              | Type    | Purpose                                 |
|:------------------|:--------|:----------------------------------------|
| get_parsed_text    | Function | Recover parsed text via local or remote fallback methods. |

🧠 For AI Agents:
- @ai-dependencies: pathlib, json, boto3, fitz (for PDF parsing if used downstream)
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
- @notes: ""

👤 Human Overview:
    - Context: Used when parsed documents may be partially missing during preprocessing or ingestion.
    - Change Caution: Remote config assumptions (S3 paths) are hardcoded; breaking changes may occur if path structures change.
    - Future Hints: Support automatic stub regeneration and compression handling for large parsed files.
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