"""LangChain ReAct：create_agent + astream_events。

查询分类器由 chat_graph 先执行。深度思考只作用在主模型 extra_body；
分类器 / 计划走各自的环境变量。测试可 set_react_streamer 注入，不打外网。
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator, Callable
from contextlib import aclosing
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
        tool_start_times[name] = stamp
        produced.append({"type": "tool_start", "name": name})
        if consecutive_tool_calls > MAX_CONSECUTIVE_TOOL_CALLS:
            produced.append(
                {
                    "type": "error",
                    "content": "抱歉，我在处理这个问题时遇到了困难（工具调用循环），请尝试换一种方式提问。",
                }
            )
            return produced, consecutive_tool_calls
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

    from app.ai_service.thinking import extra_body
    from app.ai_service.usage_callback import ModelUsageCallback
    from app.services.usage_service import get_trace_context

    kwargs: dict[str, Any] = {
        "model": settings.llm_model,
        "api_key": settings.llm_api_key,
        "base_url": settings.llm_base_url,
        "streaming": True,
        "timeout": timeout,
        "stream_usage": True,
        "max_retries": 0,
        "callbacks": [ModelUsageCallback(
            settings.llm_model, (get_trace_context() or {}).get("stage") or "agent"
        )],
    }
    body = extra_body(enable_thinking, settings)
    if body is not None:
        kwargs["extra_body"] = body
    return ChatOpenAI(**kwargs)


def _create_agent(model, tools, system_prompt: str):
    try:
        from langchain.agents import create_agent

        return create_agent(model=model, tools=tools or [], system_prompt=system_prompt)
    except ImportError:
        from langgraph.prebuilt import create_react_agent

        return create_react_agent(model, tools or [], prompt=system_prompt)


def _history_messages(history: str | list[dict], summary: str) -> list:
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    messages = []
    if (summary or "").strip():
        messages.append(SystemMessage(content=f"[历史对话摘要]\n{summary.strip()}"))
    if isinstance(history, list):
        for item in history:
            cls = HumanMessage if item["role"] == "user" else AIMessage
            messages.append(cls(content=item["content"]))
    elif (history or "").strip():
        messages.append(SystemMessage(content=f"近期对话：\n{history.strip()}"))
    return messages


async def run_langchain_react(
    question: str,
    user_id: str,
    session_factory,
    settings: Settings,
    *,
    history: str | list[dict] = "",
    summary: str = "",
    rag_context: str = "",
    enable_thinking: bool = False,
    timeout: int | None = None,
    tool_groups: list[str] | None = None,
    extra_system: str = "",
    reflect: bool = True,
    read_only: bool = False,
) -> AsyncIterator[dict[str, Any]]:
    from langchain_core.messages import HumanMessage

    from app.ai_service.thinking import agent_timeout
    timeout = agent_timeout(settings, enable_thinking, timeout=timeout)
    system_prompt = build_react_system_prompt(
        question, rag_context=rag_context, extra_system=extra_system
    )
    tools = build_langchain_tools(user_id, session_factory, tool_groups, read_only=read_only)
    model = _create_chat_model(
        settings, enable_thinking=enable_thinking, timeout=timeout
    )
    accumulated: list[str] = []
    try:
        import asyncio
        from app.ai_service.reflection import build_repair_note, no_retry_tools, stream_l1_refine

        async with asyncio.timeout(timeout):
            repair_note = ""
            for attempt in range(2):
                accumulated = []
                consecutive = 0
                tool_start_times: dict[str, float] = {}
                failure = None
                failed_tool = None
                touched_side_effect = False
                agent = _create_agent(model, tools, system_prompt)
                payload = {"messages": [
                    *_history_messages(history, summary),
                    HumanMessage(content=(visible_question(question) or question) + repair_note),
                ]}
                try:
                    async for event in agent.astream_events(
                        payload, version="v2", config={"recursion_limit": 30}
                    ):
                        mapped, consecutive = map_langchain_event(
                            event, consecutive_tool_calls=consecutive,
                            tool_start_times=tool_start_times,
                        )
                        for item in mapped:
                            kind = item.get("type")
                            if kind == "response":
                                accumulated.append(item.get("content") or "")
                            elif kind == "tool_start":
                                from app.ai_service.tool_registry import registry

                                spec = registry.get(item["name"])
                                touched_side_effect |= (
                                    item["name"] in no_retry_tools(settings)
                                    or spec is None or not spec.parallel_safe
                                )
                            elif kind == "tool_end" and item.get("error"):
                                failed_tool = item["name"]
                            elif kind == "error":
                                failure = item
                                break
                            yield item
                        if failure:
                            break
                except Exception as exc:
                    logger.warning("ReAct 执行失败", exc_info=True)
                    failure = {"type": "error", "content": "工具或模型执行失败，请稍后重试"}
                    repair_note = build_repair_note(failed_tool, type(exc).__name__)
                if failure is None:
                    break
                if attempt or not settings.reflection_l2_enabled or touched_side_effect:
                    yield failure
                    return
                yield {"type": "reflection", "stage": "repairing", "round": 1}
                yield {"type": "response_replace", "content": ""}
                repair_note = repair_note or build_repair_note(failed_tool, failure["content"])
            final = "".join(accumulated)
            if reflect:
                async for event in stream_l1_refine(
                    visible_question(question) or question, final, settings,
                    enable_thinking=enable_thinking, context=system_prompt,
                ):
                    if event["type"] == "stream_done":
                        refined = event["full_response"]
                        if refined != final:
                            yield {"type": "response_replace", "content": refined}
                        final = refined
                    else:
                        yield event
            yield {"type": "stream_done", "full_response": final}
    except TimeoutError:
        logger.warning("ReAct 响应超时 (timeout=%ss)", timeout)
        yield {"type": "error", "content": "生成超时，请稍后重试"}
    except Exception as exc:
        logger.warning("ReAct 执行失败: %s", exc)
        yield {"type": "error", "content": "生成失败，请稍后重试"}


async def run_react(
    question: str,
    user_id: str,
    session_factory,
    settings: Settings,
    *,
    history: str | list[dict] = "",
    summary: str = "",
    rag_context: str = "",
    enable_thinking: bool = False,
    timeout: int | None = None,
    tool_groups: list[str] | None = None,
    extra_system: str = "",
    reflect: bool = True,
    read_only: bool = False,
) -> AsyncIterator[dict[str, Any]]:
    fn = _injected or run_langchain_react
    kwargs = {} if _injected else {"timeout": timeout}
    stream = fn(
        question,
        user_id,
        session_factory,
        settings,
        history=history,
        summary=summary,
        rag_context=rag_context,
        enable_thinking=enable_thinking,
        tool_groups=tool_groups, extra_system=extra_system, reflect=reflect,
        read_only=read_only, **kwargs,
    )
    async with aclosing(stream):
        async for event in stream:
            yield event
