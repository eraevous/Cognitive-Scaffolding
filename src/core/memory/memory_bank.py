from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

from core.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_MEMORY_DIR = Path("memory_frames")


def save_frame(content: str, memory_dir: Path = DEFAULT_MEMORY_DIR) -> Path:
    """Persist a text frame for later recall."""
    memory_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    path = memory_dir / f"frame_{ts}.json"
    data = {"timestamp": ts, "content": content}
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.debug("Saved frame %s", path)
    return path


def load_recent_frames(limit: int = 5, memory_dir: Path = DEFAULT_MEMORY_DIR) -> List[str]:
    """Load recent frames for context injection."""
    if not memory_dir.exists():
        return []
    files = sorted(memory_dir.glob("frame_*.json"), reverse=True)[:limit]
    frames = []
    for p in files:
        try:
            frames.append(json.loads(p.read_text(encoding="utf-8"))['content'])
        except Exception as e:
            logger.warning("Failed to load frame %s: %s", p, e)
    return frames
