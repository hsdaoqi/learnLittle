"""聊天热缓存：会话列表 + 最近消息。

对齐原项目 DatabaseSessionManager：
- 写入：MySQL 先成功，再写 Redis；Redis 失败不影响主流程
- 读取：Redis → MySQL（miss 时回填）
- 会话列表：`chat:sessions:{user_id}`，JSON，短 TTL
- 最近消息：`chat:msgs:{session_id}`，List，LPUSH 最新在前，LTRIM 只留 N 条

本阶段不做游标分页、幂等键。前端消息历史仍走 MySQL 全量，避免只拿到热窗口。
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_BUFFER_SIZE = 20
DEFAULT_SESSION_LIST_TTL = 300


def sessions_key(user_id: str) -> str:
    return f"chat:sessions:{user_id}"


def messages_key(session_id: str) -> str:
    return f"chat:msgs:{session_id}"


def _dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _loads(raw: str) -> Any:
    return json.loads(raw)


def dump_session(session: Any) -> dict:
    created = getattr(session, "created_at", None)
    updated = getattr(session, "updated_at", None)
    if isinstance(session, dict):
        return {
            "id": session.get("id"),
            "title": session.get("title"),
            "created_at": session.get("created_at"),
            "updated_at": session.get("updated_at"),
        }
    return {
        "id": session.id,
        "title": session.title,
        "created_at": created.isoformat() if isinstance(created, datetime) else created,
        "updated_at": updated.isoformat() if isinstance(updated, datetime) else updated,
    }


def dump_message(message: Any) -> dict:
    created = getattr(message, "created_at", None)
    if isinstance(message, dict):
        return {
            "id": message.get("id"),
            "session_id": message.get("session_id"),
            "role": message.get("role"),
            "content": message.get("content"),
            "created_at": message.get("created_at"),
        }
    return {
        "id": message.id,
        "session_id": message.session_id,
        "role": message.role,
        "content": message.content,
        "created_at": created.isoformat() if isinstance(created, datetime) else created,
    }


async def get_session_list(user_id: str) -> list[dict] | None:
    try:
        from app.db.redis_client import get_redis

        raw = await get_redis().get(sessions_key(user_id))
        if not raw:
            return None
        data = _loads(raw)
        return data if isinstance(data, list) else None
    except Exception as exc:
        logger.debug("会话列表缓存读取失败: %s", exc)
        return None


async def set_session_list(
    user_id: str, sessions: list[dict], ttl: int = DEFAULT_SESSION_LIST_TTL
) -> None:
    try:
        from app.db.redis_client import get_redis

        await get_redis().set(sessions_key(user_id), _dumps(sessions), ex=max(ttl, 1))
    except Exception as exc:
        logger.warning("会话列表缓存写入失败: %s", exc)


async def invalidate_session_list(user_id: str) -> None:
    try:
        from app.db.redis_client import get_redis

        await get_redis().delete(sessions_key(user_id))
    except Exception as exc:
        logger.debug("会话列表缓存失效失败: %s", exc)


async def get_recent_messages(session_id: str) -> list[dict] | None:
    """命中则返回时间正序（旧 → 新）。空列表视为 miss，好回填。"""
    try:
        from app.db.redis_client import get_redis

        raw_items = await get_redis().lrange(messages_key(session_id), 0, -1)
        if not raw_items:
            return None
        messages = [_loads(item) for item in raw_items]
        messages.reverse()
        return messages
    except Exception as exc:
        logger.debug("消息热缓存读取失败: %s", exc)
        return None


async def push_message(
    session_id: str,
    message: Any,
    buffer_size: int = DEFAULT_BUFFER_SIZE,
) -> None:
    try:
        from app.db.redis_client import get_redis

        redis = get_redis()
        key = messages_key(session_id)
        await redis.lpush(key, _dumps(dump_message(message)))
        await redis.ltrim(key, 0, max(buffer_size, 1) - 1)
    except Exception as exc:
        logger.warning("消息热缓存更新失败: %s", exc)


async def rebuild_messages(
    session_id: str,
    messages: list[Any],
    buffer_size: int = DEFAULT_BUFFER_SIZE,
) -> None:
    """messages 为正序；写入时最新在 List 头部。"""
    try:
        from app.db.redis_client import get_redis

        redis = get_redis()
        key = messages_key(session_id)
        await redis.delete(key)
        recent = list(messages)[-max(buffer_size, 1) :]
        for item in reversed(recent):
            await redis.lpush(key, _dumps(dump_message(item)))
    except Exception as exc:
        logger.warning("消息热缓存回填失败: %s", exc)


async def delete_messages(session_id: str) -> None:
    try:
        from app.db.redis_client import get_redis

        await get_redis().delete(messages_key(session_id))
    except Exception as exc:
        logger.debug("消息热缓存删除失败: %s", exc)
