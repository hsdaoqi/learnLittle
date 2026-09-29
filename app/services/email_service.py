"""SMTP 邮件：验证码、改绑邮箱、笔记导出。

测试注入 send 函数，不打真实 SMTP。
验证码 Redis：email_code:{email} TTL 300s；错误计数 5 次锁定。
"""

from __future__ import annotations

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path

from app.config import Settings, get_settings
from app.core.failed_response import BusinessError, ErrorCode
from app.db.redis_client import get_redis

logger = logging.getLogger(__name__)

CODE_TTL = 300
MAX_CODE_ATTEMPTS = 5
ERROR_COUNT_TTL = 900
COOLDOWN_SECONDS = 60
IP_HOURLY_LIMIT = 10

SendFn = Callable[..., Awaitable[None]]

_injected: SendFn | None = None

TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "templates"
    / "email"
    / "verification_code.html"
)


def set_send_email_fn(fn: SendFn | None) -> None:
    global _injected
    _injected = fn


def get_send_email_fn() -> SendFn | None:
    return _injected


def smtp_available(settings: Settings | None = None) -> bool:
    if _injected is not None:
        return True
    settings = settings or get_settings()
    return bool(
        settings.smtp_host and settings.smtp_username and settings.smtp_password
    )


def generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


def _build_message(
    *,
    settings: Settings,
    to: str,
    subject: str,
    body: str,
    html: str | None = None,
    attachments: list[dict] | None = None,
) -> MIMEMultipart:
    has_attachments = bool(attachments)
    if has_attachments:
        msg = MIMEMultipart("mixed")
        alt = MIMEMultipart("alternative")
        alt.attach(MIMEText(body, "plain", "utf-8"))
        if html:
            alt.attach(MIMEText(html, "html", "utf-8"))
        msg.attach(alt)
    else:
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(body, "plain", "utf-8"))
        if html:
            msg.attach(MIMEText(html, "html", "utf-8"))

    msg["From"] = formataddr(
        (settings.smtp_from_name, settings.smtp_username or "noreply@local")
    )
    msg["To"] = to
    msg["Subject"] = str(Header(subject, "utf-8"))

    for att in attachments or []:
        mime = att.get("mime") or "application/octet-stream"
        main_type, _, sub_type = mime.partition("/")
        data = att["data"]
        if main_type == "text":
            text = data.decode("utf-8") if isinstance(data, bytes) else data
            part = MIMEText(text, sub_type or "plain", "utf-8")
        else:
            part = MIMEApplication(data, _subtype=sub_type or "octet-stream")
        part.add_header(
            "Content-Disposition", "attachment", filename=("utf-8", "", att["filename"])
        )
        msg.attach(part)
    return msg


async def send_email(
    to: str,
    subject: str,
    body: str,
    *,
    html: str | None = None,
    attachments: list[dict] | None = None,
    settings: Settings | None = None,
    retries: int = 2,
    backoff: float = 2.0,
) -> None:
    settings = settings or get_settings()
    if _injected is not None:
        await _injected(to, subject, body, html, attachments)
        return
    if not smtp_available(settings):
        raise BusinessError(
            code=ErrorCode.EMAIL_SEND_FAILED, http_status=503, message="SMTP 未配置"
        )

    import aiosmtplib

    msg = _build_message(
        settings=settings,
        to=to,
        subject=subject,
        body=body,
        html=html,
        attachments=attachments,
    )
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            async with aiosmtplib.SMTP(
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                timeout=10,
                start_tls=True,
            ) as smtp:
                await smtp.login(settings.smtp_username, settings.smtp_password)
                await smtp.send_message(msg)
            logger.info("邮件发送成功: to=%s subject=%s", to, subject)
            return
        except aiosmtplib.SMTPAuthenticationError:
            logger.error("SMTP 认证失败")
            raise BusinessError(
                code=ErrorCode.EMAIL_SEND_FAILED, http_status=502
            ) from None
        except (
            aiosmtplib.SMTPConnectError,
            aiosmtplib.SMTPTimeoutError,
            OSError,
        ) as exc:
            last_error = exc
            if attempt < retries:
                wait = backoff * (2**attempt)
                logger.warning("邮件瞬态失败，%ss 后重试: %s", wait, exc)
                await asyncio.sleep(wait)
    logger.error("邮件发送失败: to=%s error=%s", to, last_error)
    raise BusinessError(code=ErrorCode.EMAIL_SEND_FAILED, http_status=502)


def _render_verification_html(code: str, settings: Settings) -> str | None:
    try:
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    return (
        template.replace("{{app_name}}", settings.smtp_from_name or settings.app_name)
        .replace("{{code}}", code)
        .replace("{{expire_minutes}}", str(CODE_TTL // 60))
    )


async def send_verification_code(to: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    if not smtp_available(settings):
        raise BusinessError(code=ErrorCode.EMAIL_SEND_FAILED, http_status=503)
    code = generate_code()
    redis = get_redis()
    await redis.set(f"email_code:{to}", code, ex=CODE_TTL)
    html = _render_verification_html(code, settings)
    await send_email(
        to,
        f"【{settings.smtp_from_name or settings.app_name}】邮箱验证码",
        f"您的验证码是：{code}，{CODE_TTL // 60} 分钟内有效。\n如非本人操作，请忽略本邮件。",
        html=html,
        settings=settings,
    )
    return code


async def verify_code(email: str, code: str) -> bool:
    redis = get_redis()
    key = f"email_code:{email}"
    stored = await redis.get(key)
    if stored is None or stored != code:
        err_key = f"email_code_errors:{email}"
        count = await redis.incr(err_key)
        if count == 1:
            await redis.expire(err_key, ERROR_COUNT_TTL)
        if count >= MAX_CODE_ATTEMPTS:
            await redis.delete(key)
            logger.warning("邮箱验证码错误次数过多: %s", email)
        return False
    await redis.delete(key)
    await redis.delete(f"email_code_errors:{email}")
    return True


async def enforce_send_code_limits(email: str, client_ip: str | None) -> None:
    redis = get_redis()
    cooldown_key = f"email_code_cooldown:{email}"
    if await redis.exists(cooldown_key):
        ttl = await redis.ttl(cooldown_key)
        raise BusinessError(
            code=ErrorCode.ENDPOINT_RATE_LIMIT,
            message=f"发送过于频繁，请 {max(ttl, 1)} 秒后再试",
            http_status=429,
        )
    if client_ip:
        from datetime import datetime

        hour_bucket = datetime.now().strftime("%Y%m%d%H")
        ip_key = f"send_code_ip:{client_ip}:{hour_bucket}"
        ip_count = await redis.incr(ip_key)
        if ip_count == 1:
            await redis.expire(ip_key, 3600)
        if ip_count > IP_HOURLY_LIMIT:
            raise BusinessError(
                code=ErrorCode.ENDPOINT_RATE_LIMIT,
                message="请求过于频繁，请稍后再试",
                http_status=429,
            )


async def mark_send_code_cooldown(email: str) -> None:
    await get_redis().set(f"email_code_cooldown:{email}", "1", ex=COOLDOWN_SECONDS)


def note_attachment(title: str, content: str, fmt: str) -> dict:
    safe = (
        "".join(ch if ch.isalnum() or ch in "._- " else "_" for ch in title).strip()
        or "note"
    )
    if fmt == "txt":
        return {
            "filename": f"{safe}.txt",
            "data": content.encode("utf-8"),
            "mime": "text/plain",
        }
    return {
        "filename": f"{safe}.md",
        "data": content.encode("utf-8"),
        "mime": "text/markdown",
    }
