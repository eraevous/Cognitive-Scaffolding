#__________________________________________________________________
# File: __init__.py
"""Public API for the :mod:`core.memory` package."""

from .frame_store import FrameStore

__all__ = ["FrameStore"]


"""Public API for the :mod:`core.memory` package."""

from .frame_store import FrameStore

__all__ = ["FrameStore"]

#__________________________________________________________________
# File: frame_store.py
# No docstring found

from pathlib import Path
from typing import Optional
import json

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
#__________________________________________________________________
# File: memory_proxy.py
# No docstring found

# core/memory/memory_proxy.py

import os
import re
from pathlib import Path
from typing import List, Dict

INTENT_DIR = Path("intents")

def extract_metadata_from_intent(filepath: Path) -> Dict:
    """Extract ISO date, path, and first lines from an .intent.md file."""
    match = re.search(r"(\d{4}-\d{2}-\d{2})__([a-zA-Z0-9_/.]+)\.intent\.md", filepath.name)
    if not match:
        return {}
    date, module_path = match.groups()
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    summary = ""
    for line in lines:
        if line.strip().startswith("###"):
            summary = line.strip().lstrip("#").strip()
            break

    return {
        "path": str(filepath),
        "date": date,
        "module": module_path,
        "summary": summary,
        "content": "".join(lines),
    }

def load_all_intents() -> List[Dict]:
    files = INTENT_DIR.glob("*.intent.md")
    return [extract_metadata_from_intent(f) for f in files if extract_metadata_from_intent(f)]

def find_relevant_intents(prompt: str, intents: List[Dict], top_n: int = 3) -> List[Dict]:
    """Naive keyword + substring match for now. Replace with embeddings for full RAG later."""
    prompt_lower = prompt.lower()
    scored = []
    for intent in intents:
        score = sum(1 for token in prompt_lower.split() if token in intent["content"].lower())
        scored.append((score, intent))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [item[1] for item in scored[:top_n] if item[0] > 0]