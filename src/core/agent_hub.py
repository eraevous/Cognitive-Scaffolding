"""Lightweight orchestration for cooperative agent sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from core.retrieval.retriever import Retriever
from core.utils import budget_tracker
from core.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class AgentSession:
    """Minimal agent wrapper that consults a shared retriever."""

    role: str
    retriever: Retriever
    history: List[str] = field(default_factory=list)

    def step(self, prompt: str, *, k: int = 3) -> str:
        """Return a response using retrieval-augmented context."""

        hits = self.retriever.query(prompt, k=k, return_text=True)
        context = [chunk for _, _, chunk in hits if isinstance(chunk, str) and chunk]
        if context:
            response = f"[{self.role}] {prompt}\n" + "\n".join(context[:2])
        else:
            response = f"[{self.role}] {prompt}"
        self.history.append(response)
        return response


def run_agents(
    prompt: str,
    roles: Iterable[str],
    retriever: Retriever,
    *,
    steps: int = 1,
    k: int = 3,
) -> Dict[str, List[str]]:
    """Iterate cooperative agent sessions sharing ``retriever``."""

    tracker = budget_tracker.get_budget_tracker()
    sessions = [AgentSession(role=role, retriever=retriever) for role in roles]
    transcripts: Dict[str, List[str]] = {session.role: [] for session in sessions}

    for step_index in range(steps):
        for session in sessions:
            if not tracker.check(0.0):
                logger.warning("Budget exceeded; stopping agent loop")
                return transcripts
            response = session.step(prompt, k=k)
            transcripts[session.role].append(response)
            logger.info("Agent %s step %s complete", session.role, step_index + 1)
    return transcripts


__all__ = ["AgentSession", "run_agents"]
