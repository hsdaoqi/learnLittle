"""多轮问答：把本会话近期对话带进检索和改写。

当前问题还没落库，所以这里只用已经保存的历史。
先按轮数取窗口，再按 Token 配额从新到旧截断。
检索用「近期对话 + 当前问题」；改写另外看原文历史。
窗口外旧对话由记忆压缩做成里程碑摘要，另附在提示里。
"""

from __future__ import annotations

from typing import Any

from app.config import Settings
from app.rag.token_budget import TokenBudget, count_message


def clip_text(text: str, max_chars: int) -> str:
    raw = " ".join((text or "").split())
    if max_chars <= 0 or len(raw) <= max_chars:
        return raw
    return raw[: max(max_chars - 1, 0)].rstrip() + "…"


def take_recent_messages(messages: list[Any], max_rounds: int) -> list[Any]:
    if max_rounds <= 0 or not messages:
        return []
    limit = max_rounds * 2
    return list(messages)[-limit:]


def _role_label(role: str) -> str:
    if role == "user":
        return "用户"
    if role == "assistant":
        return "助手"
    return role or "未知"


def format_history_block(messages: list[Any], max_chars_per_msg: int) -> str:
    lines: list[str] = []
    for item in messages:
        if isinstance(item, dict):
            role = item.get("role") or ""
            content = item.get("content") or ""
        else:
            role = getattr(item, "role", "") or ""
            content = getattr(item, "content", "") or ""
        text = clip_text(content, max_chars_per_msg)
        if not text:
            continue
        lines.append(f"{_role_label(role)}：{text}")
    return "\n".join(lines)


def expand_retrieval_query(question: str, history_block: str) -> str:
    query = (question or "").strip()
    history = (history_block or "").strip()
    if not history:
        return query
    return f"近期对话：\n{history}\n\n当前问题：{query}"


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


def fit_messages_to_budget(
    messages: list[Any], quota: int, max_chars: int
) -> list[dict]:
    """从最新消息向前累加，超出配额则丢掉更旧的。最新一条即使超配额也保留。"""
    if quota <= 0 or not messages:
        return []
    selected: list[dict] = []
    used = 2
    for item in reversed(list(messages)):
        role, content = _role_and_content(item)
        text = clip_text(content, max_chars)
        if not text:
            continue
        tokens = count_message(text)
        if selected and used + tokens > quota:
            break
        selected.append({"role": role, "content": text})
        used += tokens
    selected.reverse()
    return selected


def select_history_messages(
    messages: list[Any],
    settings: Settings,
    *,
    rag_text: str | None = None,
) -> list[dict]:
    if settings.chat_history_rounds <= 0:
        return []
    recent = take_recent_messages(messages, settings.chat_history_rounds)
    clipped = []
    for item in recent:
        role, content = _role_and_content(item)
        text = clip_text(content, settings.chat_history_max_chars)
        if text:
            clipped.append({"role": role, "content": text})
    quota = TokenBudget.from_settings(settings).history_quota(rag_text)
    return fit_messages_to_budget(clipped, quota, settings.chat_history_max_chars)
