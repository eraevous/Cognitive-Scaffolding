from typing import Iterable

from core.retrieval.retriever import Retriever


class AgentSession:
    """Placeholder agent session using a shared retriever."""

    def __init__(self, role: str, retriever: Retriever):
        self.role = role
        self.retriever = retriever

    def step(self, user_msg: str) -> dict:
        # For now, just return retrieved doc IDs
        context = self.retriever.query(user_msg, k=5)
        return {"role": self.role, "context": context}


def run_agents(prompt: str, roles: Iterable[str]) -> None:
    retriever = Retriever()
    sessions = [AgentSession(role, retriever) for role in roles]
    for session in sessions:
        result = session.step(prompt)
        print(session.role, result)
