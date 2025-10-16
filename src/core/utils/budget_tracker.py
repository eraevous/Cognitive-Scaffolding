"""Minimal budget tracking helper for API usage."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class BudgetTracker:
    """Accumulate approximate spend and guard against runaway costs."""

    max_usd: float
    spent_usd: float = 0.0
    month: Optional[int] = None
    log_path: Optional[Path] = None

    def check(self, cost: float) -> bool:
        """Record ``cost`` and return ``False`` when the budget is exceeded."""

        current_month = time.gmtime().tm_mon
        if self.month is not None and current_month != self.month:
            self.spent_usd = 0.0
        self.month = current_month

        self.spent_usd += float(cost)
        if self.log_path is not None:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self.log_path.write_text(f"{self.month}:{self.spent_usd:.4f}\n")

        return self.spent_usd <= self.max_usd

    def reset(self) -> None:
        """Reset the tracker to zero spend for the current month."""

        self.spent_usd = 0.0
        self.month = time.gmtime().tm_mon
        if self.log_path and self.log_path.exists():
            self.log_path.unlink()


_singleton: Optional[BudgetTracker] = None


def get_budget_tracker() -> BudgetTracker:
    """Return a singleton :class:`BudgetTracker` configured from the environment."""

    global _singleton
    if _singleton is None:
        limit = float(os.environ.get("OPENAI_BUDGET_USD", "100.0"))
        log_file = os.environ.get("OPENAI_BUDGET_LOG")
        log_path = Path(log_file).expanduser() if log_file else None
        _singleton = BudgetTracker(max_usd=limit, log_path=log_path)
    return _singleton


__all__ = ["BudgetTracker", "get_budget_tracker"]
