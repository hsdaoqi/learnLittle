"""认证相关 Pydantic Schema：注册、登录、Token、用户信息。

本阶段注册仅需用户名 + 密码（邮箱可选）；
默认注册要求邮箱验证码；仅显式关闭 registration_require_email 时兼容旧客户端。
"""

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class UserRegister(BaseModel):
    """用户注册请求。"""

    username: str = Field(min_length=3, max_length=50, description="用户名")
    password: str = Field(min_length=8, max_length=128, description="密码")
    email: str | None = Field(
        default=None, max_length=255, description="注册邮箱（默认必须与验证码一起提供）"
    )
    verification_code: str | None = Field(default=None, min_length=6, max_length=6)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str | None) -> str | None:
        if v is not None and not _EMAIL_RE.match(v):
            raise ValueError("邮箱格式不正确")
        return v


class SendCodeRequest(BaseModel):
    email: str = Field(description="邮箱地址")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("邮箱格式不正确")
        return v


class EmailChangeRequest(BaseModel):
    email: str
    verification_code: str = Field(min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("邮箱格式不正确")
        return v


class NoteExportEmailRequest(BaseModel):
    to: str | None = Field(default=None, description="收件人；空则用当前用户邮箱")
    format: str = Field(default="md", pattern="^(md|txt)$")

    @field_validator("to")
    @classmethod
    def validate_to(cls, v: str | None) -> str | None:
        if v is not None and not _EMAIL_RE.match(v):
            raise ValueError("邮箱格式不正确")
        return v


class UserLogin(BaseModel):
    """用户登录请求。"""

    username: str = Field(description="用户名")
    password: str = Field(description="密码")
    device_id: str | None = Field(
        default=None, max_length=64, description="设备唯一标识"
    )
    device_name: str | None = Field(
        default=None, max_length=100, description="设备可读名称"
    )


class TokenResponse(BaseModel):
    """登录/刷新成功返回的 Token 信息。"""

    access_token: str = Field(description="Access Token（JWT）")
    refresh_token: str = Field(description="Refresh Token（JWT）")
    token_type: str = Field(default="bearer", description="Token 类型")
    expires_in: int = Field(description="Access Token 有效期（秒）")
    device_id: str | None = Field(default=None, description="回传设备标识")


class RefreshTokenRequest(BaseModel):
    """Token 刷新请求。"""

    refresh_token: str = Field(description="Refresh Token")
    device_id: str | None = Field(default=None, max_length=64)


class LogoutRequest(BaseModel):
    """登出请求：携带 refresh_token 一并吊销（可选但推荐）。"""

    refresh_token: str | None = Field(
        default=None, description="当前设备的 Refresh Token"
    )
    device_id: str | None = Field(default=None, max_length=64)


class UserUpdate(BaseModel):
    """个人资料更新；邮箱必须走 /user/change-email。"""

    model_config = {"extra": "forbid"}
    bio: str | None = Field(default=None, max_length=500)


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isalpha() for c in v):
            raise ValueError("密码必须包含字母")
        if not any(c.isdigit() for c in v):
            raise ValueError("密码必须包含数字")
        return v


class SessionInfo(BaseModel):
    device_id: str
    device_name: str | None = None
    ip: str | None = None
    created_at: str | None = None
    last_used: str | None = None
    is_current: bool = False


class UserInfo(BaseModel):
    """用户信息响应。"""

    uuid: str
    username: str
    email: str | None = None
    email_verified: bool = False
    avatar: str | None = None
    bio: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
