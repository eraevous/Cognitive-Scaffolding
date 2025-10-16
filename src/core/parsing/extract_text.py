"""Utilities for extracting plain text from common document formats."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from core.utils.logger import get_logger

logger = get_logger(__name__)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_markdown(path: Path) -> str:
    try:  # pragma: no cover - optional dependency
        import markdown  # type: ignore[import]

        html = markdown.markdown(path.read_text(encoding="utf-8"))
        return html
    except Exception:  # pragma: no cover - fallback to plain text
        logger.warning("markdown package unavailable; returning raw text for %s", path)
        return path.read_text(encoding="utf-8")


def _read_docx(path: Path) -> str:
    try:  # pragma: no cover - optional dependency
        from docx import Document  # type: ignore[import]

        doc = Document(str(path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    except Exception as exc:  # pragma: no cover - fallback when dependency missing
        raise ValueError(f"Unable to read DOCX file {path}: {exc}") from exc


def _read_pdf(path: Path) -> str:
    try:  # pragma: no cover - optional dependency
        import fitz  # type: ignore[import]

        text_chunks: list[str] = []
        with fitz.open(str(path)) as document:
            for page in document:
                text_chunks.append(page.get_text())
        return "\n".join(text_chunks)
    except Exception as exc:  # pragma: no cover - fallback when dependency missing
        raise ValueError(f"Unable to read PDF file {path}: {exc}") from exc


_READERS: dict[str, Callable[[Path], str]] = {
    ".txt": _read_text,
    ".md": _read_markdown,
    ".markdown": _read_markdown,
    ".docx": _read_docx,
    ".pdf": _read_pdf,
}


def extract_text(file_path: Path | str) -> str:
    """Return UTF-8 text extracted from ``file_path``.

    Unsupported extensions raise :class:`ValueError` so callers can surface
    actionable feedback in the CLI layer.
    """

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(path)
    reader = _READERS.get(path.suffix.lower())
    if reader is None:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    return reader(path)


__all__ = ["extract_text"]
