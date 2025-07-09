# core/cadence/cadence_controller.py

from enum import Enum
from datetime import datetime
import logging

CadenceTriggerKeywords = {
    "run": ["fix", "debug", "proceed", "continue", "implement", "optimize"],
    "drift": ["explore", "compare", "reflect", "design", "refactor", "ask"],
}

class CadenceMode(Enum):
    RUN = "run"
    DRIFT = "drift"

class CadenceController:
    def __init__(self):
        self.current_mode = CadenceMode.DRIFT
        self.history = []

    def detect_mode_from_prompt(self, prompt: str) -> CadenceMode:
        """Heuristic detection based on prompt content."""
        prompt_lower = prompt.lower()
        for keyword in CadenceTriggerKeywords["run"]:
            if keyword in prompt_lower:
                return CadenceMode.RUN
        for keyword in CadenceTriggerKeywords["drift"]:
            if keyword in prompt_lower:
                return CadenceMode.DRIFT
        return CadenceMode.DRIFT  # Default fallback

    def set_mode(self, mode: CadenceMode, reason: str = ""):
        """Manually set cadence mode, with logging."""
        self.current_mode = mode
        self._log_transition(mode, reason)

    def get_current_mode(self) -> CadenceMode:
        return self.current_mode

    def _log_transition(self, mode: CadenceMode, reason: str):
        timestamp = datetime.utcnow().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "mode": mode.value,
            "reason": reason,
        }
        self.history.append(log_entry)
        logging.info(f"[Cadence] Switched to {mode.value.upper()} — {reason}")

    def suggest_behavior(self) -> str:
        """Give guidance based on current mode."""
        if self.current_mode == CadenceMode.RUN:
            return "Focus on code execution, completeness, and logic. Minimize commentary unless `.intent.md` trails are needed."
        else:
            return "Reflect on design intent, surface integration points, validate `.purpose.md`, and annotate reasoning."

