"""对话卡片：把笔记搜索结果收成前端能解析的编号列表。

用户引用笔记时，消息里会带 <referenced_notes>。问答主句用可见问题，
完整引用块交给 Agent，避免标题和检索被整段卡片正文冲掉。
"""

from __future__ import annotations

import re

CONTEXT_MARKER = "以下是用户引用的笔记"
REF_BLOCK_RE = re.compile(r"<referenced_notes>\s*.*?\s*</referenced_notes>", re.DOTALL)


def one_line(text: str, max_chars: int = 30) -> str:
    collapsed = " ".join((text or "").split())
    if len(collapsed) <= max_chars:
        return collapsed
    return collapsed[:max_chars].rstrip() + "…"


def format_note_search_cards(query: str, items: list[dict]) -> str:
    """items: title / note_id / excerpt。空列表返回固定未找到文案。"""
    if not items:
        return "未找到相关笔记"
    keyword = (query or "").strip() or "关键词"
    lines = [f'找到 {len(items)} 篇与"{keyword}"相关的笔记：']
    for index, item in enumerate(items, start=1):
        title = (item.get("title") or "未命名").strip() or "未命名"
        note_id = (item.get("note_id") or "").strip()
        excerpt = one_line(item.get("excerpt") or "", 30)
        head = f"{index}. {title}"
        if note_id:
            head += f" (ID: {note_id})"
        if excerpt:
            head += f" - {excerpt}"
        lines.append(head)
    return "\n".join(lines)


def visible_question(message: str) -> str:
    """去掉引用卡片后的用户原问题，给标题和检索用。"""
    text = message or ""
    marker = text.find(CONTEXT_MARKER)
    if marker < 0:
        return text.strip()
    prefix = text[:marker]
    prefix = re.sub(r"\s*[-—–]+\s*$", "", prefix).strip()
    return prefix or text.strip()


def referenced_notes_prompt(message: str) -> str:
    """有引用块时抽出给 Agent 的上下文；没有则空串。"""
    text = message or ""
    if CONTEXT_MARKER not in text and not REF_BLOCK_RE.search(text):
        return ""
    return text.strip()
