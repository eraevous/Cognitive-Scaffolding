"""Persistent storage for short text memory frames."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


class FrameStore:
    """Store and retrieve memory fragments for prompt injection."""

    def __init__(self, path: Path | str) -> None:
        self.base_path = Path(path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _frame_path(self, frame_id: str) -> Path:
        return self.base_path / f"{frame_id}.txt"

    def save_frame(self, frame_id: str, text: str) -> Path:
        path = self._frame_path(frame_id)
        path.write_text(text, encoding="utf-8")
        return path

    def load_frame(self, frame_id: str) -> str:
        path = self._frame_path(frame_id)
        if not path.exists():
            raise FileNotFoundError(frame_id)
        return path.read_text(encoding="utf-8")

    def inject_memory(self, prompt: str, frame_ids: Iterable[str]) -> str:
        fragments = [self.load_frame(frame_id) for frame_id in frame_ids]
        fragments.append(prompt)
        return "\n".join(fragments)


__all__ = ["FrameStore"]
