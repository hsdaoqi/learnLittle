"""Plan-and-Execute：生成计划 → 逐步执行工具 → 综合成最终回答。

本阶段不接 Reflection。计划失败或综合失败推 plan_fallback，由调用方改走 ReAct。
测试可 set_plan_streamer / set_plan_fn 注入，不打外网。
"""

from __future__ import annotations

import inspect
import json
import logging
import re
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.ai_service.tool_registry import registry
from app.ai_service.tools import bind_user_tools
from app.config import Settings
from app.rag.note_cards import visible_question

logger = logging.getLogger(__name__)

PlanStreamer = Callable[..., AsyncIterator[dict[str, Any]]]
PlanFn = Callable[[str], Awaitable["ExecutionPlan"]]

_injected_streamer: PlanStreamer | None = None
_injected_plan: PlanFn | None = None

KNOWN_TOOLS = {
    "what_time_is_now": "获取当前时间",
    "get_user_info_tools": "获取当前用户基本信息",
    "search_notes_tool": "搜索用户笔记，返回标题和 ID 摘要",
    "get_note_content_tool": "获取单篇笔记全文",
    "get_note_stats_tool": "笔记分类统计",
    "get_today_reviews_tool": "今日待回顾列表",
    "mark_reviewed_tool": "标记回顾完成",
    "create_note_tool": "创建笔记",
    "update_note_tool": "更新笔记",
    "get_related_notes_tool": "按标题找相关笔记",
}


@dataclass
class PlanStep:
    step: int
    action: str
    tool: str = "none"
    depends_on: list[int] = field(default_factory=list)
    result: str = ""


@dataclass
class ExecutionPlan:
    goal: str
    steps: list[PlanStep]


def set_plan_streamer(fn: PlanStreamer | None) -> None:
    global _injected_streamer
    _injected_streamer = fn


def get_plan_streamer() -> PlanStreamer | None:
    return _injected_streamer


def set_plan_fn(fn: PlanFn | None) -> None:
    global _injected_plan
    _injected_plan = fn


def get_plan_fn() -> PlanFn | None:
    return _injected_plan


def plan_available(settings: Settings) -> bool:
    if not settings.plan_execute_enabled:
        return False
    if _injected_streamer is not None or _injected_plan is not None:
        return True
    return bool(settings.llm_api_key)


def build_plan_tool_list() -> str:
    lines = []
    for index, spec in enumerate(registry.resolve(), start=1):
        desc = KNOWN_TOOLS.get(spec.name) or spec.description
        lines.append(f"{index}. {spec.name} - {desc}")
    lines.append(f"{len(lines) + 1}. none - 不调用工具，直接根据已有结果写文字")
    return "\n".join(lines)


def build_plan_prompt(message: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        "你是一个任务规划器。将用户的复杂请求分解为有序的执行步骤。\n\n"
        f"当前时间：{now}\n\n"
        f"可用工具：\n{build_plan_tool_list()}\n\n"
        '直接回答 - 不需要工具的问题直接回答（标注 tool: "none"）\n\n'
        f"用户请求：{(message or '')[:1000]}\n\n"
        "请用 JSON 格式生成执行计划（不要包含其他内容）：\n"
        '{"goal": "用一句话概括目标", "steps": '
        '[{"step": 1, "action": "步骤描述", "tool": "工具名或none", "depends_on": []}]}\n\n'
        "规则：\n"
        "- 步骤数控制在 2-5 个\n"
        "- 搜索类请求优先「1 个搜索步骤 + 1 个综合步骤」\n"
        "- depends_on 填前置步骤编号，无依赖填 []\n"
        '- 最后一步始终是综合所有结果生成最终回答（tool: "none"）\n'
        "- 不要规划邮件、PPT、MCP 等尚未接入的工具\n"
    )


def build_synthesize_prompt(plan: ExecutionPlan, message: str) -> str:
    parts = []
    for step in plan.steps:
        text = (step.result or "无结果").strip()[:400]
        parts.append(f"步骤 {step.step}（{step.action}）：{text}")
    return (
        "根据以下执行计划的结果，生成最终回答。\n\n"
        f"原始用户问题：{(message or '')[:500]}\n\n"
        f"执行计划：{plan.goal}\n\n"
        "各步骤结果：\n"
        f"{chr(10).join(parts)}\n\n"
        "请基于以上结果生成完整、连贯的中文回答。"
        "步骤过程不要复述给用户；搜索结果若带编号列表和 (ID:)，原样保留。"
        "某步没有结果就如实说明，不要编造笔记内容。"
    )


def parse_plan_payload(raw: str, fallback_goal: str = "") -> ExecutionPlan:
    content = (raw or "").strip()
    content = re.sub(r"```json\s*", "", content)
    content = re.sub(r"```\s*", "", content).strip()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise ValueError("Plan JSON 解析失败")
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Plan JSON 不是对象")
    goal = str(data.get("goal") or fallback_goal or "完成用户请求").strip()[:80]
    raw_steps = data.get("steps") or []
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("Plan 无步骤")
    steps: list[PlanStep] = []
    known = set(KNOWN_TOOLS)
    for index, item in enumerate(raw_steps[:8], start=1):
        if not isinstance(item, dict):
            continue
        tool = str(item.get("tool") or "none").strip() or "none"
        if tool != "none" and tool not in known:
            tool = "none"
        depends = item.get("depends_on") or []
        if not isinstance(depends, list):
            depends = []
        clean_depends = []
        for dep in depends:
            try:
                number = int(dep)
            except (TypeError, ValueError):
                continue
            if number > 0:
                clean_depends.append(number)
        steps.append(
            PlanStep(
                step=int(item.get("step") or index),
                action=str(item.get("action") or f"步骤 {index}").strip()[:120],
                tool=tool,
                depends_on=clean_depends,
            )
        )
    if not steps:
        raise ValueError("Plan 无有效步骤")
    if steps[-1].tool != "none":
        steps.append(
            PlanStep(
                step=steps[-1].step + 1,
                action="综合前面步骤，生成最终回答",
                tool="none",
            )
        )
    return ExecutionPlan(goal=goal or fallback_goal, steps=steps)


def topological_batches(steps: list[PlanStep]) -> list[list[PlanStep]]:
    completed: set[int] = set()
    remaining = list(steps)
    batches: list[list[PlanStep]] = []
    while remaining:
        ready = [
            item
            for item in remaining
            if all(dep in completed for dep in item.depends_on)
        ]
        if not ready:
            logger.warning("计划存在循环依赖，剩余步骤改为顺序执行")
            ready = remaining[:]
        batches.append(ready)
        for item in ready:
            completed.add(item.step)
            remaining.remove(item)
    return batches


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


def _clip(text: str, limit: int = 800) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "…"


async def generate_plan(message: str, settings: Settings) -> ExecutionPlan:
    if _injected_plan is not None:
        return await _injected_plan(message)
    from app.rag.llm import complete_openai_compatible
    from app.services import usage_service

    previous = (usage_service.get_trace_context() or {}).get("stage") or "chat"
    usage_service.set_trace_stage("plan")
    try:
        raw = await complete_openai_compatible(build_plan_prompt(message), settings)
        return parse_plan_payload(raw, fallback_goal=visible_question(message)[:40])
    finally:
        usage_service.set_trace_stage(previous)


async def _execute_named_tool(
    step: PlanStep,
    question: str,
    bound: dict[str, Callable[..., Awaitable[str]]],
    previous: dict[int, str],
) -> AsyncIterator[dict[str, Any]]:
    fn = bound.get(step.tool)
    yield {"type": "tool_start", "name": step.tool}
    if fn is None:
        text = f"未知工具: {step.tool}"
        yield {"type": "tool_end", "name": step.tool, "error": text}
        step.result = text
        return
    context = "\n".join(
        f"步骤 {dep} 结果：{previous[dep]}"
        for dep in step.depends_on
        if dep in previous
    )
    arguments: dict[str, Any] = {}
    params = inspect.signature(fn).parameters
    if "query" in params:
        arguments["query"] = question
    elif "note_title" in params:
        arguments["note_title"] = question
    elif "title" in params and "content" in params:
        arguments["title"] = step.action[:40]
        arguments["content"] = context or question
    try:
        result = await _call_tool(fn, arguments)
        yield {"type": "tool_end", "name": step.tool, "result": result}
        step.result = _clip(result)
    except Exception as exc:
        logger.warning("计划步骤 %s 工具失败: %s", step.step, exc)
        text = f"工具执行失败: {exc}"
        yield {"type": "tool_end", "name": step.tool, "error": str(exc)}
        step.result = text


async def _complete_step_text(prompt: str, settings: Settings) -> str:
    from app.rag.llm import complete_openai_compatible
    from app.services import usage_service

    previous = (usage_service.get_trace_context() or {}).get("stage") or "chat"
    usage_service.set_trace_stage("plan_step")
    try:
        return (await complete_openai_compatible(prompt, settings)).strip()
    finally:
        usage_service.set_trace_stage(previous)


async def run_plan_execute(
    question: str,
    user_id: str,
    session_factory,
    settings: Settings,
    *,
    history: str = "",
    summary: str = "",
    rag_context: str = "",
) -> AsyncIterator[dict[str, Any]]:
    from app.ai_service.react_agent import build_react_system_prompt
    from app.rag.llm import complete_openai_compatible
    from app.services import usage_service

    visible = visible_question(question) or question
    try:
        plan = await generate_plan(visible, settings)
        if settings.plan_execute_max_steps:
            plan.steps = plan.steps[: max(2, settings.plan_execute_max_steps)]
    except Exception as exc:
        logger.warning("Plan 生成失败，降级 ReAct: %s", exc)
        yield {"type": "plan_fallback", "reason": str(exc)[:120] or "plan_failed"}
        return

    yield {
        "type": "plan_start",
        "goal": plan.goal,
        "steps": [
            {"step": item.step, "action": item.action, "tool": item.tool}
            for item in plan.steps
        ],
    }

    bound = bind_user_tools(user_id, session_factory)
    previous: dict[int, str] = {}
    for batch in topological_batches(plan.steps):
        for step in batch:
            yield {"type": "plan_step_start", "step": step.step, "action": step.action}
            if step.tool and step.tool != "none":
                async for event in _execute_named_tool(step, visible, bound, previous):
                    yield event
            else:
                dep_text = "\n".join(
                    f"步骤 {dep}：{previous.get(dep, '')}" for dep in step.depends_on
                )
                prompt = (
                    f"用户请求（背景）：{visible[:200]}\n"
                    f"当前步骤：{step.action}\n"
                    f"{dep_text}\n"
                    "只完成这一步，不要回答用户的完整问题。"
                )
                try:
                    if settings.llm_api_key:
                        step.result = _clip(
                            await _complete_step_text(prompt, settings), 500
                        )
                    else:
                        step.result = _clip(dep_text or step.action, 500)
                except Exception as exc:
                    logger.warning("计划步骤 %s 文本失败: %s", step.step, exc)
                    step.result = f"步骤 {step.step} 失败"
            previous[step.step] = step.result
            yield {
                "type": "plan_step_end",
                "step": step.step,
                "action": step.action,
                "result": step.result[:200],
            }

    yield {"type": "plan_synthesize", "goal": plan.goal}
    system = build_react_system_prompt(question, rag_context=rag_context)
    extra = ""
    if (summary or "").strip():
        extra += f"\n[历史对话摘要]\n{summary.strip()}"
    if (history or "").strip():
        extra += f"\n近期对话：\n{history.strip()}"
    prompt = f"{system}{extra}\n\n{build_synthesize_prompt(plan, visible)}"
    previous_stage = (usage_service.get_trace_context() or {}).get("stage") or "chat"
    usage_service.set_trace_stage("plan_synthesize")
    try:
        if settings.llm_api_key:
            answer = (await complete_openai_compatible(prompt, settings)).strip()
        else:
            answer = "\n".join(
                item.result for item in plan.steps if item.result
            ).strip()
        if not answer:
            raise ValueError("综合结果为空")
        yield {"type": "response", "content": answer}
        yield {"type": "plan_complete", "goal": plan.goal}
        yield {"type": "stream_done", "full_response": answer}
    except Exception as exc:
        logger.warning("Plan 综合失败，降级 ReAct: %s", exc)
        yield {"type": "plan_fallback", "reason": "synthesize_failed"}
    finally:
        usage_service.set_trace_stage(previous_stage)


async def run_plan(
    question: str,
    user_id: str,
    session_factory,
    settings: Settings,
    *,
    history: str = "",
    summary: str = "",
    rag_context: str = "",
) -> AsyncIterator[dict[str, Any]]:
    if _injected_streamer is not None:
        async for event in _injected_streamer(
            question,
            user_id,
            session_factory,
            settings,
            history=history,
            summary=summary,
            rag_context=rag_context,
        ):
            yield event
        return
    async for event in run_plan_execute(
        question,
        user_id,
        session_factory,
        settings,
        history=history,
        summary=summary,
        rag_context=rag_context,
    ):
        yield event
