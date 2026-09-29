"""会话自动标题：首轮问答后生成一次，失败回退截断问句。

只在标题仍是「新对话」时写入。用户手动改名后不再覆盖。
测试可 set_title_fn 注入，不打外网。
"""

from __future__ import annotations

import logging
import re
from collections.abc import Awaitable, Callable

from app.config import Settings
from app.rag.llm import complete_openai_compatible

logger = logging.getLogger(__name__)

DEFAULT_TITLE = "新对话"
TitleFn = Callable[[str], Awaitable[str]]

_injected: TitleFn | None = None

_QUOTE_RE = re.compile(r'^[\'"「」『』《》]+|[\'"「」『』《》]+$')


def set_title_fn(fn: TitleFn | None) -> None:
    global _injected
    _injected = fn


def get_title_fn() -> TitleFn | None:
    return _injected


def build_title_prompt(question: str) -> str:
    return (
        "请根据以下用户问题，生成一个不超过20字的会话标题。\n\n"
        f"问题：{question}\n\n"
        "要求：\n"
        "- 不超过20个字\n"
        "- 用用户的语言\n"
        "- 不加引号\n"
        "- 概括问题主题\n"
        "- 不要解释你在做什么，只输出标题本身\n\n"
        "标题："
    )


def fallback_title(question: str, max_chars: int = 40) -> str:
    text = " ".join((question or "").strip().split())
    if not text:
        return DEFAULT_TITLE
    return text[: max(1, max_chars)]


def sanitize_title(raw: str, *, max_chars: int, fallback: str) -> str:
    text = " ".join((raw or "").strip().split())
    text = _QUOTE_RE.sub("", text).strip()
    if not text:
        return fallback
    return text[:max_chars]


async def generate_session_title(question: str, settings: Settings) -> str:
    """生成标题文本。失败或关闭开关时返回截断问句，不抛给主流程。"""
    fallback = fallback_title(question, settings.chat_auto_title_fallback_chars)
    if not (question or "").strip():
        return DEFAULT_TITLE
    if not settings.chat_auto_title_enabled:
        return fallback

    max_chars = settings.chat_auto_title_max_chars
    try:
        from app.services.usage_service import UsageTimer, set_trace_stage

        set_trace_stage("title")
        if _injected is not None:
            timer = UsageTimer("title", settings.llm_model)
            try:
                text = await _injected(question)
                await timer.finish(question, text or "")
            except Exception as exc:
                await timer.finish(question, "", success=False, error=str(exc))
                raise
        elif settings.llm_api_key:
            text = await complete_openai_compatible(
                build_title_prompt(question), settings
            )
        else:
            set_trace_stage("chat")
            return fallback
        cleaned = sanitize_title(text, max_chars=max_chars, fallback=fallback)
        set_trace_stage("chat")
        return cleaned
    except Exception as exc:
        logger.warning("会话标题生成失败，回退截断: %s", exc)
        from app.services.usage_service import set_trace_stage

        set_trace_stage("chat")
        return fallback
