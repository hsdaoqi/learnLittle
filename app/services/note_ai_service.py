"""笔记 AI 辅助：内联补全、写作辅助、自动打标签。

优先级：测试注入函数 > LLM_API_KEY > 本地兜底。
失败不抛给用户写操作：补全/写作返回空或原文，打标签返回 []。
"""

from __future__ import annotations

import logging
import re
from collections.abc import Awaitable, Callable

from app.config import Settings, get_settings
from app.rag.llm import complete_openai_compatible

logger = logging.getLogger(__name__)

CompleteFn = Callable[[str], Awaitable[str]]

_injected: CompleteFn | None = None

WRITE_MODES = ("continue", "expand", "summary")


def set_note_ai_fn(fn: CompleteFn | None) -> None:
    global _injected
    _injected = fn


def get_note_ai_fn() -> CompleteFn | None:
    return _injected


def _clip(text: str, limit: int) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    return text[:limit]


def build_autocomplete_prompt(content: str, cursor_position: int) -> str:
    cursor = max(0, min(cursor_position, len(content or "")))
    prefix = _clip((content or "")[:cursor], 1200)
    suffix = _clip((content or "")[cursor:], 400)
    return (
        "你在给一篇笔记做内联补全。只输出光标处接下来要写的一小段，不要重复已有正文，"
        "不要解释，不要加引号。\n\n"
        f"光标前：\n{prefix}\n\n"
        f"光标后：\n{suffix}\n\n"
        "补全："
    )


def build_write_prompt(content: str, mode: str) -> str:
    body = _clip(content, 4000)
    if mode == "expand":
        instruction = "把下面这段扩写得更具体，保留原意，不要加标题。"
    elif mode == "summary":
        instruction = "把下面这段总结成简短要点，用中文，不要开场白。"
    else:
        instruction = "接着下面这段往下续写，不要重复原文，不要解释。"
    return f"{instruction}\n\n原文：\n{body}\n\n结果："


def build_tag_prompt(title: str, content: str) -> str:
    return (
        "根据笔记标题和正文生成 1 到 5 个短标签。"
        "只输出逗号分隔的标签，不要编号，不要解释。\n\n"
        f"标题：{_clip(title, 200)}\n\n"
        f"正文：{_clip(content, 2000)}\n\n"
        "标签："
    )


def parse_tags(raw: str) -> list[str]:
    parts = re.split(r"[,，、\n]+", raw or "")
    tags: list[str] = []
    seen: set[str] = set()
    for part in parts:
        tag = part.strip().lstrip("#").strip()
        if not tag or tag.lower() in seen:
            continue
        seen.add(tag.lower())
        tags.append(tag[:20])
        if len(tags) >= 5:
            break
    return tags


async def _complete(prompt: str, settings: Settings) -> str:
    from app.services.usage_service import UsageTimer, set_trace_stage

    set_trace_stage("note_ai")
    if _injected is not None:
        timer = UsageTimer("note_ai", settings.llm_model)
        try:
            text = (await _injected(prompt)).strip()
            await timer.finish(prompt, text)
            return text
        except Exception as exc:
            await timer.finish(prompt, "", success=False, error=str(exc))
            raise
    if settings.llm_api_key:
        return (await complete_openai_compatible(prompt, settings)).strip()
    return ""


async def autocomplete(content: str, cursor_position: int = 0, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    try:
        return await _complete(build_autocomplete_prompt(content, cursor_position), settings)
    except Exception as exc:
        logger.warning("笔记内联补全失败: %s", exc)
        return ""


async def write_assist(content: str, mode: str = "continue", settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    if mode not in WRITE_MODES:
        mode = "continue"
    try:
        text = await _complete(build_write_prompt(content, mode), settings)
        return text
    except Exception as exc:
        logger.warning("笔记写作辅助失败: %s", exc)
        return ""


async def suggest_tags(title: str, content: str, settings: Settings | None = None) -> list[str]:
    settings = settings or get_settings()
    try:
        raw = await _complete(build_tag_prompt(title, content), settings)
        return parse_tags(raw)
    except Exception as exc:
        logger.warning("笔记自动打标签失败: %s", exc)
        return []
