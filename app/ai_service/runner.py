"""轻量 Agent：OpenAI 函数调用循环，或无密钥时走本地关键词路由。

测试可 set_agent_runner 注入。失败返回空，问答回退 RAG。
"""

from __future__ import annotations

import inspect
import json
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

from app.ai_service.tool_registry import registry
from app.ai_service.tools import bind_user_tools
from app.config import Settings

logger = logging.getLogger(__name__)

AgentEvent = dict[str, Any]
AgentRunner = Callable[[str, str, Any, Settings, str], AsyncIterator[AgentEvent]]

_injected: AgentRunner | None = None
MAX_TOOL_ROUNDS = 4

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


def _parse_args(raw: str | dict | None) -> dict:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


async def _call_tool(fn: Callable[..., Awaitable[str]], arguments: dict) -> str:
    params = inspect.signature(fn).parameters
    kwargs = {key: value for key, value in arguments.items() if key in params}
    return await fn(**kwargs)


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
    bound = bind_user_tools(user_id, session_factory)
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


async def run_openai_tools(
    question: str,
    user_id: str,
    session_factory,
    settings: Settings,
    history: str = "",
) -> AsyncIterator[AgentEvent]:
    import httpx

    bound = bind_user_tools(user_id, session_factory)
    tools = registry.openai_tools()
    system = (
        "你是学习助手。需要查笔记、统计、回顾或当前用户信息时调用工具。"
        "工具结果用简洁中文回答用户。不要编造 note_id / review_id。"
        "当 search_notes_tool 返回编号列表时，把「找到 N 篇…」和每条"
        "「N. 标题 (ID: xxx) - 摘要」原样交给用户，不要丢掉 ID。"
    )
    messages: list[dict] = [{"role": "system", "content": system}]
    if history.strip():
        messages.append({"role": "system", "content": f"近期对话：\n{history.strip()}"})
    from app.rag.note_cards import referenced_notes_prompt

    refs = referenced_notes_prompt(question)
    if refs:
        messages.append({"role": "system", "content": f"用户本轮引用了笔记：\n{refs}"})
    messages.append({"role": "user", "content": question})

    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    for _ in range(MAX_TOOL_ROUNDS):
        payload = {
            "model": settings.llm_model,
            "stream": False,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
        }
        from app.services.usage_service import UsageTimer

        timer = UsageTimer("agent", settings.llm_model)
        prompt_text = json.dumps(messages, ensure_ascii=False)
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                raise RuntimeError(
                    f"Agent LLM HTTP {resp.status_code}: {resp.text[:300]}"
                )
            data = resp.json()
            message = (data.get("choices") or [{}])[0].get("message") or {}
            await timer.finish(
                prompt_text, json.dumps(message, ensure_ascii=False), data
            )
        except Exception as exc:
            await timer.finish(prompt_text, "", success=False, error=str(exc))
            raise
        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            text = (message.get("content") or "").strip()
            if text:
                yield {"type": "response", "content": text}
            return

        messages.append(message)
        for call in tool_calls:
            function = call.get("function") or {}
            name = function.get("name") or ""
            arguments = _parse_args(function.get("arguments"))
            yield {"type": "tool_start", "name": name}
            fn = bound.get(name)
            if fn is None:
                result = f"未知工具: {name}"
                yield {"type": "tool_end", "name": name, "error": result}
            else:
                try:
                    result = await _call_tool(fn, arguments)
                    yield {"type": "tool_end", "name": name, "result": result}
                except Exception as exc:
                    result = f"工具执行失败: {exc}"
                    logger.warning("工具 %s 失败: %s", name, exc)
                    yield {"type": "tool_end", "name": name, "error": str(exc)}
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id") or name,
                    "content": result,
                }
            )


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
    if settings.llm_api_key:
        async for event in run_openai_tools(
            question, user_id, session_factory, settings, history
        ):
            yield event
        return
    async for event in run_local_tool(
        question, user_id, session_factory, settings, history
    ):
        yield event
