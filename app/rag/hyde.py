"""HyDE：用假设性回答去检索，而不是直接用用户原句。

短问题（「那是什么」）和文档切片（陈述句）不在同一个语义空间。
先让模型写一段「可能的答案」，再用这段去走向量 + BM25。
重排序仍用原问题，避免假设文本把字面关键词冲掉。

未配密钥、关闭开关、调用失败时都回退原问题，检索不能因为 HyDE 挂掉。
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Awaitable, Callable

from app.config import Settings
from app.rag.llm import complete_openai_compatible

logger = logging.getLogger(__name__)

HydeFn = Callable[[str], Awaitable[str]]

_injected: HydeFn | None = None


def set_hyde_fn(fn: HydeFn | None) -> None:
    global _injected
    _injected = fn


def get_hyde_fn() -> HydeFn | None:
    return _injected


def build_hyde_prompt(question: str) -> str:
    return (
        "请根据下列问题写一段假设性回答，用于检索相关文档。"
        "不需要完全正确，但要像文档里会出现的陈述句，包含可能的术语和实体。"
        "不要提问，不要解释你在做什么，只输出假设性回答本身。\n\n"
        f"问题：{question}\n\n"
        "假设性回答："
    )


def hyde_cache_key(question: str, user_id: str, model: str) -> str:
    digest = hashlib.md5(question.encode("utf-8")).hexdigest()[:16]
    return f"hyde:v1:{model}:{user_id}:{digest}"


async def _cache_get(key: str) -> str | None:
    try:
        from app.db.redis_client import get_redis

        value = await get_redis().get(key)
        return value or None
    except Exception:
        return None


async def _cache_set(key: str, value: str, ttl: int) -> None:
    try:
        from app.db.redis_client import get_redis

        await get_redis().set(key, value, ex=max(ttl, 1))
    except Exception:
        return


async def generate_hyde(question: str, user_id: str, settings: Settings) -> str:
    """返回用于检索的文本：假设性回答或原问题。"""
    query = (question or "").strip()
    if not query:
        return query
    if not settings.hyde_enabled:
        return query

    key = hyde_cache_key(query, user_id, settings.llm_model)
    cached = await _cache_get(key)
    if cached:
        return cached

    try:
        from app.services.usage_service import UsageTimer, set_trace_stage

        set_trace_stage("hyde")
        if _injected is not None:
            timer = UsageTimer("hyde", settings.llm_model)
            try:
                text = (await _injected(query)).strip()
                await timer.finish(query, text)
            except Exception as exc:
                await timer.finish(query, "", success=False, error=str(exc))
                raise
        elif settings.llm_api_key:
            text = await complete_openai_compatible(build_hyde_prompt(query), settings)
        else:
            set_trace_stage("chat")
            return query
    except Exception as exc:
        logger.warning("HyDE 生成失败，回退原问题: %s", exc)
        from app.services.usage_service import set_trace_stage

        set_trace_stage("chat")
        return query

    if not text:
        return query
    await _cache_set(key, text, settings.hyde_cache_ttl_seconds)
    from app.services.usage_service import set_trace_stage

    set_trace_stage("chat")
    return text
