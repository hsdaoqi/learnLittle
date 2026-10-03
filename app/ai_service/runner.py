"""无模型时的关键词工具降级；真实模型问答统一走 LangChain ReAct。

测试可 set_agent_runner 注入。失败返回空，问答回退 RAG。
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Callable
from typing import Any

from app.ai_service.tool_registry import registry
from app.ai_service.tools import bind_user_tools
from app.config import Settings

logger = logging.getLogger(__name__)

AgentEvent = dict[str, Any]
AgentRunner = Callable[[str, str, Any, Settings, str], AsyncIterator[AgentEvent]]

_injected: AgentRunner | None = None

TOOL_KEYWORDS: list[tuple[str, list[str]]] = [
    ("search_notes_tool", ["搜索笔记", "查找笔记", "找笔记", "搜一下笔记", "相关笔记"]),
    (
        "get_today_reviews_tool",
        ["今日待回顾", "待复习", "今天复习", "艾宾浩斯", "回顾列表"],
    ),
    ("get_note_stats_tool", ["笔记统计", "分类统计", "有多少笔记", "笔记数量"]),
    ("get_user_info_tools", ["我是谁", "我的邮箱", "用户信息", "当前用户"]),
    ("what_time_is_now", ["现在几点", "当前时间", "今天几号", "现在时间"]),
]


def set_agent_runner(fn: AgentRunner | None) -> None:
    global _injected
    _injected = fn


def get_agent_runner() -> AgentRunner | None:
    return _injected


def match_local_tool(question: str) -> str | None:
    text = (question or "").strip()
    for name, keywords in TOOL_KEYWORDS:
        if any(key in text for key in keywords):
            return name
    return None


def should_use_agent(question: str, settings: Settings) -> bool:
    if not settings.agent_enabled:
        return False
    if _injected is not None:
        return True
    if match_local_tool(question):
        return True
    return False


async def run_local_tool(
    question: str,
    user_id: str,
    session_factory,
    settings: Settings,
    history: str = "",
) -> AsyncIterator[AgentEvent]:
    name = match_local_tool(question)
    if not name:
        return
    bound = registry.bind(bind_user_tools(user_id, session_factory))
    fn = bound.get(name)
    if fn is None:
        return
    yield {"type": "tool_start", "name": name}
    try:
        if name == "search_notes_tool":
            result = await fn(question)
        else:
            result = await fn()
    except Exception as exc:
        logger.warning("本地工具失败 %s: %s", name, exc)
        yield {"type": "tool_end", "name": name, "error": str(exc)}
        return
    yield {"type": "tool_end", "name": name, "result": result}
    yield {"type": "response", "content": result}


async def run_agent(
    question: str,
    user_id: str,
    session_factory,
    settings: Settings,
    history: str = "",
) -> AsyncIterator[AgentEvent]:
    if _injected is not None:
        async for event in _injected(
            question, user_id, session_factory, settings, history
        ):
            yield event
        return
    async for event in run_local_tool(
        question, user_id, session_factory, settings, history
    ):
        yield event
