import json
import os
import time
from pathlib import Path


class BudgetTracker:
    """Track and limit API spending across operations."""

    def __init__(self, max_usd: float, log_path: Path | None = None):
        self.max_usd = max_usd
        self.log_path = log_path
        self.spent = 0.0
        self.month = time.strftime("%Y-%m")

    def check(self, cost: float) -> bool:
        now = time.strftime("%Y-%m")
        if now != self.month:
            self.reset(now)
        if self.spent + cost > self.max_usd:
            return False
        self.spent += cost
        self._persist()
        return True

    def reset(self, month: str | None = None) -> None:
        self.month = month or time.strftime("%Y-%m")
        self.spent = 0.0
        self._persist()

    def _persist(self) -> None:
        if not self.log_path:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump({"month": self.month, "spent": self.spent}, f)


_instance: "BudgetTracker | None" = None


def get_budget_tracker() -> "BudgetTracker | None":
    """Return a singleton ``BudgetTracker`` from environment variables.

    Environment variables:
    - ``OPENAI_BUDGET_USD``: monthly budget limit in dollars.
    - ``OPENAI_BUDGET_LOG``: optional path to persist spend log.
    """
    global _instance
    if _instance is None:
        budget = os.getenv("OPENAI_BUDGET_USD")
        if budget:
            log_path = Path(os.getenv("OPENAI_BUDGET_LOG", "budget_log.json"))
            _instance = BudgetTracker(float(budget), log_path=log_path)
        else:
            _instance = None
    return _instance
