"""Utilities for parsing ChatGPT data exports."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from core.parsing.normalize import normalize_filename

RoleMessage = Tuple[str, str]


def _read_conversations(export_path: Path) -> List[Dict[str, object]]:
    if export_path.is_dir():
        candidate = export_path / "conversations.json"
        if not candidate.exists():
            raise FileNotFoundError(candidate)
        return json.loads(candidate.read_text(encoding="utf-8"))

    with zipfile.ZipFile(export_path, "r") as archive:
        name = None
        for member in archive.namelist():
            if member.endswith("conversations.json"):
                name = member
                break
        if name is None:
            raise FileNotFoundError("conversations.json not found in export")
        with archive.open(name) as handle:
            return json.loads(handle.read().decode("utf-8"))


def _message_parts(message: dict) -> Optional[RoleMessage]:
    author = message.get("author", {}) if isinstance(message, dict) else {}
    role = str(author.get("role", "unknown")).upper()
    content = message.get("content") if isinstance(message, dict) else {}
    parts = content.get("parts") if isinstance(content, dict) else []
    texts = [part for part in parts if isinstance(part, str) and part.strip()]
    if not texts:
        return None
    if role == "SYSTEM":
        return None
    return role, "\n".join(texts).strip()


def _extract_messages(mapping: Dict[str, dict]) -> List[RoleMessage]:
    if not mapping:
        return []
    root = next((node for node in mapping.values() if node.get("parent") is None), None)
    if root is None:
        return []
    order: List[RoleMessage] = []
    current = root
    visited: set[str] = set()
    while current and current.get("id") not in visited:
        visited.add(str(current.get("id")))
        message = current.get("message")
        if message:
            parts = _message_parts(message)
            if parts is not None:
                order.append(parts)
        children = current.get("children") or []
        next_id = next((child for child in children if child in mapping), None)
        current = mapping.get(next_id) if next_id else None
    return order


def _write_conversation(
    transcript: List[RoleMessage],
    out_dir: Path,
    title: str,
    *,
    markdown: bool = False,
) -> Tuple[Path, Path]:
    slug = normalize_filename(title)
    convo_path = out_dir / f"{slug}.{'md' if markdown else 'txt'}"
    prompt_dir = out_dir / "prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = prompt_dir / f"{slug}_prompts.txt"

    lines: List[str] = []
    prompts: List[str] = []
    for role, text in transcript:
        label = role.capitalize() if markdown else role
        if markdown:
            prefix = "**{}:**".format(label)
            lines.append(f"{prefix} {text}")
        else:
            lines.append(f"{label}: {text}")
        if role.upper() == "USER":
            prompts.append(text)

    convo_path.parent.mkdir(parents=True, exist_ok=True)
    convo_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    prompt_path.write_text("\n".join(prompts), encoding="utf-8")
    return convo_path, prompt_path


def parse_chatgpt_export(
    export_path: Path | str,
    out_dir: Path | str,
    *,
    markdown: bool = False,
) -> List[Dict[str, Path]]:
    """Parse a ChatGPT export archive and write conversations to ``out_dir``."""

    export = Path(export_path)
    out_dir = Path(out_dir)
    conversations = _read_conversations(export)
    out_dir.mkdir(parents=True, exist_ok=True)

    results: List[Dict[str, Path]] = []
    for index, convo in enumerate(conversations):
        title = str(convo.get("title", f"conversation_{index}"))
        mapping = convo.get("mapping")
        if not isinstance(mapping, dict):
            continue
        transcript = _extract_messages(mapping)
        if transcript is None:
            raise ValueError("Failed to extract messages from export")
        convo_file, prompt_file = _write_conversation(
            transcript,
            out_dir,
            f"{index:04d}_{title}",
            markdown=markdown,
        )
        results.append({"conversation": convo_file, "prompts": prompt_file})
    if not results:
        raise ValueError("No conversations found in export")
    return results


__all__ = ["parse_chatgpt_export", "_extract_messages"]
