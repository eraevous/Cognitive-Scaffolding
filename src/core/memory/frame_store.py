"""Module: core.memory.frame_store
Simple JSON-based storage for conversational frames.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from core.config.config_registry import get_path_config


def _frames_dir() -> Path:
    paths = get_path_config()
    frames = paths.output / "frames"
    frames.mkdir(parents=True, exist_ok=True)
    return frames


def save_frame(text: str, metadata: Optional[Dict[str, Any]] = None, frame_id: Optional[str] = None) -> str:
    """Persist a text snippet and metadata as a frame file."""
    frames = _frames_dir()
    if not frame_id:
        frame_id = f"frame_{len(list(frames.glob('frame_*.json'))):04d}"
    data = {"text": text, "metadata": metadata or {}}
    (frames / f"{frame_id}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return frame_id


def load_frame(frame_id: str) -> Dict[str, Any]:
    """Load a stored frame by ID."""
    path = _frames_dir() / f"{frame_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Frame not found: {frame_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_frames() -> List[str]:
    """Return all frame IDs present in the store."""
    return sorted(p.stem for p in _frames_dir().glob('frame_*.json'))
