"""Shared constants for core modules."""

from __future__ import annotations

from typing import Dict

# --------------------------------------------------------------------------- #
#  Storage prefixes and schema defaults
# --------------------------------------------------------------------------- #

DEFAULT_S3_PREFIXES: Dict[str, str] = {
    "raw": "raw/",
    "parsed": "parsed/",
    "stub": "stub/",
    "metadata": "metadata/",
}
"""Fallback S3 prefixes keyed by storage role."""

DEFAULT_S3_DOWNLOAD_PREFIX: str = DEFAULT_S3_PREFIXES["raw"]
"""Default prefix used when downloading files from S3."""

DEFAULT_METADATA_SCHEMA_PATH: str = "config/metadata_schema.json"
"""Relative path to the default metadata schema file."""

# --------------------------------------------------------------------------- #
#  Error message templates
# --------------------------------------------------------------------------- #

ERROR_SCHEMA_FILE_NOT_FOUND = "Schema file not found at: {path}"
ERROR_PATH_CONFIG_NOT_FOUND = "Path config file not found at: {path}"
ERROR_REMOTE_CONFIG_NOT_FOUND = "Remote config file not found at: {path}"
ERROR_REMOTE_CONFIG_MISSING_FIELDS = "Missing required remote config fields: {fields}"
ERROR_PATH_RESOLVE_FAILURE = "Failed to resolve path relative to root: {value}\n{error}"
ERROR_PROMPT_FILE_NOT_FOUND = "Prompt file not found: {path}"
ERROR_BUDGET_EXCEEDED = "Budget exceeded for completion request"
ERROR_OPENAI_RESPONSE_NOT_JSON = "Could not parse OpenAI response as JSON:\n{response}"
ERROR_S3_KEY_NOT_FOUND = "S3 key not found: {key}"
ERROR_TOKENIZER_NOT_FOUND = "Tokenizer '{spec}' not found. Available: {available}"
ERROR_CONVERSATIONS_EXPORT_MISSING = "conversations.json not found in export"
ERROR_CONVERSATION_EXTRACTION_FAILED = "Failed to extract messages from conversation"
