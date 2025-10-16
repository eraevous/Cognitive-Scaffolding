"""Utilities for deduplicating prompt text files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from core.utils.logger import get_logger

logger = get_logger(__name__)


def _iter_prompt_lines(paths: Iterable[Path]) -> set[str]:
    unique: set[str] = set()
    for path in paths:
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                trimmed = line.strip()
                if trimmed:
                    unique.add(trimmed)
        except UnicodeDecodeError:  # pragma: no cover - defensive guard
            logger.warning("Skipping non-text prompt file: %s", path)
    return unique


def dedup_lines_in_folder(folder: Path | str, output_file: Path | str | None = None) -> Path:
    """Collect unique lines from ``folder`` and write them to ``output_file``.

    The resulting file always contains sorted lines to provide deterministic
    diffs and to ease review when prompts change.
    """

    base = Path(folder)
    if output_file is None:
        output_file = base / "deduplicated_prompts.txt"
    else:
        output_file = Path(output_file)

    candidates = list(base.rglob("*.txt")) + list(base.rglob("*.md"))
    lines = _iter_prompt_lines(candidates)
    sorted_lines = sorted(lines)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(sorted_lines), encoding="utf-8")
    logger.info("Wrote %s unique prompt lines to %s", len(sorted_lines), output_file)
    return output_file


__all__ = ["dedup_lines_in_folder"]
