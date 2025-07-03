from pathlib import Path
import json
import time


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
