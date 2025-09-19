import json
from pathlib import Path
from typing import Optional

from core.config.config_registry import get_path_config


class FrameStore:
    """Simple file-based frame storage for memory injection."""

    def __init__(self, path: Optional[Path] = None):
        paths = get_path_config()
        self.path = path or paths.output / "frames"
        self.path.mkdir(parents=True, exist_ok=True)

    def save_frame(self, frame_id: str, text: str) -> Path:
        fpath = self.path / f"{frame_id}.json"
        fpath.write_text(json.dumps({"text": text}), encoding="utf-8")
        return fpath

    def load_frame(self, frame_id: str) -> str:
        fpath = self.path / f"{frame_id}.json"
        if fpath.exists():
            data = json.loads(fpath.read_text())
            return data.get("text", "")
        return ""

    def inject_memory(self, text: str, frame_ids: list[str]) -> str:
        fragments = []
        for fid in frame_ids:
            fragment = self.load_frame(fid)
            if fragment:
                fragments.append(fragment)
        if fragments:
            return "\n".join(fragments) + "\n" + text
        return text
