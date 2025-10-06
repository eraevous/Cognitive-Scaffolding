"""Ensure purpose documentation tracks AST-level dependencies."""

from __future__ import annotations

import csv
from pathlib import Path

MODULE_PURPOSE = {
    "core.retrieval.retriever": Path(
        "Codex_++/purpose_files/core.retrieval.retriever.purpose.md"
    ),
    "core.embeddings.embedder": Path(
        "Codex_++/purpose_files/core.embeddings.embedder.purpose.md"
    ),
    "core.configuration.path_config": Path(
        "Codex_++/purpose_files/core.configuration.path_config.purpose.md"
    ),
    "core.configuration.config_registry": Path(
        "Codex_++/purpose_files/core.configuration.config_registry.purpose.md"
    ),
    "core.constants": Path("Codex_++/purpose_files/core.constants.purpose.md"),
}

ALIAS_PREFIX = {
    "path_config": "core.configuration.path_config",
    "remote_config": "core.configuration.remote_config",
}


def _normalize_dependency(raw: str) -> str:
    raw = raw.replace("\\", ".")
    if raw.startswith("builtins"):
        return ""
    parts = raw.split(".")
    if parts[0] in {"typing"}:
        return ""
    if parts[0] in ALIAS_PREFIX:
        return ALIAS_PREFIX[parts[0]]
    if parts[0] == "core":
        if len(parts) >= 3:
            return ".".join(parts[:3])
        return ".".join(parts)
    return parts[0]


def _read_ast_dependencies(module: str) -> set[str]:
    deps: set[str] = set()
    with Path("ast_deps.csv").open(newline="") as handle:
        reader = csv.reader(handle)
        for src, dest in reader:
            src_module = src.replace("\\", ".").rsplit(".", 1)[0]
            if src_module != module:
                continue
            norm = _normalize_dependency(dest)
            if not norm or norm == module:
                continue
            deps.add(norm)
    return deps


def _read_doc_dependencies(path: Path) -> set[str]:
    for line in path.read_text().splitlines():
        if line.startswith("- @ai-dependencies:"):
            _, _, payload = line.partition(":")
            return {dep.strip() for dep in payload.split(",") if dep.strip()}
    raise AssertionError(f"Missing @ai-dependencies tag in {path}")


def test_purpose_dependencies_match_ast():
    for module, doc_path in MODULE_PURPOSE.items():
        ast_deps = _read_ast_dependencies(module)
        doc_deps = _read_doc_dependencies(doc_path)
        missing = ast_deps - doc_deps
        assert not missing, f"{module} missing dependencies: {sorted(missing)}"
