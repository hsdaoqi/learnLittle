"""Plan -> dependency batches of step agents -> synthesis -> reflection."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass, field
from contextlib import aclosing
from datetime import datetime
from typing import Any

from app.ai_service.models import settings_for_role
from app.ai_service.tool_registry import registry
from app.ai_service.tools import register_builtin_tools
from app.config import Settings
from app.rag.note_cards import visible_question

logger = logging.getLogger(__name__)
PlanStreamer = Callable[..., AsyncIterator[dict[str, Any]]]
PlanFn = Callable[[str], Awaitable["ExecutionPlan"]]
_injected_streamer: PlanStreamer | None = None
_injected_plan: PlanFn | None = None
register_builtin_tools()


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
    return settings.plan_execute_enabled and bool(
        _injected_streamer or _injected_plan or settings.llm_api_key
    )


def build_plan_tool_list() -> str:
    return "\n".join(
        f"- {spec.name}: {spec.description}" for spec in registry.resolve()
    ) + "\n- none: 根据已有结果分析、总结，不调用工具"


def build_plan_prompt(message: str) -> str:
    return (
        "你是任务规划器。拆成 2-5 个步骤，显式声明依赖；不要编造工具。\n"
        f"当前时间：{datetime.now():%Y-%m-%d %H:%M:%S}\n"
        f"可用工具：\n{build_plan_tool_list()}\n"
        f"用户请求：{message[:4000]}\n"
        "读全文、更新或回顾完成步骤必须依赖提供资源 ID 的步骤。\n"
        "最后由系统统一综合回答，不必重复安排综合步骤。只输出 JSON：\n"
        '{"goal":"目标","steps":[{"step":1,"action":"具体任务",'
        '"tool":"工具名或none","depends_on":[]}]}'
    )


def parse_plan_payload(raw: str, fallback_goal: str = "") -> ExecutionPlan:
    content = re.sub(r"```(?:json)?\s*", "", (raw or "").strip()).strip()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise ValueError("Plan JSON 解析失败")
        data = json.loads(match.group())
    if not isinstance(data, dict) or not isinstance(data.get("steps"), list):
        raise ValueError("Plan 无步骤")
    steps = []
    for index, item in enumerate(data["steps"], 1):
        tool = str(item.get("tool") or "none")
        if tool != "none" and registry.get(tool) is None:
            raise ValueError(f"Plan 包含未注册工具: {tool}")
        steps.append(PlanStep(
            step=int(item.get("step") or index),
            action=str(item.get("action") or "").strip(),
            tool=tool,
            depends_on=[int(dep) for dep in (item.get("depends_on") or [])],
        ))
    if not steps or any(not step.action for step in steps):
        raise ValueError("Plan 无有效步骤")
    topological_batches(steps)
    return ExecutionPlan(str(data.get("goal") or fallback_goal)[:200], steps)


def topological_batches(steps: list[PlanStep]) -> list[list[PlanStep]]:
    ids = {step.step for step in steps}
    if len(ids) != len(steps) or any(step.step <= 0 for step in steps):
        raise ValueError("计划步骤编号必须唯一且为正数")
    if any(dep not in ids for step in steps for dep in step.depends_on):
        raise ValueError("计划依赖了不存在的步骤")
    completed: set[int] = set()
    remaining = list(steps)
    batches = []
    while remaining:
        ready = [step for step in remaining if set(step.depends_on) <= completed]
        if not ready:
            raise ValueError("计划存在循环依赖")
        batches.append(ready)
        completed.update(step.step for step in ready)
        remaining = [step for step in remaining if step not in ready]
    return batches


async def _complete(prompt, settings, role, timeout, enable_thinking=False):
    from app.rag.llm import complete_openai_compatible
    from app.services import usage_service

    previous = (usage_service.get_trace_context() or {}).get("stage") or "chat"
    usage_service.set_trace_stage(role)
    try:
        async with asyncio.timeout(timeout):
            return await complete_openai_compatible(
                prompt, settings_for_role(settings, role),
                timeout=timeout, enable_thinking=enable_thinking,
            )
    finally:
        usage_service.set_trace_stage(previous)


async def generate_plan(message: str, settings: Settings) -> ExecutionPlan:
    from app.ai_service.thinking import complete_thinking_for

    async with asyncio.timeout(settings.plan_timeout):
        if _injected_plan:
            return await _injected_plan(message)
        raw = await _complete(
            build_plan_prompt(message), settings, "plan", settings.plan_timeout,
            complete_thinking_for("plan", settings),
        )
        return parse_plan_payload(raw, visible_question(message))


async def _execute_step(
    step, question, previous, user_id, session_factory, settings, *,
    history, summary, rag_context, enable_thinking,
):
    from app.ai_service.react_agent import run_react
    from app.services import usage_service

    yield {"type": "plan_step_start", "step": step.step, "action": step.action}
    context = "\n\n".join(
        f"步骤 {dep} 的结果：\n{previous[dep]}"
        for dep in step.depends_on if dep in previous
    )
    task = (
        f"用户请求（背景）：{question}\n\n"
        f"当前步骤：{step.action}\n{context}\n\n"
        "只完成当前步骤，不回答完整请求。使用前置结果中的真实 ID；"
        "读取正文后再修改，禁止猜测 ID、伪造工具成功或笔记内容。"
    )
    try:
        step_timeout = settings.plan_step_timeout * (2 if enable_thinking else 1)
        async with asyncio.timeout(step_timeout):
            if step.tool != "none":
                usage_service.set_trace_stage("plan_step")
                parts = []
                stream = run_react(
                    task, user_id, session_factory, settings,
                    history=history, summary=summary, rag_context=rag_context,
                    enable_thinking=enable_thinking,
                    timeout=settings.plan_step_timeout,
                    tool_groups=registry.groups_for(step.tool),
                    extra_system=f"当前只执行步骤 {step.step}，建议工具：{step.tool}。\n{context}",
                    reflect=False,
                    read_only=bool(registry.get(step.tool) and registry.get(step.tool).parallel_safe),
                )
                async with aclosing(stream):
                    async for event in stream:
                        kind = event.get("type")
                        if kind == "response":
                            parts.append(event.get("content") or "")
                        elif kind == "response_replace":
                            parts = [event.get("content") or ""]
                        elif kind == "stream_done":
                            parts = [event.get("full_response") or "".join(parts)]
                        elif kind == "error":
                            step.result = "步骤失败，未能确认完成"
                            yield event
                            return
                        elif kind in {"thinking", "tool_start", "tool_end", "reflection"}:
                            yield event
                step.result = "".join(parts).strip()[:6000] or "没有可用结果"
            elif settings.llm_api_key:
                step.result = (await _complete(
                    task + f"\n历史摘要：{summary}\n参考资料：{rag_context}",
                    settings, "plan_step", step_timeout,
                    enable_thinking,
                )).strip()[:6000]
            else:
                step.result = context or step.action
    except Exception:
        logger.warning("计划步骤失败", exc_info=True)
        yield {"type": "error", "content": f"步骤 {step.step} 执行失败，请稍后重试"}
        return
    yield {"type": "plan_step_end", "step": step.step, "action": step.action,
           "result": step.result[:200]}


async def _execute_batch(batch, *args, **kwargs):
    queue: asyncio.Queue = asyncio.Queue()
    sentinel = object()

    async def consume(step):
        try:
            async for event in _execute_step(step, *args, **kwargs):
                await queue.put(event)
        finally:
            await queue.put(sentinel)

    tasks = [asyncio.create_task(consume(step)) for step in batch]
    try:
        finished = 0
        while finished < len(tasks):
            event = await queue.get()
            if event is sentinel:
                finished += 1
            else:
                yield event
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


def _safe_batches(batch, limit):
    reads = []
    for step in batch:
        spec = registry.get(step.tool)
        if step.tool == "none" or (spec and spec.parallel_safe):
            reads.append(step)
            if len(reads) >= limit:
                yield reads
                reads = []
        else:
            if reads:
                yield reads
                reads = []
            yield [step]
    if reads:
        yield reads


def build_synthesize_prompt(plan: ExecutionPlan, message: str) -> str:
    results = "\n\n".join(
        f"步骤 {step.step}（{step.action}）：\n{step.result[:6000]}"
        for step in plan.steps
    )
    return (
        f"用户请求：{message}\n目标：{plan.goal}\n各步骤结果：\n{results}\n\n"
        "根据结果给出最终回答，不重复过程，不编造失败步骤的结果。"
        "笔记搜索结果的编号、标题、(ID: ...) 必须保留。"
    )


async def run_plan_execute(
    question, user_id, session_factory, settings, *,
    history="", summary="", rag_context="", enable_thinking=False,
):
    from app.ai_service.react_agent import build_react_system_prompt
    from app.ai_service.reflection import stream_l1_refine, no_retry_tools

    wrote = False
    try:
        async with asyncio.timeout(settings.plan_total_timeout * (2 if enable_thinking else 1)):
            plan = await generate_plan(question, settings)
            if len(plan.steps) > settings.plan_execute_max_steps:
                raise ValueError("计划超过步骤上限")
            batches = topological_batches(plan.steps)
            yield {"type": "plan_start", "goal": plan.goal, "steps": [
                {"step": step.step, "action": step.action, "tool": step.tool}
                for step in plan.steps
            ]}
            previous = {}
            for batch in batches:
                for sub_batch in _safe_batches(batch, max(1, settings.plan_max_parallel_steps)):
                    failed = False
                    stream = _execute_batch(
                        sub_batch, question, previous, user_id, session_factory, settings,
                        history=history, summary=summary, rag_context=rag_context,
                        enable_thinking=enable_thinking,
                    )
                    try:
                        async for event in stream:
                            if event.get("type") == "tool_start":
                                spec = registry.get(event.get("name", ""))
                                wrote |= event.get("name") in no_retry_tools(settings) or spec is None or not spec.parallel_safe
                            failed |= event.get("type") == "error"
                            if event.get("type") != "error":
                                yield event
                    finally:
                        await stream.aclose()
                    if failed:
                        if wrote:
                            yield {"type": "error", "content": "部分操作可能已执行，请核对记录；不会自动重放写入"}
                        else:
                            yield {"type": "plan_fallback", "reason": "step_failed"}
                        return
                    previous.update({step.step: step.result for step in sub_batch})
            yield {"type": "plan_synthesize", "goal": plan.goal}
            system = build_react_system_prompt(question, rag_context=rag_context)
            history_text = json.dumps(history, ensure_ascii=False) if isinstance(history, list) else history
            prompt = (
                f"{system}\n历史摘要：{summary}\n近期对话：{history_text}\n\n"
                + build_synthesize_prompt(plan, question)
            )
            if settings.llm_api_key:
                answer = (await _complete(
                    prompt, settings, "plan_synthesize",
                    settings.plan_synthesize_timeout * (2 if enable_thinking else 1),
                    enable_thinking,
                )).strip()
            else:
                answer = "\n".join(step.result for step in plan.steps)
            if not answer:
                raise ValueError("综合结果为空")
            async for event in stream_l1_refine(
                question, answer, settings, plan_summary=plan.goal,
                step_results="\n".join(previous.values()), context=prompt,
                enable_thinking=enable_thinking,
            ):
                if event["type"] == "stream_done":
                    answer = event["full_response"]
                else:
                    yield event
            yield {"type": "response", "content": answer}
            yield {"type": "plan_complete", "goal": plan.goal}
            yield {"type": "stream_done", "full_response": answer}
    except Exception:
        logger.warning("Plan 执行失败", exc_info=True)
        if wrote:
            yield {"type": "error", "content": "部分操作已执行，结果汇总失败；请核对记录后再试"}
        else:
            yield {"type": "plan_fallback", "reason": "plan_failed"}


async def run_plan(question, user_id, session_factory, settings, **kwargs):
    fn = _injected_streamer or run_plan_execute
    async with aclosing(fn(question, user_id, session_factory, settings, **kwargs)) as stream:
        async for event in stream:
            yield event
