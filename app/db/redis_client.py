"""Redis 连接管理。

模块级单例：由应用生命周期 init/close，业务代码通过 get_redis() 取用。
测试中可用 set_redis() 预先注入 fakeredis，init_redis 发现已有实例会跳过真实连接。
"""

import asyncio
import logging

import redis.asyncio as redis

from app.config import Settings

logger = logging.getLogger(__name__)

_client: redis.Redis | None = None


def set_redis(client: redis.Redis) -> None:
    """替换模块级 Redis 实例（测试注入用）。"""
    global _client
    _client = client


def get_redis() -> redis.Redis:
    """获取 Redis 实例；未初始化时抛错，避免业务代码静默拿到 None。"""
    if _client is None:
        raise RuntimeError(
            "Redis 未初始化：应通过应用生命周期 init_redis() 启动，"
            "或在测试中先用 set_redis() 注入 fakeredis"
        )
    return _client


def create_redis_client(settings: Settings) -> redis.Redis:
    """按配置创建异步客户端；decode_responses 让所有命令直接返回 str。"""
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        decode_responses=True,
    )


async def init_redis(settings: Settings) -> redis.Redis:
    """建立连接并 ping 验证；已有实例（如测试注入）时直接复用。"""
    global _client
    if _client is not None:
        return _client

    client = create_redis_client(settings)
    await client.ping()
    _client = client
    logger.info("Redis 已连接: %s:%s/%s", settings.redis_host, settings.redis_port, settings.redis_db)
    return _client


async def close_redis() -> None:
    """应用关闭时释放连接。"""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
        logger.info("Redis 连接已关闭")


async def check_redis() -> bool:
    """两秒内 ping 通过则视为可用，供 /ready 探针使用。"""
    if _client is None:
        return False
    try:
        async with asyncio.timeout(2):
            await _client.ping()
        return True
    except (redis.RedisError, TimeoutError, OSError):
        return False
