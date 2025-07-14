"""
📦 Module: core.parsing.normalize
- @ai-path: core.parsing.normalize
- @ai-source-file: normalize.py
- @ai-role: utility
- @ai-intent: "Standardize strings for safe filenames"
- @schema-version: 0.2
"""

import re


def normalize_filename(name: str) -> str:
    """Return a lowercase, path-safe slug."""
    sanitized = re.sub(r"[\\/:*?\"<>|]", "_", name)
    sanitized = sanitized.replace(" ", "_").replace("-", "_")
    sanitized = re.sub(r"[^\w]+", "_", sanitized)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    return sanitized.lower()
