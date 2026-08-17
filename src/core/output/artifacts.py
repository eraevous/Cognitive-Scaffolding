from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Iterable

from core.configuration.path_config import PathConfig


def slugify(value: str, max_length: int = 64) -> str:
    """Create a stable, filesystem-friendly label from query text."""

    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        return "untitled"
    return slug[:max_length].strip("-") or "untitled"


def resolve_artifact_path(
    out: Path,
    paths: PathConfig,
    kind: str,
    query: str,
    *,
    suffix: str = ".md",
) -> Path:
    """Resolve an output file path from a file, directory, or extensionless path."""

    if out.suffix:
        return out

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}__{kind}__{slugify(query)}{suffix}"
    if out == Path("."):
        return paths.output / kind / filename
    return out / filename


def write_artifact(
    out: Path,
    paths: PathConfig,
    kind: str,
    query: str,
    lines: Iterable[str],
    *,
    suffix: str = ".md",
) -> Path:
    """Write text output to a resolved artifact path."""

    path = resolve_artifact_path(out, paths, kind, query, suffix=suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines).rstrip() + "\n"
    path.write_text(content, encoding="utf-8")
    return path
