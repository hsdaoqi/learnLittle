"""深度思考开关：主模型跟前端，分类器 / 计划 / 反思跟环境变量。

enable_thinking 是百炼兼容模式的扩展字段，不是 OpenAI 官方参数。
GPT 兼容网关收到这个字段会直接 400。只有判定为 dashscope 协议时才写入请求。

有附件时主模型思考强制关闭（视觉模型不支持思考模式）。
本阶段不解析附件，只认 QueryRequest.attachment_ids 是否非空。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.config import Settings

ThinkingReason = Literal["off", "agent", "attachment", "unsupported"]
ThinkingProtocol = Literal["dashscope", "none"]
CompleteRole = Literal["classifier", "plan", "reflection", "agent"]

ATTACHMENT_THINKING_NOTICE = "深度思考对附件场景自动关闭（视觉模型理解附件）"
UNSUPPORTED_THINKING_NOTICE = "当前模型接口不支持深度思考，已按普通模式继续"


@dataclass(frozen=True)
class ThinkingDecision:
    requested: bool
    applied: bool
    reason: ThinkingReason

    def sse_notice(self) -> dict[str, str] | None:
        if self.reason == "attachment" and self.requested:
            return {
                "type": "thinking",
                "stage": "attachment",
                "content": ATTACHMENT_THINKING_NOTICE,
            }
        if self.reason == "unsupported" and self.requested:
            return {
                "type": "thinking",
                "stage": "unsupported",
                "content": UNSUPPORTED_THINKING_NOTICE,
            }
        return None


def thinking_protocol(settings: Settings) -> ThinkingProtocol:
    """auto：百炼域名才走 enable_thinking；其余接口默认不传这个字段。"""
    mode = (settings.llm_thinking_protocol or "auto").strip().lower()
    if mode in {"none", "off", "openai"}:
        return "none"
    if mode == "dashscope":
        return "dashscope"
    url = (settings.llm_base_url or "").lower()
    if "dashscope.aliyuncs.com" in url:
        return "dashscope"
    return "none"


def extra_body(enable_thinking: bool, settings: Settings) -> dict[str, bool] | None:
    """ChatOpenAI extra_body。非百炼返回 None，调用方不要把空字典传上去。"""
    if thinking_protocol(settings) != "dashscope":
        return None
    return {"enable_thinking": bool(enable_thinking)}


def payload_thinking_fields(enable_thinking: bool, settings: Settings) -> dict[str, bool]:
    """补全请求体。非百炼返回空 dict，避免带上非法参数。"""
    body = extra_body(enable_thinking, settings)
    return dict(body) if body is not None else {}


def resolve_agent_thinking(
    requested: bool,
    *,
    has_attachments: bool = False,
    settings: Settings | None = None,
) -> ThinkingDecision:
    if has_attachments:
        return ThinkingDecision(bool(requested), False, "attachment")
    if not requested:
        return ThinkingDecision(False, False, "off")
    if settings is not None and thinking_protocol(settings) != "dashscope":
        return ThinkingDecision(True, False, "unsupported")
    return ThinkingDecision(True, True, "agent")


def complete_thinking_for(role: CompleteRole, settings: Settings) -> bool:
    if thinking_protocol(settings) != "dashscope":
        return False
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
