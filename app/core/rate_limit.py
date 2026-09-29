"""接口护栏：Redis 固定窗口计数。

两层：
- 全局：同一身份每分钟最多 N 次，防止单用户打满进程
- 接口：按路径最长前缀匹配，登录/问答等比默认更严

身份：能解出 Access Token 就用 user_id，否则 anon:{ip}。
限流失败抛 BusinessError，由中间件转成统一 JSON。
"""

from __future__ import annotations

import logging
import time

import jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import Settings
from app.core.failed_response import BusinessError, ErrorCode, failed_response
from app.db.redis_client import get_redis

logger = logging.getLogger(__name__)

ENDPOINT_RATE_LIMITS = {
    "/api/v1/chat": 10,
    "/api/v1/knowledge/upload": 20,
    "/api/v1/note": 60,
    "/api/v1/auth/send-code": 10,
    "/api/v1/auth": 5,
}

SKIP_PREFIXES = ("/health", "/ready", "/docs", "/redoc", "/openapi.json", "/static")


def endpoint_limit_for(path: str, default: int) -> int:
    best_limit = default
    best_length = 0
    for prefix, limit in ENDPOINT_RATE_LIMITS.items():
        if path.startswith(prefix) and len(prefix) > best_length:
            best_limit = limit
            best_length = len(prefix)
    return best_limit


def identity_for(request: Request, settings: Settings) -> str:
    authorization = request.headers.get("authorization") or ""
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        try:
            payload = jwt.decode(
                parts[1],
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
            user_id = payload.get("sub")
            if payload.get("type") == "access" and user_id:
                return str(user_id)
        except jwt.PyJWTError:
            pass
    ip = request.client.host if request.client else "unknown"
    return f"anon:{ip}"


async def _hit(key: str, limit: int, window: int) -> int:
    redis = get_redis()
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, window + 1)
    return int(count)


async def check_rate_limit(
    identity: str,
    path: str,
    *,
    global_limit: int,
    default_limit: int,
    window: int,
) -> None:
    slot = int(time.time()) // window
    global_count = await _hit(
        f"rate_limit:{identity}:global:{slot}", global_limit, window
    )
    if global_count > global_limit:
        logger.warning(
            "全局限流: identity=%s count=%s/%s", identity, global_count, global_limit
        )
        raise BusinessError(code=ErrorCode.GLOBAL_RATE_LIMIT, http_status=429)

    limit = endpoint_limit_for(path, default_limit)
    endpoint_count = await _hit(f"rate_limit:{identity}:{path}:{slot}", limit, window)
    if endpoint_count > limit:
        logger.warning(
            "接口限流: identity=%s path=%s count=%s/%s",
            identity,
            path,
            endpoint_count,
            limit,
        )
        raise BusinessError(code=ErrorCode.ENDPOINT_RATE_LIMIT, http_status=429)


async def check_named_limit(
    identity: str, name: str, limit: int, window: int = 60
) -> None:
    """路由内额外计数，例如彻底删除 30 次/分钟。"""
    slot = int(time.time()) // window
    count = await _hit(f"rate_limit:{identity}:{name}:{slot}", limit, window)
    if count > limit:
        raise BusinessError(code=ErrorCode.ENDPOINT_RATE_LIMIT, http_status=429)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        settings: Settings = request.app.state.settings
        path = request.url.path
        if not settings.rate_limit_enabled or any(
            path.startswith(prefix) for prefix in SKIP_PREFIXES
        ):
            return await call_next(request)
        if not path.startswith("/api/"):
            return await call_next(request)
        try:
            await check_rate_limit(
                identity_for(request, settings),
                path,
                global_limit=settings.rate_limit_global,
                default_limit=settings.rate_limit_default,
                window=settings.rate_limit_window_seconds,
            )
        except BusinessError as exc:
            return JSONResponse(
                status_code=exc.http_status,
                content=failed_response(
                    code=exc.code, message=exc.message, detail=exc.detail
                ),
            )
        return await call_next(request)
