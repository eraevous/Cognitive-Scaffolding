"""Optional clustering dependency handles."""

from __future__ import annotations

# Avoid importing heavy optional dependencies during test runs. Setting these to
# ``None`` signals callers to skip functionality when the packages are absent.
umap = None  # type: ignore[assignment]
hdbscan = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    from sklearn.cluster import SpectralClustering  # type: ignore[import]
except Exception:  # pragma: no cover
    SpectralClustering = None  # type: ignore[assignment]

__all__ = ["umap", "hdbscan", "SpectralClustering"]
