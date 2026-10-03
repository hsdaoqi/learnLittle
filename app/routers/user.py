"""用户认证与资料路由。

端点：
- POST /auth/register - 用户注册（默认要求邮箱验证码）
- POST /auth/sse-token - 一次性 60 秒聊天凭证
- POST /auth/login    - 用户登录，返回 Access/Refresh Token
- POST /auth/refresh  - 刷新 Access Token（白名单校验 + 轮换）
- POST /auth/logout   - 登出：拉黑 Access Token + 吊销 Refresh Token
- GET  /auth/sessions - 活跃设备列表
- DELETE /auth/sessions/{device_id} - 撤销指定设备
- GET  /user/me       - 获取当前登录用户信息
- PUT  /user/me       - 更新简介
- POST /user/me/password - 改密码（吊销全部 refresh）
- POST /file/avatar   - 上传头像

安全机制（Redis）：
- 连续 5 次登录失败锁定 15 分钟
- Refresh Token 白名单：只有登记过的 token 才能刷新，轮换后旧票立即作废
- Access Token 黑名单：登出后剩余有效期内不可再用
- 设备会话：同一 device_id 重复登录轮换旧 refresh；最多 5 台
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.failed_response import BusinessError, ErrorCode
from app.core.success_response import success_response
from app.db.database import get_db_session
from app.models.user import User
from app.schemas.auth import (
    EmailChangeRequest,
    LogoutRequest,
    PasswordChange,
    RefreshTokenRequest,
    SendCodeRequest,
    TokenResponse,
    UserInfo,
    UserLogin,
    UserRegister,
    UserUpdate,
)
from app.services import email_service
from app.utils.auth_utils import (
    blacklist_access_token,
    check_login_attempts,
    clear_login_attempts,
    create_access_token,
    create_refresh_token,
    decode_token,
    delete_device_session,
    enforce_session_limit,
    get_current_token_payload,
    get_current_user_id,
    get_device_session,
    hash_password,
    list_user_sessions,
    record_login_failure,
    remaining_ttl_seconds,
    revoke_all_refresh_tokens,
    revoke_refresh_token,
    store_device_session,
    store_refresh_token,
    update_device_session,
    validate_password_strength,
    verify_password,
    verify_refresh_token,
)
from app.utils.file_handler import (
    ensure_dir,
    read_upload_limited,
    validate_avatar_file,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/auth/register", summary="用户注册")
async def register(data: UserRegister, request: Request, db: AsyncSession = Depends(get_db_session)):
    """校验用户名/邮箱唯一性与密码强度，创建用户记录。"""
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise BusinessError(code=ErrorCode.USERNAME_EXISTS, http_status=409)

    verified = False
    email = data.email
    if request.app.state.settings.registration_require_email and not (
        email and data.verification_code
    ):
        raise BusinessError(
            code=ErrorCode.EMAIL_CODE_INVALID, message="注册必须填写邮箱并完成验证码验证",
        )
    if email and data.verification_code:
        if not await email_service.verify_code(email, data.verification_code):
            raise BusinessError(code=ErrorCode.EMAIL_CODE_INVALID, http_status=400)
        verified = True
    elif email and not data.verification_code:
        # 兼容旧客户端：没验证码就只存邮箱，不算已验证
        verified = False

    if email:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise BusinessError(code=ErrorCode.EMAIL_EXISTS, http_status=409)

    is_valid, error_msg = validate_password_strength(data.password)
    if not is_valid:
        raise BusinessError(code=ErrorCode.INVALID_PARAMETER, message=error_msg)

    user = User(
        uuid=str(uuid.uuid4()),
        username=data.username,
        email=email,
        email_verified=verified,
        password=hash_password(data.password),
    )
    db.add(user)
    await db.flush()

    # 为新用户播种默认分类树（与用户记录同一事务提交）
    from app.services.category_service import seed_template_tree

    await seed_template_tree(db, user.uuid)

    return success_response(data={"user_id": user.uuid, "username": user.username})


@router.post("/auth/sse-token", summary="获取一次性 SSE 短期 Token")
async def sse_token(user_id: str = Depends(get_current_user_id)):
    from app.utils.auth_utils import create_sse_token

    token = await create_sse_token(user_id)
    return success_response(data={"token": token, "expires_in": 60})


@router.post("/auth/send-code", summary="发送邮箱验证码")
async def send_code(data: SendCodeRequest, request: Request):
    client_ip = (
        request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        or request.headers.get("X-Real-IP", "").strip()
        or (request.client.host if request.client else None)
    )
    await email_service.enforce_send_code_limits(data.email, client_ip)
    try:
        await email_service.send_verification_code(data.email)
    except BusinessError:
        raise
    except Exception as exc:
        raise BusinessError(code=ErrorCode.EMAIL_SEND_FAILED, http_status=502) from exc
    await email_service.mark_send_code_cooldown(data.email)
    return success_response(message="验证码已发送")


@router.post("/user/change-email", summary="修改/绑定邮箱")
async def change_email(
    data: EmailChangeRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    if not await email_service.verify_code(data.email, data.verification_code):
        raise BusinessError(code=ErrorCode.EMAIL_CODE_INVALID, http_status=400)
    existing = (
        await db.execute(select(User).where(User.email == data.email))
    ).scalar_one_or_none()
    if existing and existing.uuid != user_id:
        raise BusinessError(code=ErrorCode.EMAIL_EXISTS, http_status=409)
    user = (
        await db.execute(select(User).where(User.uuid == user_id))
    ).scalar_one_or_none()
    if not user:
        raise BusinessError(code=ErrorCode.USER_NOT_FOUND, http_status=404)
    user.email = data.email
    user.email_verified = True
    await db.flush()
    return success_response(message="邮箱修改成功")


@router.post("/auth/login", summary="用户登录")
async def login(
    data: UserLogin, request: Request, db: AsyncSession = Depends(get_db_session)
):
    """校验用户名密码，签发 Access Token + Refresh Token（并登记白名单）。"""
    await check_login_attempts(data.username)

    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password):
        await record_login_failure(data.username)
        raise BusinessError(code=ErrorCode.PASSWORD_ERROR, http_status=401)

    await clear_login_attempts(data.username)

    if data.device_id:
        existing = await get_device_session(user.uuid, data.device_id)
        if existing and existing.get("jti"):
            await revoke_refresh_token(user.uuid, existing["jti"])

    refresh_token, refresh_jti = create_refresh_token(user.uuid)
    await store_refresh_token(user.uuid, refresh_jti)

    settings = get_settings()
    if data.device_id:
        await store_device_session(
            user.uuid,
            data.device_id,
            refresh_jti,
            device_name=data.device_name,
            request=request,
        )
        await enforce_session_limit(user.uuid, settings.max_device_sessions)

    return success_response(
        data=TokenResponse(
            access_token=create_access_token(user.uuid),
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            device_id=data.device_id,
        ).model_dump()
    )


@router.post("/auth/refresh", summary="刷新 Access Token")
async def refresh(data: RefreshTokenRequest, request: Request):
    """校验白名单后签发新 Access Token，并轮换 Refresh Token。

    轮换：旧 refresh token 立即从白名单移除，新 token 重新登记。
    泄露的旧票在下一次使用时会被发现。
    """
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise BusinessError(
            code=ErrorCode.TOKEN_INVALID, message="Token 类型错误", http_status=401
        )

    user_id = payload.get("sub")
    jti = payload.get("jti")
    if not user_id or not jti:
        raise BusinessError(code=ErrorCode.TOKEN_INVALID, http_status=401)

    if not await verify_refresh_token(user_id, jti):
        raise BusinessError(code=ErrorCode.REFRESH_TOKEN_INVALID, http_status=401)

    await revoke_refresh_token(user_id, jti)
    new_refresh_token, new_jti = create_refresh_token(user_id)
    await store_refresh_token(user_id, new_jti)
    if data.device_id:
        await update_device_session(user_id, data.device_id, new_jti, request)

    settings = get_settings()
    return success_response(
        data=TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            device_id=data.device_id,
        ).model_dump()
    )


@router.post("/auth/logout", summary="用户登出")
async def logout(
    data: LogoutRequest,
    payload: dict = Depends(get_current_token_payload),
):
    """登出：Access Token 拉黑至自然过期，Refresh Token 从白名单吊销。

    Access Token 本身无状态无法作废，黑名单保证它在剩余有效期（≤30 分钟）内失效。
    """
    user_id = payload["sub"]
    jti = payload.get("jti", "")
    await blacklist_access_token(jti, remaining_ttl_seconds(payload))

    revoked = 0
    if data.refresh_token:
        refresh_payload = decode_token(data.refresh_token)
        refresh_jti = refresh_payload.get("jti", "")
        if (
            refresh_payload.get("type") == "refresh"
            and refresh_payload.get("sub") == user_id
            and await verify_refresh_token(user_id, refresh_jti)
        ):
            await revoke_refresh_token(user_id, refresh_jti)
            revoked = 1

    if data.device_id:
        session = await get_device_session(user_id, data.device_id)
        if session and session.get("jti"):
            await revoke_refresh_token(user_id, session["jti"])
            revoked = 1
        await delete_device_session(user_id, data.device_id)

    return success_response(data={"refresh_tokens_revoked": revoked})


@router.get("/user/me", summary="获取当前用户信息")
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    """根据 Access Token 返回当前登录用户的信息。"""
    result = await db.execute(select(User).where(User.uuid == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise BusinessError(code=ErrorCode.USER_NOT_FOUND, http_status=404)

    return success_response(data=UserInfo.model_validate(user).model_dump(mode="json"))


@router.put("/user/me", summary="更新个人资料")
async def update_me(
    data: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    user = (
        await db.execute(select(User).where(User.uuid == user_id))
    ).scalar_one_or_none()
    if not user:
        raise BusinessError(code=ErrorCode.USER_NOT_FOUND, http_status=404)
    if data.bio is not None:
        user.bio = data.bio
    await db.flush()
    return success_response(message="更新成功")


@router.post("/user/me/password", summary="修改密码")
async def change_password(
    data: PasswordChange,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    user = (
        await db.execute(select(User).where(User.uuid == user_id))
    ).scalar_one_or_none()
    if not user:
        raise BusinessError(code=ErrorCode.USER_NOT_FOUND, http_status=404)
    if not verify_password(data.old_password, user.password):
        raise BusinessError(code=ErrorCode.PASSWORD_ERROR, http_status=403)

    is_valid, error_msg = validate_password_strength(data.new_password)
    if not is_valid:
        raise BusinessError(code=ErrorCode.INVALID_PARAMETER, message=error_msg)

    user.password = hash_password(data.new_password)
    await db.flush()
    await revoke_all_refresh_tokens(user_id)
    return success_response(message="密码修改成功")


@router.post("/file/avatar", summary="上传头像")
async def upload_avatar(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    settings = request.app.state.settings
    content = await read_upload_limited(file, settings.max_avatar_size_mb)
    ext = validate_avatar_file(
        file.filename or "",
        len(content),
        content,
        settings.max_avatar_size_mb,
    )

    avatar_dir = Path(settings.avatar_dir) / user_id
    ensure_dir(str(avatar_dir))
    stored_name = f"avatar_{int(datetime.now().timestamp() * 1000)}{ext}"
    file_path = avatar_dir / stored_name
    file_path.write_bytes(content)

    user = (
        await db.execute(select(User).where(User.uuid == user_id))
    ).scalar_one_or_none()
    if user and user.avatar:
        old_path = Path(settings.avatar_dir) / user_id / Path(user.avatar).name
        if old_path.exists() and old_path.is_file():
            try:
                old_path.unlink()
            except OSError as exc:
                logger.warning("删除旧头像失败: %s", exc)

    avatar_url = f"/static/avatars/{user_id}/{stored_name}"
    if user:
        user.avatar = avatar_url
        await db.flush()

    return success_response(data={"avatar_url": avatar_url, "filename": stored_name})


@router.get("/auth/sessions", summary="查看活跃设备")
async def get_sessions(
    request: Request,
    user_id: str = Depends(get_current_user_id),
):
    current_device_id = request.headers.get("X-Device-Id")
    sessions = await list_user_sessions(user_id, current_device_id)
    return success_response(data={"sessions": sessions})


@router.delete("/auth/sessions/{device_id}", summary="撤销设备会话")
async def revoke_session(
    device_id: str,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    payload: dict = Depends(get_current_token_payload),
):
    session = await get_device_session(user_id, device_id)
    if not session:
        raise BusinessError(code=ErrorCode.DEVICE_SESSION_NOT_FOUND, http_status=404)

    old_jti = session.get("jti")
    if old_jti:
        await revoke_refresh_token(user_id, old_jti)
    await delete_device_session(user_id, device_id)

    current_device_id = request.headers.get("X-Device-Id")
    if current_device_id == device_id:
        await blacklist_access_token(
            payload.get("jti", ""), remaining_ttl_seconds(payload)
        )
        return success_response(message="当前会话已注销")
    return success_response(message="会话已撤销")
