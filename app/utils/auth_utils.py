"""认证工具：密码哈希、JWT 签发/校验、当前用户依赖注入、Redis 安全增强。

与原项目的差异（重建阶段的有意取舍）：
- 密码哈希直接使用 bcrypt 库（原项目用 passlib，后者已停止维护）
- JWT 使用 PyJWT（原项目用 python-jose）
- 设备会话管理（多设备列表/会话数上限）暂未实现，后续阶段补齐

Redis 键约定：
- login_attempts:{username}        登录失败计数（TTL = 锁定时长）
- refresh_token:{user_id}:{jti}    Refresh Token 白名单（TTL = refresh 有效期）
- token_blacklist:{jti}            已登出的 Access Token 黑名单（TTL = 剩余有效期）
- session:{user_id}:{device_id}    设备会话 Hash（TTL = refresh 有效期）
- user_sessions:{user_id}          该用户全部 device_id 集合
"""

import time
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, Header, Request

from app.config import get_settings
from app.core.failed_response import BusinessError, ErrorCode
from app.db.redis_client import get_redis

# 登录锁定策略：失败 5 次锁 15 分钟
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900


# ========== 密码哈希（bcrypt） ==========


def hash_password(password: str) -> str:
    """对明文密码做 bcrypt 哈希，返回可直接存库的字符串。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码与存储的哈希是否匹配；哈希格式非法时视为不匹配。"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """密码强度策略：至少 8 位，且同时包含字母和数字。"""
    if len(password) < 8:
        return False, "密码长度至少 8 位"
    if not any(c.isalpha() for c in password):
        return False, "密码必须包含字母"
    if not any(c.isdigit() for c in password):
        return False, "密码必须包含数字"
    return True, ""


# ========== JWT Token ==========


def _create_token(user_id: str, token_type: str, lifetime: timedelta) -> str:
    """签发 JWT；jti 唯一标识用于 Redis 白名单/黑名单。"""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + lifetime,
        "jti": str(uuid.uuid4()),
        "type": token_type,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str) -> str:
    """签发短生命周期的 Access Token。"""
    settings = get_settings()
    return _create_token(
        user_id, "access", timedelta(minutes=settings.access_token_expire_minutes)
    )


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """签发长生命周期的 Refresh Token，返回 (token, jti)，jti 用于白名单登记。"""
    settings = get_settings()
    token = _create_token(
        user_id, "refresh", timedelta(days=settings.refresh_token_expire_days)
    )
    # jti 已写入 token 内部，解码取回即可
    return token, decode_token(token)["jti"]


def decode_token(token: str) -> dict:
    """解码并校验 JWT；过期与无效分别返回不同业务错误码。"""
    settings = get_settings()
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError as exc:
        raise BusinessError(code=ErrorCode.TOKEN_EXPIRED, http_status=401) from exc
    except jwt.InvalidTokenError as exc:
        raise BusinessError(code=ErrorCode.TOKEN_INVALID, http_status=401) from exc


# ========== 登录失败锁定 ==========


def _attempts_key(username: str) -> str:
    return f"login_attempts:{username}"


async def check_login_attempts(username: str) -> None:
    """登录前检查：失败次数达到上限则直接拒绝（含正确密码）。"""
    attempts = await get_redis().get(_attempts_key(username))
    if attempts and int(attempts) >= MAX_LOGIN_ATTEMPTS:
        raise BusinessError(code=ErrorCode.ACCOUNT_LOCKED, http_status=403)


async def record_login_failure(username: str) -> None:
    """密码错误时计数 +1；首次失败起设置锁定窗口 TTL。"""
    redis = get_redis()
    count = await redis.incr(_attempts_key(username))
    if count == 1:
        await redis.expire(_attempts_key(username), LOCKOUT_DURATION_SECONDS)


async def clear_login_attempts(username: str) -> None:
    """登录成功后清除失败计数。"""
    await get_redis().delete(_attempts_key(username))


# ========== Refresh Token 白名单 ==========


def _refresh_key(user_id: str, jti: str) -> str:
    return f"refresh_token:{user_id}:{jti}"


def _refresh_ttl_seconds() -> int:
    return get_settings().refresh_token_expire_days * 86400


async def store_refresh_token(user_id: str, jti: str) -> None:
    """把新签发的 Refresh Token 登记进白名单，TTL 与其有效期一致。"""
    await get_redis().setex(_refresh_key(user_id, jti), _refresh_ttl_seconds(), "1")


async def verify_refresh_token(user_id: str, jti: str) -> bool:
    """校验 Refresh Token 是否仍在白名单中（登出/轮换/改密后会移除）。"""
    return bool(await get_redis().get(_refresh_key(user_id, jti)))


async def revoke_refresh_token(user_id: str, jti: str) -> None:
    """从白名单移除单个 Refresh Token（轮换/登出时调用）。"""
    await get_redis().delete(_refresh_key(user_id, jti))


async def revoke_all_refresh_tokens(user_id: str) -> None:
    """吊销某用户全部 Refresh Token（改密/全端登出场景）。"""
    redis = get_redis()
    cursor = 0
    while True:
        cursor, keys = await redis.scan(
            cursor, match=f"refresh_token:{user_id}:*", count=100
        )
        if keys:
            await redis.delete(*keys)
        if cursor == 0:
            break
    await _clear_all_device_sessions(user_id)


# ========== Access Token 黑名单 ==========


def _blacklist_key(jti: str) -> str:
    return f"token_blacklist:{jti}"


async def blacklist_access_token(jti: str, remaining_ttl_seconds: int) -> None:
    """登出时把 Access Token 拉黑，TTL 取其剩余有效期（至少 1 秒）。"""
    if remaining_ttl_seconds <= 0:
        return
    await get_redis().setex(_blacklist_key(jti), max(1, remaining_ttl_seconds), "1")


async def is_token_blacklisted(jti: str) -> bool:
    """检查 Access Token 是否已被登出拉黑。"""
    return bool(await get_redis().get(_blacklist_key(jti)))


# ========== FastAPI 依赖注入 ==========


async def get_current_token_payload(
    authorization: str | None = Header(default=None),
) -> dict:
    """解析 Bearer Token 并返回完整 payload。

    校验顺序：格式 → 签名/有效期 → 类型 → 黑名单（登出）。
    """
    if not authorization:
        raise BusinessError(
            code=ErrorCode.TOKEN_INVALID, message="缺少认证信息", http_status=401
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise BusinessError(
            code=ErrorCode.TOKEN_INVALID,
            message="Authorization 格式错误，应为 'Bearer <token>'",
            http_status=401,
        )

    payload = decode_token(parts[1])
    if payload.get("type") != "access":
        raise BusinessError(
            code=ErrorCode.TOKEN_INVALID, message="Token 类型错误", http_status=401
        )

    jti = payload.get("jti")
    if jti and await is_token_blacklisted(jti):
        raise BusinessError(
            code=ErrorCode.TOKEN_INVALID, message="Token 已被撤销", http_status=401
        )

    return payload


async def get_current_user_id(
    payload: dict = Depends(get_current_token_payload),
) -> str:
    """从已校验的 payload 中取出当前用户 ID（供业务接口使用）。"""
    user_id = payload.get("sub")
    if not user_id:
        raise BusinessError(code=ErrorCode.TOKEN_INVALID, http_status=401)
    return user_id


def remaining_ttl_seconds(payload: dict) -> int:
    """根据 payload 的 exp 计算剩余有效期（秒）。"""
    return int(payload["exp"] - time.time())


# ========== 设备会话 ==========


def _session_key(user_id: str, device_id: str) -> str:
    return f"session:{user_id}:{device_id}"


def _sessions_set_key(user_id: str) -> str:
    return f"user_sessions:{user_id}"


def parse_device_name(user_agent: str) -> str:
    """从 User-Agent 拼可读设备名，不引入额外依赖。"""
    if not user_agent:
        return "Unknown Device"

    os_name = "Unknown"
    if "Windows" in user_agent:
        os_name = "Windows"
    elif "Mac OS" in user_agent or "Macintosh" in user_agent:
        os_name = "macOS"
    elif "iPhone" in user_agent or "iPad" in user_agent:
        os_name = "iOS"
    elif "Android" in user_agent:
        os_name = "Android"
    elif "Linux" in user_agent:
        os_name = "Linux"

    browser = "Unknown"
    if "Edg" in user_agent:
        browser = "Edge"
    elif "Chrome" in user_agent and "Safari" in user_agent:
        browser = "Chrome"
    elif "Safari" in user_agent:
        browser = "Safari"
    elif "Firefox" in user_agent:
        browser = "Firefox"

    return f"{browser} / {os_name}"


def _client_ip(request: Request | None) -> str:
    if request is None:
        return ""
    forwarded = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else ""


async def store_device_session(
    user_id: str,
    device_id: str,
    jti: str,
    device_name: str | None = None,
    request: Request | None = None,
) -> None:
    """登录时写入或覆盖设备会话；created_at 在覆盖时保留。"""
    redis = get_redis()
    now = datetime.now(timezone.utc).isoformat()
    user_agent = request.headers.get("user-agent", "") if request else ""
    if not device_name and user_agent:
        device_name = parse_device_name(user_agent)

    session_key = _session_key(user_id, device_id)
    ttl = _refresh_ttl_seconds()
    existing = await redis.hget(session_key, "created_at")
    session_data = {
        "jti": jti,
        "device_name": device_name or "Unknown Device",
        "ip": _client_ip(request),
        "user_agent": user_agent,
        "created_at": existing or now,
        "last_used": now,
    }
    for field, value in session_data.items():
        await redis.hset(session_key, field, value)
    await redis.expire(session_key, ttl)
    await redis.sadd(_sessions_set_key(user_id), device_id)
    await redis.expire(_sessions_set_key(user_id), ttl)


async def get_device_session(user_id: str, device_id: str) -> dict | None:
    data = await get_redis().hgetall(_session_key(user_id, device_id))
    if not data:
        return None
    return {
        "jti": data.get("jti", ""),
        "device_name": data.get("device_name", ""),
        "ip": data.get("ip", ""),
        "user_agent": data.get("user_agent", ""),
        "created_at": data.get("created_at", ""),
        "last_used": data.get("last_used", ""),
    }


async def update_device_session(
    user_id: str,
    device_id: str,
    new_jti: str,
    request: Request | None = None,
) -> None:
    """refresh 轮换后更新 jti / last_used / ip，并刷新 TTL。"""
    redis = get_redis()
    session_key = _session_key(user_id, device_id)
    if not await redis.exists(session_key):
        return
    now = datetime.now(timezone.utc).isoformat()
    ttl = _refresh_ttl_seconds()
    await redis.hset(session_key, "jti", new_jti)
    await redis.hset(session_key, "last_used", now)
    ip = _client_ip(request)
    if ip:
        await redis.hset(session_key, "ip", ip)
    await redis.expire(session_key, ttl)
    await redis.expire(_sessions_set_key(user_id), ttl)


async def delete_device_session(user_id: str, device_id: str) -> None:
    redis = get_redis()
    await redis.delete(_session_key(user_id, device_id))
    await redis.srem(_sessions_set_key(user_id), device_id)


async def list_user_sessions(
    user_id: str, current_device_id: str | None = None
) -> list[dict]:
    redis = get_redis()
    device_ids = await redis.smembers(_sessions_set_key(user_id))
    sessions: list[dict] = []
    for device_id in device_ids:
        data = await redis.hgetall(_session_key(user_id, device_id))
        if not data:
            await redis.srem(_sessions_set_key(user_id), device_id)
            continue
        sessions.append(
            {
                "device_id": device_id,
                "device_name": data.get("device_name", "Unknown Device"),
                "ip": data.get("ip", ""),
                "created_at": data.get("created_at", ""),
                "last_used": data.get("last_used", ""),
                "is_current": bool(current_device_id)
                and device_id == current_device_id,
            }
        )
    sessions.sort(key=lambda item: item.get("last_used", ""), reverse=True)
    return sessions


async def enforce_session_limit(user_id: str, max_sessions: int = 5) -> None:
    """超出上限时按 created_at 踢掉最旧设备，并吊销它的 refresh。"""
    redis = get_redis()
    device_ids = await redis.smembers(_sessions_set_key(user_id))
    if not device_ids or len(device_ids) <= max_sessions:
        return

    timed: list[tuple[str, str]] = []
    for device_id in device_ids:
        created_at = await redis.hget(_session_key(user_id, device_id), "created_at")
        timed.append((device_id, created_at or ""))
    timed.sort(key=lambda item: item[1])

    for device_id, _ in timed[: len(timed) - max_sessions]:
        old_jti = await redis.hget(_session_key(user_id, device_id), "jti")
        if old_jti:
            await redis.delete(_refresh_key(user_id, old_jti))
        await redis.delete(_session_key(user_id, device_id))
        await redis.srem(_sessions_set_key(user_id), device_id)


async def _clear_all_device_sessions(user_id: str) -> None:
    redis = get_redis()
    device_ids = await redis.smembers(_sessions_set_key(user_id))
    for device_id in device_ids:
        await redis.delete(_session_key(user_id, device_id))
    await redis.delete(_sessions_set_key(user_id))
