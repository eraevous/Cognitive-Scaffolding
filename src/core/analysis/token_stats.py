"""Token counting utilities with pluggable tokenizer backends."""

from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Sequence

import typer

logger = logging.getLogger(__name__)

Tokenizer = Callable[[str], int]
TokenizerFactory = Callable[[str], Tokenizer]

_DEFAULT_SPEC = "tiktoken:text-embedding-3-small"
_FACTORIES: Dict[str, TokenizerFactory] = {}
_DEFAULT_MODELS: Dict[str, str] = {
    "tiktoken": "text-embedding-3-small",
    "huggingface": "gpt2",
}


def register_tokenizer(family: str, factory: TokenizerFactory, *, default_model: str | None = None) -> None:
    _FACTORIES[family] = factory
    if default_model is not None:
        _DEFAULT_MODELS[family] = default_model


def get_tokenizer(spec: str = _DEFAULT_SPEC) -> Tokenizer:
    family, _, model = spec.partition(":")
    if family not in _FACTORIES:
        raise ValueError(f"Unknown tokenizer family '{family}'. Available: {sorted(_FACTORIES)}")
    model_name = model or _DEFAULT_MODELS.get(family)
    if not model_name:
        raise ValueError(f"Tokenizer family '{family}' requires a model name")
    return _FACTORIES[family](model_name)


def _register_defaults() -> None:
    try:  # pragma: no cover - optional dependency
        import tiktoken  # type: ignore[import]

        def _tiktoken_factory(model: str) -> Tokenizer:
            encoding = tiktoken.encoding_for_model(model)

            def _count(text: str) -> int:
                return len(encoding.encode(text, disallowed_special=()))

            return _count

        register_tokenizer("tiktoken", _tiktoken_factory, default_model="text-embedding-3-small")
    except Exception:  # pragma: no cover - dependency optional
        logger.warning("tiktoken unavailable; tokenizer registry missing 'tiktoken'")

    try:  # pragma: no cover - optional dependency
        from transformers import AutoTokenizer  # type: ignore[import]

        def _hf_factory(model: str) -> Tokenizer:
            tokenizer = AutoTokenizer.from_pretrained(model)

            def _count(text: str) -> int:
                return len(tokenizer.encode(text))

            return _count

        register_tokenizer("huggingface", _hf_factory, default_model="gpt2")
    except Exception:  # pragma: no cover
        logger.debug("transformers not installed; skipping huggingface tokenizer")


_register_defaults()


@dataclass(slots=True)
class TokenStats:
    files: List[Path] = field(default_factory=list)
    token_counts: List[int] = field(default_factory=list)
    errors: List[Path] = field(default_factory=list)

    def add(self, path: Path, count: int) -> None:
        self.files.append(path)
        self.token_counts.append(count)

    def record_error(self, path: Path) -> None:
        self.errors.append(path)

    def total_tokens(self) -> int:
        return sum(self.token_counts)

    def describe(self) -> str:
        if not self.token_counts:
            return "No files processed."
        counts = self.token_counts
        summary = {
            "files": len(counts),
            "total": self.total_tokens(),
            "mean": round(statistics.mean(counts), 2),
            "median": statistics.median(counts),
            "min": min(counts),
            "max": max(counts),
        }
        quartiles = statistics.quantiles(counts, n=4, method="inclusive") if len(counts) >= 4 else None
        parts = [
            f"files={summary['files']}",
            f"total={summary['total']}",
            f"mean={summary['mean']}",
            f"median={summary['median']}",
            f"min={summary['min']}",
            f"max={summary['max']}",
        ]
        if quartiles:
            parts.append("quartiles=" + ",".join(str(int(q)) for q in quartiles))
        if self.errors:
            parts.append(f"errors={len(self.errors)}")
        return "; ".join(parts)

    def to_dict(self) -> Dict[str, object]:
        return {
            "files": [str(path) for path in self.files],
            "token_counts": list(self.token_counts),
            "errors": [str(path) for path in self.errors],
            "total_tokens": self.total_tokens(),
        }


def _collect_files(path_pattern: str | Path) -> List[Path]:
    if isinstance(path_pattern, Path):
        return [path_pattern]
    base = Path()
    return sorted(base.glob(str(path_pattern)))


def collect_token_stats(path_pattern: str = "parsed/**/*.txt", tokenizer: str = _DEFAULT_SPEC) -> TokenStats:
    counter = get_tokenizer(tokenizer)
    stats = TokenStats()
    for path in _collect_files(path_pattern):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            logger.warning("Skipping unreadable file: %s", path)
            stats.record_error(path)
            continue
        count = counter(text)
        stats.add(path, count)
    return stats


def _render_histogram(counts: Sequence[int], bins: int = 10) -> str:
    if not counts:
        return ""
    try:  # pragma: no cover - optional dependency
        import numpy as np

        hist, edges = np.histogram(counts, bins=bins)
    except Exception:  # pragma: no cover - fallback without numpy
        minimum, maximum = min(counts), max(counts)
        span = max(1, maximum - minimum)
        width = max(1, span // bins)
        edges = [minimum + i * width for i in range(bins + 1)]
        hist = [0] * bins
        for value in counts:
            index = min((value - minimum) // width, bins - 1)
            hist[index] += 1
    lines = []
    for bucket, edge in zip(hist, edges):
        bar = "#" * bucket
        lines.append(f"{int(edge):>6}: {bar}")
    return "\n".join(lines)


@app.command()
def tokens(
    path_pattern: str = typer.Argument("parsed/**/*.txt"),
    tokenizer: str = typer.Option(_DEFAULT_SPEC, help="Tokenizer spec family:model"),
    show_hist: bool = typer.Option(False, help="Render histogram"),
) -> None:
    stats = collect_token_stats(path_pattern, tokenizer)
    typer.echo(stats.describe())
    if show_hist:
        typer.echo(_render_histogram(stats.token_counts))


__all__ = [
    "TokenStats",
    "collect_token_stats",
    "get_tokenizer",
    "register_tokenizer",
    "tokens",
    "app",
]
