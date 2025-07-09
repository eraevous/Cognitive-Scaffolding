#__________________________________________________________________
# File: token_stats.py
"""
Quick token-count and distribution helper for Mosaic files.

Usage (from code):

    from core.analysis.token_stats import TokenStats
    stats = TokenStats.from_glob(
        path_pattern="parsed/**/*.txt",
        tokenizer="tiktoken:gpt-4o-mini"
    )
    print(stats.describe())

The same logic powers the `mosaic tokens` CLI command.
"""

"""
Quick token-count and distribution helper for Mosaic files.

Usage (from code):

    from core.analysis.token_stats import TokenStats
    stats = TokenStats.from_glob(
        path_pattern="parsed/**/*.txt",
        tokenizer="tiktoken:gpt-4o-mini"
    )
    print(stats.describe())

The same logic powers the `mosaic tokens` CLI command.
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean, median, quantiles
from typing import Callable, Dict, List

from transformers import AutoTokenizer

# --------------------------------------------------------------------------- #
#  Registry of tokenizers
# --------------------------------------------------------------------------- #

def _tiktoken_loader(model_name: str) -> Callable[[str], int]:
    import tiktoken
    enc = tiktoken.encoding_for_model(model_name)
    return lambda text: len(enc.encode(text, disallowed_special=()))

def _hf_loader(model_name: str):
    tok = AutoTokenizer.from_pretrained(model_name)
    return lambda text: len(tok.encode(text))

TOKENIZERS: Dict[str, Callable[[str], Callable[[str], int]]] = {
    # key format:  "<family>:<model>"
    "tiktoken:gpt-4o-mini": _tiktoken_loader,
    "tiktoken:gpt-3-small": _tiktoken_loader,
    "huggingface:roberta-base": _hf_loader
    # register more like:
    # "huggingface:bert-base-uncased": lambda _: hf_loader("bert-base-uncased")
}

def get_tokenizer(spec: str) -> Callable[[str], int]:
    family, model = spec.split(":", 1)
    if spec not in TOKENIZERS:
        raise ValueError(
            f"Tokenizer '{spec}' not found.  "
            f"Available: {list(TOKENIZERS.keys())}"
        )
    return TOKENIZERS[spec](model)

# --------------------------------------------------------------------------- #
#  Stats dataclass
# --------------------------------------------------------------------------- #

@dataclass
class TokenStats:
    counts: List[int] = field(default_factory=list)
    file_paths: List[Path] = field(default_factory=list)

    # ---------- construction helpers ----------
    @classmethod
    def from_glob(cls, path_pattern: str, tokenizer: str) -> "TokenStats":
        tk = get_tokenizer(tokenizer)
        paths = sorted(Path(".").glob(path_pattern))
        counts: List[int] = []

        for p in paths:
            try:
                counts.append(tk(p.read_text()))
            except Exception as e:
                print(f"[warn] skipping {p}: {e}")

        return cls(counts=counts, file_paths=paths)

    # ---------- summary ----------
    def describe(self, percentiles=(0.25, 0.5, 0.75)) -> str:
        if not self.counts:
            return "No files processed."

        qs = quantiles(self.counts, n=4, method="inclusive")
        lines = [
            f"Files analysed: {len(self.counts)}",
            f"Min / Max     : {min(self.counts):,} / {max(self.counts):,}",
            f"Mean / Median : {mean(self.counts):,.1f} / {median(self.counts):,}",
            f"25-50-75 pct  : " + " / ".join(f"{int(q):,}" for q in qs),
        ]
        return "\n".join(lines)

    # ---------- ext. hooks ----------
    def to_dict(self):
        return {
            "files": [str(p) for p in self.file_paths],
            "counts": self.counts,
        }
    
    @classmethod
    def from_dir(cls, folder: Path, pattern: str = "*.txt", tokenizer: str = "tiktoken:gpt-4o-mini"):
        """Count tokens in every file matching `pattern` under `folder` (recursive)."""
        tk = get_tokenizer(tokenizer)
        paths = sorted(folder.rglob(pattern))          # <= absolute-path friendly
        counts = []
        for p in paths:
            try:
                counts.append(tk(p.read_text()))
            except Exception as e:
                print(f"[warn] skipping {p}: {e}")
        return cls(counts=counts, file_paths=paths)
