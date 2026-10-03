"""聊天服务：会话 CRUD 与当前问答流程共用的数据辅助函数。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.core.failed_response import BusinessError, ErrorCode
from app.models.chat import ChatMessage, ChatSession
from app.rag.chat_cache import (
    DEFAULT_BUFFER_SIZE,
    DEFAULT_SESSION_LIST_TTL,
    delete_messages,
    get_session_list,
    invalidate_session_list,
    push_message,
    set_session_list,
)
from app.schemas.chat import ChatMessageResponse, ChatSessionResponse


def _session_dump(session: ChatSession) -> dict:
    return ChatSessionResponse.model_validate(session).model_dump(mode="json")


def _message_dump(message: ChatMessage) -> dict:
    return ChatMessageResponse.model_validate(message).model_dump(mode="json")


def _cache_on(settings: Settings | None) -> bool:
    return True if settings is None else settings.chat_cache_enabled


def _cache_buffer(settings: Settings | None) -> int:
    return settings.chat_cache_buffer_size if settings else DEFAULT_BUFFER_SIZE


def _cache_ttl(settings: Settings | None) -> int:
    return (
        settings.chat_cache_session_ttl_seconds
        if settings
        else DEFAULT_SESSION_LIST_TTL
    )


async def list_sessions(
    db: AsyncSession, user_id: str, settings: Settings | None = None
) -> list[dict]:
    if _cache_on(settings):
        cached = await get_session_list(user_id)
        if cached is not None:
            return cached
    rows = (
        (
            await db.execute(
                select(ChatSession)
                .where(ChatSession.user_id == user_id)
                .order_by(ChatSession.updated_at.desc())
            )
        )
        .scalars()
        .all()
    )
    data = [_session_dump(s) for s in rows]
    if _cache_on(settings):
        await set_session_list(user_id, data, _cache_ttl(settings))
    return data


async def get_session(db: AsyncSession, user_id: str, session_id: str) -> ChatSession:
    session = (
        await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if session is None:
        raise BusinessError(code=ErrorCode.SESSION_NOT_FOUND, http_status=404)
    return session


async def create_session(
    db: AsyncSession,
    user_id: str,
    title: str = "新对话",
    settings: Settings | None = None,
) -> ChatSession:
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    await db.flush()
    await db.refresh(session)
    if _cache_on(settings):
        await invalidate_session_list(user_id)
    return session


async def update_session_title(
    db: AsyncSession,
    user_id: str,
    session_id: str,
    title: str,
    settings: Settings | None = None,
) -> ChatSession:
    session = await get_session(db, user_id, session_id)
    session.title = title
    session.title_manual = True
    await db.flush()
    await db.refresh(session)
    if _cache_on(settings):
        await invalidate_session_list(user_id)
    return session


async def delete_session(
    db: AsyncSession, user_id: str, session_id: str, settings: Settings | None = None
) -> None:
    session = await get_session(db, user_id, session_id)
    await db.delete(session)
    await db.flush()
    if _cache_on(settings):
        await invalidate_session_list(user_id)
        await delete_messages(session_id)


async def list_messages(db: AsyncSession, user_id: str, session_id: str) -> list[dict]:
    await get_session(db, user_id, session_id)
    rows = (
        (
            await db.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
            )
        )
        .scalars()
        .all()
    )
    return [_message_dump(m) for m in rows]


async def _add_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    content: str,
    settings: Settings | None = None,
    idempotency_key: str | None = None,
) -> ChatMessage:
    message = ChatMessage(
        session_id=session_id, role=role, content=content,
        idempotency_key=idempotency_key,
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)
    if _cache_on(settings):
        await push_message(session_id, message, _cache_buffer(settings))
    return message
