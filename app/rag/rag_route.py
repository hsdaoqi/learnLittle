"""RAG 路由：先判断这个问题要不要检索，再决定是否走 HyDE + 混合检索。

原项目用知识库 Top-1 向量距离和阈值比较：距离大就当闲聊，跳过 RAG。
这里沿用同一思路，但按当前用户过滤，并且知识库、笔记两个 collection 都看——
别人的文档不能把你拉进检索，只问笔记时也不该被漏掉。

失败时放行检索（和原项目一样），避免 embedding 抖动把该查的问题挡掉。
知识库页的关键词搜索不走这层门控。
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from app.config import Settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RouteDecision:
    retrieve: bool
    distance: float
    reason: str


RouteFn = Callable[[str, str, Settings], Awaitable[RouteDecision]]

_injected: RouteFn | None = None


def set_route_fn(fn: RouteFn | None) -> None:
    global _injected
    _injected = fn


def get_route_fn() -> RouteFn | None:
    return _injected


async def decide_retrieval(question: str, user_id: str, settings: Settings) -> RouteDecision:
    """返回是否检索。关闭开关时始终检索；算分失败时也检索。"""
    query = (question or "").strip()
    if not query:
        return RouteDecision(False, float("inf"), "empty")
    if not settings.rag_route_enabled:
        return RouteDecision(True, 0.0, "disabled")

    if _injected is not None:
        return await _injected(query, user_id, settings)

    try:
        from app.rag.vector_store import get_vector_store

        distance = await get_vector_store().compute_route_score(query, user_id)
    except Exception as exc:
        logger.warning("RAG 路由打分失败，继续检索: %s", exc)
        return RouteDecision(True, float("inf"), "score_failed")

    if distance > settings.rag_route_threshold:
        logger.debug(
            "跳过检索: distance=%.3f > threshold=%.3f",
            distance,
            settings.rag_route_threshold,
        )
        return RouteDecision(False, distance, "above_threshold")
    return RouteDecision(True, distance, "below_threshold")
