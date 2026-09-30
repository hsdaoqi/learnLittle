"""LangChain ReAct：create_agent + astream_events。

本阶段接 ReAct 流式对话。查询分类器在 chat_service 里先跑；Plan-Execute / Reflection 还不在这里。
测试可 set_react_streamer 注入，不打外网。
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator, Callable
from typing import Any

from app.ai_service.langchain_tools import build_langchain_tools
from app.config import Settings
from app.rag.note_cards import referenced_notes_prompt, visible_question

logger = logging.getLogger(__name__)

ReactStreamer = Callable[..., AsyncIterator[dict[str, Any]]]

_injected: ReactStreamer | None = None
DEFAULT_SYSTEM_PROMPT = (
    "你是学习助手。需要查笔记、统计、回顾或当前用户信息时调用工具。"
    "工具结果用简洁中文回答用户。不要编造 note_id / review_id。"
    "当 search_notes_tool 返回编号列表时，把「找到 N 篇…」和每条"
    "「N. 标题 (ID: xxx) - 摘要」原样交给用户，不要丢掉 ID。"
    "有检索资料时优先依据资料回答；资料不够就明说，不要编造文档内容。"
)
MAX_CONSECUTIVE_TOOL_CALLS = 6


def set_react_streamer(fn: ReactStreamer | None) -> None:
    global _injected
    _injected = fn


def get_react_streamer() -> ReactStreamer | None:
    return _injected


def build_react_system_prompt(
    message: str,
    *,
    rag_context: str = "",
    extra_system: str = "",
) -> str:
    parts = [DEFAULT_SYSTEM_PROMPT]
    extra = (extra_system or "").strip()
    if extra:
        parts.append(extra)
    context = (rag_context or "").strip()
    if context:
        parts.append(
            "以下是从知识库和笔记中检索到的相关内容，请在回答时优先参考：\n"
            f"<reference>\n{context}\n</reference>"
        )
    refs = referenced_notes_prompt(message)
    if refs:
        parts.append(f"用户本轮引用了笔记：\n{refs}")
    return "\n\n".join(parts)


def chunk_text(chunk: Any) -> str:
    content = getattr(chunk, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text") or "")
        return "".join(parts)
    return ""


def chunk_reasoning(chunk: Any) -> str:
    extra = getattr(chunk, "additional_kwargs", None) or {}
    if isinstance(extra, dict):
        text = extra.get("reasoning_content") or extra.get("reasoning") or ""
        if text:
            return str(text)
    return str(getattr(chunk, "reasoning_content", "") or "")


def map_langchain_event(
    event: dict[str, Any],
    *,
    consecutive_tool_calls: int,
    tool_start_times: dict[str, float],
    now: float | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """把 astream_events v2 事件收成前端能用的 thinking / response / tool_*。"""
    event_type = event.get("event")
    produced: list[dict[str, Any]] = []
    stamp = time.time() if now is None else now

    if event_type == "on_chat_model_stream":
        chunk = (event.get("data") or {}).get("chunk")
        if chunk is None:
            return produced, consecutive_tool_calls
        reasoning = chunk_reasoning(chunk)
        if reasoning:
            produced.append(
                {"type": "thinking", "stage": "thinking", "content": reasoning}
            )
        text = chunk_text(chunk)
        if text:
            consecutive_tool_calls = 0
            produced.append({"type": "response", "content": text})
        return produced, consecutive_tool_calls

    if event_type == "on_tool_start":
        name = event.get("name") or "unknown"
        consecutive_tool_calls += 1
        if consecutive_tool_calls > MAX_CONSECUTIVE_TOOL_CALLS:
            produced.append(
                {
                    "type": "error",
                    "content": "抱歉，我在处理这个问题时遇到了困难（工具调用循环），请尝试换一种方式提问。",
                }
            )
            return produced, consecutive_tool_calls
        tool_start_times[name] = stamp
        produced.append({"type": "tool_start", "name": name})
        return produced, consecutive_tool_calls

    if event_type == "on_tool_end":
        name = event.get("name") or "unknown"
        started = tool_start_times.pop(name, None)
        duration_ms = 0 if started is None else round((stamp - started) * 1000)
        output = (event.get("data") or {}).get("output")
        result = getattr(output, "content", output)
        produced.append(
            {
                "type": "tool_end",
                "name": name,
                "duration_ms": duration_ms,
                "result": "" if result is None else str(result),
            }
        )
        return produced, consecutive_tool_calls

    if event_type == "on_tool_error":
        name = event.get("name") or "unknown"
        started = tool_start_times.pop(name, None)
        duration_ms = 0 if started is None else round((stamp - started) * 1000)
        err = (event.get("data") or {}).get("error")
        produced.append(
            {
                "type": "tool_end",
                "name": name,
                "duration_ms": duration_ms,
                "error": str(err or "工具执行失败"),
            }
        )
        return produced, consecutive_tool_calls

    return produced, consecutive_tool_calls


def _create_chat_model(settings: Settings, *, enable_thinking: bool, timeout: int):
    from langchain_openai import ChatOpenAI

    kwargs: dict[str, Any] = {
        "model": settings.llm_model,
        "api_key": settings.llm_api_key,
        "base_url": settings.llm_base_url,
        "streaming": True,
        "timeout": timeout,
    }
    if enable_thinking:
        kwargs["extra_body"] = {"enable_thinking": True}
    return ChatOpenAI(**kwargs)


def _create_agent(model, tools, system_prompt: str):
    try:
        from langchain.agents import create_agent

        return create_agent(model=model, tools=tools or [], system_prompt=system_prompt)
    except ImportError:
        from langgraph.prebuilt import create_react_agent

        return create_react_agent(model, tools or [], prompt=system_prompt)


def _history_messages(history: str, summary: str) -> list:
    from langchain_core.messages import SystemMessage

    messages = []
    if (summary or "").strip():
        messages.append(SystemMessage(content=f"[历史对话摘要]\n{summary.strip()}"))
    if (history or "").strip():
        messages.append(SystemMessage(content=f"近期对话：\n{history.strip()}"))
    return messages


async def run_langchain_react(
    question: str,
    user_id: str,
    session_factory,
    settings: Settings,
    *,
    history: str = "",
    summary: str = "",
    rag_context: str = "",
    enable_thinking: bool = False,
    timeout: int | None = None,
) -> AsyncIterator[dict[str, Any]]:
    from langchain_core.messages import HumanMessage

    from app.services.usage_service import UsageTimer

    timeout = timeout or settings.llm_stream_timeout
    if enable_thinking:
        timeout = timeout * 2
    system_prompt = build_react_system_prompt(question, rag_context=rag_context)
    tools = build_langchain_tools(user_id, session_factory)
    model = _create_chat_model(
        settings, enable_thinking=enable_thinking, timeout=timeout
    )
    agent = _create_agent(model, tools, system_prompt)
    payload = {
        "messages": [
            *_history_messages(history, summary),
            HumanMessage(content=visible_question(question) or question),
        ]
    }

    accumulated: list[str] = []
    consecutive = 0
    tool_start_times: dict[str, float] = {}
    timer = UsageTimer("agent", settings.llm_model)
    prompt_text = system_prompt + "\n" + question
    try:
        import asyncio

        async with asyncio.timeout(timeout):
            async for event in agent.astream_events(payload, version="v2"):
                mapped, consecutive = map_langchain_event(
                    event,
                    consecutive_tool_calls=consecutive,
                    tool_start_times=tool_start_times,
                )
                for item in mapped:
                    if item.get("type") == "response":
                        accumulated.append(item.get("content") or "")
                    yield item
                    if item.get("type") == "error":
                        await timer.finish(
                            prompt_text,
                            "".join(accumulated),
                            success=False,
                            error=item.get("content"),
                        )
                        return
        await timer.finish(prompt_text, "".join(accumulated))
        yield {"type": "stream_done", "full_response": "".join(accumulated)}
    except TimeoutError:
        logger.warning("ReAct 响应超时 (timeout=%ss)", timeout)
        await timer.finish(
            prompt_text, "".join(accumulated), success=False, error="timeout"
        )
        yield {"type": "error", "content": "生成超时，请稍后重试"}
    except Exception as exc:
        logger.warning("ReAct 执行失败: %s", exc)
        await timer.finish(
            prompt_text, "".join(accumulated), success=False, error=str(exc)
        )
        yield {"type": "error", "content": "生成失败，请稍后重试"}


async def run_react(
    question: str,
    user_id: str,
    session_factory,
    settings: Settings,
    *,
    history: str = "",
    summary: str = "",
    rag_context: str = "",
    enable_thinking: bool = False,
    timeout: int | None = None,
) -> AsyncIterator[dict[str, Any]]:
    if _injected is not None:
        async for event in _injected(
            question,
            user_id,
            session_factory,
            settings,
            history=history,
            summary=summary,
            rag_context=rag_context,
            enable_thinking=enable_thinking,
        ):
            yield event
        return
    async for event in run_langchain_react(
        question,
        user_id,
        session_factory,
        settings,
        history=history,
        summary=summary,
        rag_context=rag_context,
        enable_thinking=enable_thinking,
        timeout=timeout,
    ):
        yield event
