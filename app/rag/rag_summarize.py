"""检索后摘要：命中切片过长时压成短参考，再交给回答拼接 / 改写。

对齐原项目 RagService 阶段 5：
- 开关打开：对命中并发摘要，按问题抽相关信息
- 开关关闭、未配密钥、单条失败：截断后拼接，不打断问答
- 知识库页关键词搜索不走这层

测试可 set_summarize_fn 注入，不打外网。
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from app.config import Settings

logger = logging.getLogger(__name__)

SUMMARIZE_PROMPT = """请根据问题，从下面的文档片段中提取能回答问题的信息，写成一段简短参考。
只保留相关事实，不要编造。如果片段与问题无关，只输出「与问题无关」。
不要解释你在做什么，只输出短参考本身。

问题：{query}

文档片段：
{document}

短参考："""

SummarizeFn = Callable[[str, str], Awaitable[str]]

_injected: SummarizeFn | None = None


def set_summarize_fn(fn: SummarizeFn | None) -> None:
    global _injected
    _injected = fn


def get_summarize_fn() -> SummarizeFn | None:
    return _injected


def build_summarize_prompt(query: str, document: str) -> str:
    return SUMMARIZE_PROMPT.format(query=query, document=document)


def truncate_text(text: str, max_chars: int) -> str:
    raw = text or ""
    if max_chars <= 0 or len(raw) <= max_chars:
        return raw
    return raw[:max_chars]


def _copy_hit(hit: dict, content: str) -> dict:
    copied = dict(hit)
    copied["content"] = content
    return copied


async def _complete_summary(query: str, document: str, settings: Settings) -> str:
    from app.services.usage_service import UsageTimer, set_trace_stage

    set_trace_stage("rag_summary")
    if _injected is not None:
        timer = UsageTimer("rag_summary", settings.llm_model)
        try:
            text = (await _injected(query, document)).strip()
            await timer.finish(query, text)
            return text
        except Exception as exc:
            await timer.finish(query, "", success=False, error=str(exc))
            raise
    if not settings.llm_api_key:
        return ""
    from app.rag.llm import complete_openai_compatible

    prompt = build_summarize_prompt(
        query, truncate_text(document, settings.rag_summarize_input_max_chars)
    )
    return (await complete_openai_compatible(prompt, settings)).strip()


async def _summarize_one(query: str, hit: dict, settings: Settings) -> dict:
    content = (hit.get("content") or "").strip()
    max_chars = settings.rag_summarize_truncate_max_chars
    if not content:
        return _copy_hit(hit, "")
    if not settings.rag_summarize_enabled:
        return _copy_hit(hit, truncate_text(content, max_chars))

    try:
        text = await _complete_summary(query, content, settings)
        if not text:
            return _copy_hit(hit, truncate_text(content, max_chars))
        return _copy_hit(hit, text)
    except Exception as exc:
        logger.warning("检索后摘要失败，回退截断: %s", exc)
        return _copy_hit(hit, truncate_text(content, max_chars))


async def summarize_hits(
    query: str, hits: list[dict], settings: Settings
) -> list[dict]:
    """返回用于拼提示 / 算 Token 的命中副本。原 hits 不改，留给 API sources。"""
    if not hits:
        return []
    results = await asyncio.gather(
        *[_summarize_one(query, hit, settings) for hit in hits]
    )
    return list(results)
