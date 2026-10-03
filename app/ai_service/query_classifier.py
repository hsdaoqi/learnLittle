"""查询复杂度分类：L1 规则优先，不确定再走 L2 轻量补全。

simple → ReAct；complex 在可用时走 Plan-Execute，否则降级 ReAct。
失败、关闭开关或未配密钥一律 simple，不打断问答。
测试可 set_classifier_fn 注入。
"""

from __future__ import annotations

import json
import asyncio
import logging
import re
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal

from app.config import Settings

logger = logging.getLogger(__name__)

Complexity = Literal["simple", "complex"]
ClassifierSource = Literal["rule", "llm", "inject", "fallback"]
RouteName = Literal["react", "plan_pending", "plan_execute"]

ClassifierFn = Callable[[str], Awaitable["ClassificationResult"]]

_injected: ClassifierFn | None = None

COMPLEX_PATTERNS = (
    r"分析.*总结",
    r"对比.*整理",
    r"研究.*归纳",
    r"先.*然后.*再",
    r"计划",
    r"规划",
    r"步骤",
    r"方案",
    r"策略",
    r"综合分析",
    r"系统梳理",
)
SIMPLE_PATTERNS = (
    r"^你好",
    r"^谢谢",
    r"^再见",
    r"^现在.*时间",
)
CONDITION_PATTERNS = (
    r"如果.*否则",
    r"要么.*要么",
    r"根据.*决定",
)
TOOL_KEYWORDS = (
    "搜索笔记",
    "搜索",
    "统计",
    "回顾",
    "创建",
    "更新",
    "推荐",
    "标记",
)
TOOL_INTENT_KEYWORDS = (
    "搜索",
    "统计",
    "回顾",
    "创建",
    "更新",
    "推荐",
    "标记",
    "时间",
)

_COMPLEX_RES = [re.compile(pattern) for pattern in COMPLEX_PATTERNS]
_SIMPLE_RES = [re.compile(pattern) for pattern in SIMPLE_PATTERNS]
_CONDITION_RES = [re.compile(pattern) for pattern in CONDITION_PATTERNS]


@dataclass(frozen=True)
class ClassificationResult:
    complexity: Complexity
    source: ClassifierSource
    reason: str
    confidence: float = 1.0
    route: RouteName = "react"

    def thinking_text(self) -> str:
        if self.route == "plan_execute":
            return f"判定为复杂查询（{self.source}），走 Plan-Execute"
        if self.complexity == "complex":
            return (
                f"判定为复杂查询（{self.source}），Plan-Execute 不可用，本轮降级 ReAct"
            )
        return f"判定为简单查询（{self.source}），走 ReAct"


def set_classifier_fn(fn: ClassifierFn | None) -> None:
    global _injected
    _injected = fn


def get_classifier_fn() -> ClassifierFn | None:
    return _injected


def decide_route(complexity: str, *, plan_available: bool = False) -> RouteName:
    if complexity == "complex":
        return "plan_execute" if plan_available else "plan_pending"
    return "react"


def _count_tool_keywords(message: str) -> int:
    matched: list[str] = []
    for keyword in sorted(TOOL_KEYWORDS, key=len, reverse=True):
        if keyword not in message:
            continue
        if any(keyword in existing for existing in matched):
            continue
        matched.append(keyword)
    return len(matched)


def rule_classify(
    message: str, settings: Settings, *, plan_available: bool = False
) -> ClassificationResult:
    """L1：能确定就返回 simple/complex；否则 reason=uncertain，调用方再决定是否上 L2。"""
    text = (message or "").strip()
    if not text:
        return ClassificationResult("simple", "rule", "empty", 1.0, "react")

    for pattern in _COMPLEX_RES:
        if pattern.search(text):
            return _final(
                "complex",
                "rule",
                f"匹配复杂模式: {pattern.pattern}",
                plan_available=plan_available,
            )

    question_marks = text.count("？") + text.count("?")
    min_length = settings.classifier_complex_min_length
    if len(text) > min_length and question_marks >= 2:
        return _final(
            "complex",
            "rule",
            f"长文本({len(text)}字符)+{question_marks}个问号",
            plan_available=plan_available,
        )

    matched_tools = _count_tool_keywords(text)
    if matched_tools >= 3:
        return _final(
            "complex",
            "rule",
            f"多目标并列: 匹配{matched_tools}个工具意图",
            plan_available=plan_available,
        )

    for pattern in _CONDITION_RES:
        if pattern.search(text):
            return _final(
                "complex",
                "rule",
                f"条件分支: 匹配 {pattern.pattern}",
                plan_available=plan_available,
            )

    for pattern in _SIMPLE_RES:
        if pattern.search(text):
            return _final(
                "simple",
                "rule",
                f"匹配简单模式: {pattern.pattern}",
                plan_available=plan_available,
            )

    has_tool_intent = any(keyword in text for keyword in TOOL_INTENT_KEYWORDS)
    if len(text) < settings.classifier_short_msg_length and not has_tool_intent:
        return _final(
            "simple",
            "rule",
            f"短消息({len(text)}字符)无工具意图",
            plan_available=plan_available,
        )

    if has_tool_intent and matched_tools == 1:
        return _final("simple", "rule", "单步工具操作", plan_available=plan_available)

    return ClassificationResult("simple", "rule", "uncertain", 0.0, "react")


def _final(
    complexity: Complexity,
    source: ClassifierSource,
    reason: str,
    confidence: float = 1.0,
    *,
    plan_available: bool = False,
) -> ClassificationResult:
    return ClassificationResult(
        complexity,
        source,
        reason,
        confidence,
        decide_route(complexity, plan_available=plan_available),
    )


def build_classify_prompt(message: str) -> str:
    clipped = (message or "")[:500]
    return (
        '你是一个查询复杂度分析器。判断以下用户消息属于"简单"还是"复杂"。\n\n'
        "简单消息的特征：\n"
        "- 可以在一步内完成（单一工具调用或直接回答）\n"
        "- 不涉及多个子任务\n"
        "- 不需要先收集信息再综合处理\n"
        '- 示例："现在几点了？"、"帮我搜索Python笔记"、"什么是Docker？"\n\n'
        "复杂消息的特征：\n"
        "- 需要多步骤完成（先搜索、再分析、最后汇总等）\n"
        "- 包含多个子任务或目标\n"
        "- 需要制定计划分步执行\n"
        '- 示例："分析我最近的笔记，总结重点，然后制定学习计划"\n\n'
        f"用户消息：{clipped}\n\n"
        "请用 JSON 格式回答（不要包含其他内容）：\n"
        '{"complexity": "simple 或 complex", "reason": "简短判断理由(10字以内)"}'
    )


def parse_classifier_payload(
    raw: str, *, plan_available: bool = False
) -> ClassificationResult:
    content = (raw or "").strip()
    content = re.sub(r"```json\s*", "", content)
    content = re.sub(r"```\s*", "", content).strip()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            return _final(
                "simple", "llm", "parse_error", 0.5, plan_available=plan_available
            )
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return _final(
                "simple", "llm", "parse_error", 0.5, plan_available=plan_available
            )
    if not isinstance(data, dict):
        return _final(
            "simple", "llm", "parse_error", 0.5, plan_available=plan_available
        )
    complexity = data.get("complexity") or "simple"
    if complexity not in ("simple", "complex"):
        complexity = "simple"
    reason = str(data.get("reason") or "LLM 判定")[:40]
    return _final(complexity, "llm", reason, 0.8, plan_available=plan_available)


async def _llm_classify(
    message: str, settings: Settings, *, plan_available: bool = False
) -> ClassificationResult:
    from app.rag.llm import complete_openai_compatible
    from app.services import usage_service

    previous = (usage_service.get_trace_context() or {}).get("stage") or "chat"
    usage_service.set_trace_stage("classify")
    try:
        from app.ai_service.models import settings_for_role
        from app.ai_service.thinking import complete_thinking_for

        role_settings = settings_for_role(settings, "classifier")
        raw = await complete_openai_compatible(
            build_classify_prompt(message), role_settings,
            enable_thinking=complete_thinking_for("classifier", role_settings),
            timeout=settings.classifier_timeout,
        )
        return parse_classifier_payload(raw, plan_available=plan_available)
    finally:
        usage_service.set_trace_stage(previous)


async def classify_query(
    message: str, settings: Settings, *, plan_available: bool = False
) -> ClassificationResult:
    text = (message or "").strip()
    if not settings.classifier_enabled:
        return _final(
            "simple", "fallback", "disabled", 1.0, plan_available=plan_available
        )
    if _injected is not None:
        result = await _injected(text)
        route = decide_route(result.complexity, plan_available=plan_available)
        return ClassificationResult(
            result.complexity,
            "inject",
            result.reason,
            result.confidence,
            route,
        )

    l1 = rule_classify(text, settings, plan_available=plan_available)
    if l1.reason != "uncertain":
        return l1

    if not settings.classifier_l2_enabled or not settings.llm_api_key:
        return _final(
            "simple", "fallback", "no_llm_default", 0.5, plan_available=plan_available
        )
    try:
        async with asyncio.timeout(settings.classifier_timeout):
            return await _llm_classify(text, settings, plan_available=plan_available)
    except Exception as exc:
        logger.warning("L2 分类失败，降级 simple: %s", exc)
        return _final(
            "simple", "fallback", "llm_fallback", 0.5, plan_available=plan_available
        )
