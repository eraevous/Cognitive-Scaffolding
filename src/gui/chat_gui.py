"""Streamlit-based chat interface for OpenAI models."""

from __future__ import annotations

from typing import Dict, List

import streamlit as st  # type: ignore
import tiktoken
from openai import OpenAI

from core.configuration.config_registry import get_remote_config
from core.llm.invoke import LLM_COMPLETION_COST_PER_1K  # type: ignore
from core.llm.invoke import LLM_PROMPT_COST_PER_1K
from core.utils.budget_tracker import get_budget_tracker  # type: ignore


def run_openai_chat(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o",
    temperature: float = 0.5,
    max_tokens: int = 300,
    api_key: str | None = None,
) -> str:
    """Send conversation history to OpenAI and return the assistant reply."""
    remote = get_remote_config()
    client = OpenAI(api_key=api_key or remote.openai_api_key)
    tracker = get_budget_tracker()
    if tracker:
        enc = tiktoken.encoding_for_model(model)
        joined = "".join(m["content"] for m in messages)
        prompt_tokens = len(enc.encode(joined, disallowed_special=()))
        est_cost = prompt_tokens / 1000 * LLM_PROMPT_COST_PER_1K.get(
            model, 0
        ) + max_tokens / 1000 * LLM_COMPLETION_COST_PER_1K.get(model, 0)
        if not tracker.check(est_cost):
            raise RuntimeError("Budget exceeded for chat request")

    response = client.chat.completions.create(
        model=model,
        messages=messages,  # type: ignore[arg-type]
        temperature=temperature,
        max_tokens=max_tokens,
    )
    content = response.choices[0].message.content or ""
    return content.strip()


def main() -> None:
    """Launch the Streamlit conversation UI."""
    st.title("LLM Chat")

    if "messages" not in st.session_state:
        st.session_state.messages = []  # type: ignore[assignment]

    for msg in st.session_state.messages:  # type: ignore[attr-defined]
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Send a message"):
        st.session_state.messages.append({"role": "user", "content": prompt})  # type: ignore[attr-defined]
        with st.spinner("Thinking..."):
            reply = run_openai_chat(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})  # type: ignore[attr-defined]
        with st.chat_message("assistant"):
            st.write(reply)


if __name__ == "__main__":  # pragma: no cover
    main()
