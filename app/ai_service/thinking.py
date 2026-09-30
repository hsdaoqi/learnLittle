"""深度思考开关：主模型跟前端，分类器 / 计划 / 反思跟环境变量。

有附件时主模型思考强制关闭（视觉模型不支持思考模式）。
本阶段不解析附件，只认 QueryRequest.attachment_ids 是否非空。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.config import Settings

ThinkingReason = Literal["off", "agent", "attachment"]
CompleteRole = Literal["classifier", "plan", "reflection", "agent"]

ATTACHMENT_THINKING_NOTICE = "深度思考对附件场景自动关闭（视觉模型理解附件）"


@dataclass(frozen=True)
class ThinkingDecision:
    requested: bool
    applied: bool
    reason: ThinkingReason

    def sse_notice(self) -> dict[str, str] | None:
        if self.reason != "attachment" or not self.requested:
            return None
        return {
            "type": "thinking",
            "stage": "attachment",
            "content": ATTACHMENT_THINKING_NOTICE,
        }


def extra_body(enable_thinking: bool) -> dict[str, bool]:
    """DashScope compatible-mode 用 extra_body / 请求体字段传递思考开关。"""
    return {"enable_thinking": bool(enable_thinking)}


def resolve_agent_thinking(
    requested: bool,
    *,
    has_attachments: bool = False,
) -> ThinkingDecision:
    if has_attachments:
        return ThinkingDecision(bool(requested), False, "attachment")
    if requested:
        return ThinkingDecision(True, True, "agent")
    return ThinkingDecision(False, False, "off")


def complete_thinking_for(role: CompleteRole, settings: Settings) -> bool:
    if role == "classifier":
        return bool(settings.classifier_enable_thinking)
    if role == "plan":
        return bool(settings.plan_enable_thinking)
    if role == "reflection":
        return bool(settings.reflection_enable_thinking)
    return False


def agent_timeout(
    settings: Settings, enable_thinking: bool, *, timeout: int | None = None
) -> int:
    base = timeout or settings.llm_stream_timeout
    return base * 2 if enable_thinking else base
