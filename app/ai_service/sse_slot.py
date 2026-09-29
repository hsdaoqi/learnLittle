"""SSE 连接槽：同一用户同时打开的 /chat/query 有上限。

优先用 Redis 计数，多进程也能生效；Redis 挂了就退回进程内字典。
"""

from __future__ import annotations

import logging

from app.config import Settings
from app.db.redis_client import get_redis

logger = logging.getLogger(__name__)

_local_counts: dict[str, int] = {}


async def acquire_sse_slot(user_id: str, settings: Settings) -> bool:
    limit = max(1, settings.sse_max_connections_per_user)
    try:
        redis = get_redis()
        key = f"sse_conn:{user_id}"
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, 120)
        if count > limit:
            await redis.decr(key)
            logger.warning(
                "SSE 连接数超限（Redis）: user=%s count=%s", user_id[:8], count
            )
            return False
        return True
    except Exception as exc:
        logger.warning("SSE Redis 计数不可用，降级进程内: %s", exc)

    current = _local_counts.get(user_id, 0)
    if current >= limit:
        logger.warning("SSE 连接数超限（进程内）: user=%s", user_id[:8])
        return False
    _local_counts[user_id] = current + 1
    return True


async def release_sse_slot(user_id: str) -> None:
    try:
        await get_redis().decr(f"sse_conn:{user_id}")
        return
    except Exception as exc:
        logger.debug("SSE Redis 计数释放失败（TTL 自动清理兜底）: %s", exc)
    _local_counts[user_id] = max(0, _local_counts.get(user_id, 1) - 1)
