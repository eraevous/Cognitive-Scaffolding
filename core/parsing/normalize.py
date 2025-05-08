"""
📦 Module: core_lib.utils.strings
- @ai-path: core_lib.utils.strings
- @ai-source-file: combined_utils.py
- @ai-role: String Utilities
- @ai-intent: "Standardize filenames and identifiers to lowercase with underscores for safe use across the system."

🔍 Module Summary:
This module provides lightweight string normalization utilities to ensure safe, standardized filenames 
and identifiers across cloud and local systems. It primarily transforms names to lowercase and replaces 
spaces or hyphens with underscores.

🗂️ Contents:

| Name               | Type     | Purpose                                  |
|:-------------------|:---------|:-----------------------------------------|
| normalize_filename | Function | Convert names to lowercase and underscore-separated format. |

🧠 For AI Agents:
- @ai-dependencies: None
- @ai-uses: str.lower(), str.replace()
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
- @notes: ""

👤 Human Overview:
    - Context: Ensures consistent naming across document upload, storage, and retrieval pipelines.
    - Change Caution: Original case and formatting are lost; irreversible unless tracked separately.
    - Future Hints: Extend normalization options to support slug generation for web compatibility.
"""


def normalize_filename(name: str) -> str:
    return name.replace(" ", "_").replace("-", "_").lower()