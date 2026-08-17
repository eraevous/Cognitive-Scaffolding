from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List


@dataclass
class LexicalHit:
    doc_id: str
    title: str
    score: float
    path: Path
    snippet: str


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9_']+", text.lower())


def _load_manifest_records(root: Path) -> Iterable[Dict]:
    manifest_path = root / "metadata" / "chatgpt" / "chatgpt_manifest.json"
    if not manifest_path.exists():
        return []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    records = manifest.get("records", {})
    return records.values() if isinstance(records, dict) else []


def _snippet(text: str, query: str, width: int) -> str:
    lower = text.lower()
    query_lower = query.lower()
    idx = lower.find(query_lower)
    if idx == -1:
        query_terms = _tokenize(query)
        idx = min(
            (lower.find(term) for term in query_terms if lower.find(term) != -1),
            default=0,
        )
    start = max(0, idx - width // 2)
    end = min(len(text), idx + width // 2)
    return " ".join(text[start:end].split())


def search_chatgpt_corpus(
    root: Path,
    query: str,
    *,
    k: int = 10,
    snippet_chars: int = 700,
) -> List[LexicalHit]:
    """Search a parsed ChatGPT corpus locally without external API calls."""

    root = Path(root).expanduser().resolve()
    query_terms = _tokenize(query)
    if not query_terms:
        return []

    hits: List[LexicalHit] = []
    phrase = query.lower().strip()

    for record in _load_manifest_records(root):
        parsed_rel = record.get("parsed_path")
        if not parsed_rel:
            continue
        path = root / parsed_rel
        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8")
        if not text.strip():
            continue
        lower = text.lower()
        term_hits = sum(lower.count(term) for term in query_terms)
        phrase_hits = lower.count(phrase) if len(query_terms) > 1 else 0
        if term_hits == 0 and phrase_hits == 0:
            continue

        length_norm = math.sqrt(max(len(_tokenize(text)), 1))
        score = (term_hits + phrase_hits * 5) / length_norm
        hits.append(
            LexicalHit(
                doc_id=str(record.get("key") or path.stem),
                title=str(record.get("title") or path.stem),
                score=score,
                path=path,
                snippet=_snippet(text, query, snippet_chars),
            )
        )

    return sorted(hits, key=lambda hit: hit.score, reverse=True)[:k]
