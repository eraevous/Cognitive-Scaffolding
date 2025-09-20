"""
📦 Module: core.parsing.openai_export
- @ai-path: core.parsing.openai_export
- @ai-source-file: openai_export.py
- @ai-role: parser
- @ai-intent: "Parse ChatGPT Data Export zip to extract conversation transcripts and user prompts."
- @ai-version: 0.1.3
- @ai-generated: true
- @ai-verified: false
- @human-reviewed: false

This module reads the `conversations.json` file included in an OpenAI ChatGPT
"Data Export" archive and writes each conversation to its own text file.
Additionally, it saves a corresponding file containing only the user messages
for quick prompt reuse or duplicate detection.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from core.constants import (
    ERROR_CONVERSATION_EXTRACTION_FAILED,
    ERROR_CONVERSATIONS_EXPORT_MISSING,
)

from .normalize import normalize_filename


def _load_conversations(export_path: Path) -> List[Dict]:
    """Load conversation list from a zip archive or directory."""
    if export_path.is_dir():
        conv_path = export_path / "conversations.json"
        with conv_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    with zipfile.ZipFile(export_path) as zf:
        try:
            # Standard export has files under a top-level directory. Look for the
            # conversations file anywhere in the archive to support both
            # flattened and nested zips.
            name = next(
                (n for n in zf.namelist() if n.endswith("conversations.json")),
                "conversations.json",
            )
            with zf.open(name) as f:
                return json.load(f)
        except KeyError as exc:
            raise FileNotFoundError(ERROR_CONVERSATIONS_EXPORT_MISSING) from exc


def _extract_messages(convo: Dict) -> Iterable[Tuple[str, str]]:
    """Return ordered (role, text) tuples for a conversation.

    Malformed nodes are skipped so that parsing continues even if
    individual messages are missing or not structured as expected.
    Non-string content parts are ignored to handle multimodal nodes.
    """

    mapping = convo.get("mapping", {})
    node_id = convo.get("current_node")
    path: List[Tuple[str, str]] = []
    while node_id:
        node = mapping.get(node_id)
        if not node:
            break
        msg = node.get("message")
        if not msg or not isinstance(msg, dict):
            node_id = node.get("parent")
            continue
        if msg.get("author", {}).get("role") != "system":
            role = msg["author"].get("role", "unknown")
            parts = msg.get("content", {}).get("parts") or []
            text_parts = [p for p in parts if isinstance(p, str)]
            if text_parts:
                text = "\n".join(text_parts)
                path.append((role, text))
        node_id = node.get("parent")
    return reversed(path)


def parse_chatgpt_export(
    export_path: Path, out_dir: Path, *, markdown: bool = False
) -> List[Dict[str, Path]]:
    """Parse conversations and write text + prompt files.

    Parameters
    ----------
    export_path: Path
        Path to the `.zip` export or the extracted folder.
    out_dir: Path
        Directory to write conversation and prompt files.
    markdown: bool, optional
        If True, save conversation transcripts as Markdown rather than plain text.
    Returns
    -------
    List[Dict[str, Path]]
        List of dictionaries describing output file paths per conversation.
    Raises
    ------
    ValueError
        If message extraction fails for a conversation.
    """

    export_path = Path(export_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_dir = out_dir / "prompts"
    prompt_dir.mkdir(exist_ok=True)

    conversations = _load_conversations(export_path)
    outputs: List[Dict[str, Path]] = []
    ext = "md" if markdown else "txt"
    for idx, convo in enumerate(conversations):
        title = convo.get("title") or f"conversation_{idx}"
        slug = normalize_filename(title)[:32]
        convo_file = out_dir / f"{idx:04d}_{slug}.{ext}"
        prompt_file = prompt_dir / f"{idx:04d}_{slug}_prompts.txt"
        lines = []
        prompts = []
        msgs = _extract_messages(convo)
        if msgs is None:
            raise ValueError(ERROR_CONVERSATION_EXTRACTION_FAILED)
        for role, text in msgs:
            clean = text.strip()
            if markdown:
                lines.append(f"**{role.title()}:** {clean}")
            else:
                lines.append(f"{role.upper()}: {clean}")
            if role == "user":
                prompts.append(clean)

        convo_file.write_text("\n".join(lines), encoding="utf-8")
        prompt_file.write_text("\n".join(prompts), encoding="utf-8")
        outputs.append({"conversation": convo_file, "prompts": prompt_file})

    return outputs
