"""按实际上下文预算选择未摘要历史，保留用户与助手角色。"""

from __future__ import annotations

from typing import Any

from app.config import Settings
from app.rag.token_budget import TokenCounter, count_message


def _role_and_content(item: Any) -> tuple[str, str]:
    if isinstance(item, dict):
        return item.get("role") or "", item.get("content") or ""
    return getattr(item, "role", "") or "", getattr(item, "content", "") or ""


def rag_context_text(hits: list[dict]) -> str:
    parts = []
    for hit in hits or []:
        text = (hit.get("content") or "").strip()
        if text:
            parts.append(text)
    return "\n".join(parts)


def build_agent_history(
    messages: list[Any], settings: Settings, *, rag_text: str = "",
    question: str = "", summary: str = "", summarized_through: int = 0,
) -> list[dict]:
    """Use full-role messages, not the legacy fixed-round display window."""
    # Stage-20 .env files used zero before agents existed; zero now means auto.
    scratchpad = settings.token_agent_scratchpad_reserve
    if scratchpad <= 0:
        scratchpad = 4000
    quota = max(
        0,
        settings.token_model_context_size
        - settings.token_system_prompt
        - settings.token_safety_margin
        - scratchpad
        - TokenCounter.count(question)
        - TokenCounter.count(summary)
        - TokenCounter.count(rag_text),
    )
    pending = []
    for item in messages:
        message_id = item.get("id", 0) if isinstance(item, dict) else getattr(item, "id", 0)
        if summarized_through and message_id and message_id <= summarized_through:
            continue
        role, content = _role_and_content(item)
        if role in {"user", "assistant"} and content:
            pending.append({"role": role, "content": content})
    selected: list[dict] = []
    used = 2
    for item in reversed(pending):
        size = count_message(item["content"])
        if used + size > quota:
            if not selected and quota > 8:
                # An individual oversized message must not exhaust the model context.
                text = item["content"]
                while text and count_message(text) + used > quota:
                    text = text[: max(0, len(text) * 3 // 4)]
                if text:
                    selected.append({**item, "content": text})
            break
        selected.append(item)
        used += size
    return list(reversed(selected))
