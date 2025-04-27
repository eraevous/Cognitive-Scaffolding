"""
Module: core_lib.utils.strings 

- @ai-path: core_lib.utils.strings 
- @ai-source-file: combined_utils.py 
- @ai-module: strings 
- @ai-role: string_utils 
- @ai-entrypoint: normalize_filename() 
- @ai-intent: "Standardize filenames and identifiers to lowercase with underscores for safe use across the system."

🔍 Summary:
This function transforms a filename or label by replacing spaces and dashes with underscores and converting to lowercase. It is used to create consistent keys for document tracking, metadata naming, and cluster assignment.

📦 Inputs:
- name (str): Original filename or label

📤 Outputs:
- str: Normalized, lowercase, underscore-separated identifier

🔗 Related Modules:
- upload_utils → uses to name parsed files and stubs
- cluster_map → uses to align doc_ids with filenames

🧠 For AI Agents:
- @ai-dependencies: None
- @ai-calls: str.lower(), str.replace()
- @ai-uses: name, str
- @ai-tags: normalization, string-utils, identifier-cleanup

⚙️ Meta: 
- @ai-version: 0.1.0 
- @ai-generated: true 
- @ai-verified: false

📝 Human Collaboration: 
- @human-reviewed: false 
- @human-edited: false 
- @last-commit: Add basic string cleaner for identifiers 
- @change-summary: Normalize filenames and labels for safe downstream use 
- @notes: 
"""


def normalize_filename(name: str) -> str:
    return name.replace(" ", "_").replace("-", "_").lower()