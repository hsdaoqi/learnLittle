"""Reflection：L1 综合后自检，L2 工具失败最多再试一轮。

原则：反思是增强不是关卡。批判超时、解析失败、模型异常一律视为通过，
不打断已经生成的回答。测试可 set_critique_fn 注入。
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from app.config import Settings

logger = logging.getLogger(__name__)

CritiqueFn = Callable[[str, str, str], Awaitable["ReflectionVerdict"]]

_injected: CritiqueFn | None = None


@dataclass(frozen=True)
class ReflectionVerdict:
    passed: bool
    issues: str = ""


def set_critique_fn(fn: CritiqueFn | None) -> None:
    global _injected
    _injected = fn


def get_critique_fn() -> CritiqueFn | None:
    return _injected


def parse_critique_response(raw: str) -> ReflectionVerdict:
    text = re.sub(r"```json\s*", "", raw or "")
    text = re.sub(r"```\s*", "", text).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            logger.warning("批判 JSON 解析失败（视为通过）: %s", text[:200])
            return ReflectionVerdict(True)
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            logger.warning("批判 JSON 解析失败（视为通过）")
            return ReflectionVerdict(True)
    if not isinstance(data, dict):
        return ReflectionVerdict(True)
    passed = bool(data.get("pass", True))
    issues = str(data.get("issues") or "").strip()
    if not passed and not issues:
        logger.warning("批判判定不合格但 issues 为空（视为通过）")
        return ReflectionVerdict(True)
    return ReflectionVerdict(passed, issues)


def build_critique_prompt(
    user_message: str,
    plan_summary: str,
    step_results: str,
    draft: str,
) -> str:
    return (
        "你是一个回答质量评审员。评审以下回答是否合格，输出严格 JSON。\n\n"
        f"原始用户问题：{(user_message or '')[:1000]}\n\n"
        f"执行计划目标：{plan_summary or '（无计划，直接回答）'}\n\n"
        f"各步骤结果（内部参考）：\n{step_results or '（无分步结果）'}\n\n"
        f"待评审回答：\n{(draft or '')[:4000]}\n\n"
        "评判维度（任一不满足 → pass: false）：\n"
        "1. 是否正面回答了用户问题\n"
        "2. 关键内容是否基于已有结果，无编造笔记或数据\n"
        "3. 失败/无结果是否如实说明\n"
        "4. 是否避免重复和大段过程细节\n\n"
        "只指出实质问题。严格输出 JSON：\n"
        '{"pass": true 或 false, "issues": "不合格时的修改指令；合格时为空字符串"}'
    )


def build_repair_note(failed_tool: str | None, error_content: str) -> str:
    tool_part = f"上次调用工具 `{failed_tool}` 失败" if failed_tool else "上次执行失败"
    return (
        f"\n\n[系统提示：{tool_part}（原因：{str(error_content)[:150]}）。"
        "请分析失败原因，修正参数或更换策略，最多再尝试 1 次工具调用；"
        "若无法确定修复方式，请直接基于已有信息回答，不要反复重试。]"
    )


def build_refine_prompt(user_message: str, draft: str, issues: str) -> str:
    return (
        f"你之前对用户问题「{(user_message or '')[:500]}」的回答未通过质量评审。\n\n"
        f"上一版回答：\n{(draft or '')[:4000]}\n\n"
        f"评审意见（必须修正的问题）：\n{issues}\n\n"
        "请输出修正后的完整回答（只输出回答正文，不要解释修改过程）。"
    )


def no_retry_tools(settings: Settings) -> set[str]:
    raw = settings.reflection_no_retry_tools or "send_email"
    return {part.strip() for part in raw.split(",") if part.strip()}


async def critique_answer(
    user_message: str,
    draft: str,
    settings: Settings,
    *,
    plan_summary: str = "",
    step_results: str = "",
) -> ReflectionVerdict:
    if _injected is not None:
        return await _injected(user_message, draft, plan_summary)
    if not settings.llm_api_key:
        return ReflectionVerdict(True)
    from app.rag.llm import complete_openai_compatible
    from app.services import usage_service

    previous = (usage_service.get_trace_context() or {}).get("stage") or "chat"
    usage_service.set_trace_stage("reflection")
    try:
        from app.ai_service.thinking import complete_thinking_for

        raw = await complete_openai_compatible(
            build_critique_prompt(user_message, plan_summary, step_results, draft),
            settings,
            enable_thinking=complete_thinking_for("reflection", settings),
        )
        return parse_critique_response(raw)
    except Exception as exc:
        logger.warning("批判调用异常（视为通过）: %s", exc)
        return ReflectionVerdict(True)
    finally:
        usage_service.set_trace_stage(previous)


async def refine_answer(
    user_message: str,
    draft: str,
    issues: str,
    settings: Settings,
    *,
    enable_thinking: bool = False,
) -> str:
    from app.rag.llm import complete_openai_compatible
    from app.services import usage_service

    previous = (usage_service.get_trace_context() or {}).get("stage") or "chat"
    usage_service.set_trace_stage("reflection")
    try:
        text = await complete_openai_compatible(
            build_refine_prompt(user_message, draft, issues),
            settings,
            enable_thinking=enable_thinking,
        )
        return (text or "").strip()
    finally:
        usage_service.set_trace_stage(previous)


async def maybe_l1_refine(
    user_message: str,
    draft: str,
    settings: Settings,
    *,
    plan_summary: str = "",
    step_results: str = "",
    enable_thinking: bool = False,
) -> tuple[str, list[dict]]:
    """草稿过短或关闭开关则原样返回。不合格时返回修正稿；修正失败仍用草稿。"""
    events: list[dict] = []
    text = (draft or "").strip()
    if not settings.reflection_l1_enabled:
        return text, events
    if len(text) < settings.reflection_min_answer_chars:
        return text, events
    if _injected is None and not settings.llm_api_key:
        return text, events
    events.append({"type": "reflection", "stage": "checking", "round": 0})
    verdict = await critique_answer(
        user_message,
        text,
        settings,
        plan_summary=plan_summary,
        step_results=step_results,
    )
    if verdict.passed:
        return text, events
    events.append({"type": "reflection", "stage": "refining", "round": 1})
    try:
        refined = await refine_answer(
            user_message,
            text,
            verdict.issues,
            settings,
            enable_thinking=enable_thinking,
        )
    except Exception as exc:
        logger.warning("L1 修正失败，保留草稿: %s", exc)
        return text, events
    if refined:
        return refined, events
    return text, events
