"""内置 Agent 工具：绑定当前用户，写操作自己开 session 并 commit。

本阶段不接邮件 / PPT / DeepL / Wolfram。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_service.review_tools import get_today_reviews_tool, mark_reviewed_tool
from app.ai_service.tool_registry import ToolSpec, registry
from app.core.failed_response import BusinessError
from app.models.category import NoteCategory
from app.models.note import Note
from app.models.user import User
from app.rag.note_cards import format_note_search_cards
from app.schemas.note import NoteCreate
from app.services import note_service

logger = logging.getLogger(__name__)

MAX_NOTE_CHARS = 20000


def _clip(text: str, limit: int) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    return text[:limit] + "…"


async def _resolve_category_id(
    db: AsyncSession, user_id: str, name: str | None
) -> str | None:
    if not name or not name.strip():
        return None
    cat = (
        await db.execute(
            select(NoteCategory).where(
                NoteCategory.user_id == user_id,
                NoteCategory.name == name.strip(),
                NoteCategory.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    return cat.id if cat else None


def bind_user_tools(user_id: str, session_factory) -> dict[str, Callable[..., Any]]:
    """把工具闭包绑到当前用户。返回 name → async callable。"""

    async def what_time_is_now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def get_user_info_tools() -> str:
        async with session_factory() as db:
            user = (
                await db.execute(select(User).where(User.uuid == user_id))
            ).scalar_one_or_none()
        if user is None:
            return f"当前用户 ID: {user_id}（用户信息获取失败）"
        email = user.email or "未设置邮箱"
        return f"用户名: {user.username}\n邮箱: {email}\n用户ID: {user_id}"

    async def search_notes_tool(query: str, top_k: int = 5) -> str:
        top_k = max(1, min(int(top_k or 5), 10))
        cards: list[dict] = []
        async with session_factory() as db:
            data = await note_service.keyword_search(db, user_id, query, top_k)
            hits = data.get("results") or []
            for item in hits:
                summary = item.get("note") or {}
                note_id = summary.get("id")
                if not note_id:
                    continue
                try:
                    note = await note_service.get_active_note(db, user_id, note_id)
                except BusinessError:
                    continue
                cards.append(
                    {
                        "title": note.title,
                        "note_id": note.id,
                        "excerpt": note.content or "",
                    }
                )
        if not cards:
            try:
                from app.rag.vector_store import get_vector_store

                vec = await get_vector_store().search(
                    query, user_id, top_k, collection="notes"
                )
            except Exception as exc:
                logger.warning("笔记向量搜索失败: %s", exc)
                vec = []
            for item in vec:
                note_id = str(item.get("note_id") or "").strip()
                title = (item.get("filename") or item.get("title") or "未命名").strip()
                if not note_id:
                    continue
                cards.append(
                    {
                        "title": title,
                        "note_id": note_id,
                        "excerpt": item.get("content") or "",
                    }
                )
        return format_note_search_cards(query, cards)

    async def get_note_content_tool(note_id: str) -> str:
        async with session_factory() as db:
            try:
                note = await note_service.get_active_note(db, user_id, note_id)
            except BusinessError:
                return "未找到笔记或无权访问"
        tags = ",".join(note.tags or []) or "无"
        updated = note.updated_at.strftime("%Y-%m-%d") if note.updated_at else "未知"
        body = _clip(note.content or "", MAX_NOTE_CHARS)
        return (
            f"# {note.title}\n\n> 标签：{tags} | 更新日期：{updated}\n\n---\n\n{body}"
        )

    async def get_note_stats_tool() -> str:
        async with session_factory() as db:
            category_name = func.coalesce(NoteCategory.name, "未分类").label(
                "category_name"
            )
            rows = list(
                (
                    await db.execute(
                        select(category_name, func.count().label("note_count"))
                        .select_from(Note)
                        .outerjoin(
                            NoteCategory,
                            and_(
                                Note.category_id == NoteCategory.id,
                                NoteCategory.deleted_at.is_(None),
                            ),
                        )
                        .where(
                            Note.user_id == user_id,
                            Note.deleted_at.is_(None),
                            (Note.category_id.is_(None))
                            | (NoteCategory.id.is_not(None)),
                        )
                        .group_by(NoteCategory.id, NoteCategory.name)
                    )
                ).all()
            )
        if not rows:
            return "暂无笔记"
        ordered = sorted(rows, key=lambda r: r[0] == "未分类")
        lines = [f"- {name}: {count} 篇" for name, count in ordered]
        return "笔记分类统计:\n" + "\n".join(lines)

    async def today_reviews() -> str:
        async with session_factory() as db:
            return await get_today_reviews_tool(db, user_id)

    async def mark_reviewed(review_id: int) -> str:
        async with session_factory() as db:
            try:
                text = await mark_reviewed_tool(db, user_id, int(review_id))
                await db.commit()
                return text
            except BusinessError:
                await db.rollback()
                return "未找到回顾记录或无权操作"
            except Exception as exc:
                await db.rollback()
                logger.warning("标记回顾失败: %s", exc)
                return "标记回顾失败，请稍后重试"

    async def create_note_tool(
        title: str, content: str, tags: str = "", category: str = ""
    ) -> str:
        tag_list = [part.strip() for part in (tags or "").split(",") if part.strip()]
        async with session_factory() as db:
            category_id = await _resolve_category_id(db, user_id, category)
            note = await note_service.create_note(
                db,
                user_id,
                NoteCreate(
                    title=title, content=content, tags=tag_list, category_id=category_id
                ),
            )
            await db.commit()
            return f"笔记创建成功！ID: {note.id}, 标题: {note.title}"

    async def update_note_tool(
        note_id: str,
        title: str | None = None,
        content: str | None = None,
        tags: str | None = None,
        category: str | None = None,
    ) -> str:
        fields: dict[str, Any] = {}
        if title is not None:
            fields["title"] = title
        if content is not None:
            fields["content"] = content
        if tags is not None:
            fields["tags"] = [part.strip() for part in tags.split(",") if part.strip()]
        async with session_factory() as db:
            if category is not None:
                fields["category_id"] = await _resolve_category_id(
                    db, user_id, category
                )
            if not fields:
                return "未提供任何要更新的字段"
            try:
                note = await note_service.update_note(db, user_id, note_id, fields)
                await db.commit()
                return f"笔记更新成功！ID: {note.id}, 标题: {note.title}"
            except BusinessError:
                await db.rollback()
                return "未找到笔记或无权访问"
            except Exception as exc:
                await db.rollback()
                logger.warning("笔记更新失败: %s", exc)
                return "笔记更新失败，请稍后重试"

    async def get_related_notes_tool(note_title: str, top_k: int = 3) -> str:
        return await search_notes_tool(note_title, top_k)

    return {
        "what_time_is_now": what_time_is_now,
        "get_user_info_tools": get_user_info_tools,
        "search_notes_tool": search_notes_tool,
        "get_note_content_tool": get_note_content_tool,
        "get_note_stats_tool": get_note_stats_tool,
        "get_today_reviews_tool": today_reviews,
        "mark_reviewed_tool": mark_reviewed,
        "create_note_tool": create_note_tool,
        "update_note_tool": update_note_tool,
        "get_related_notes_tool": get_related_notes_tool,
    }


def _empty_params() -> dict:
    return {"type": "object", "properties": {}, "additionalProperties": False}


def register_builtin_tools() -> None:
    if registry.get("what_time_is_now") is not None:
        return
    specs = [
        ToolSpec(
            "what_time_is_now",
            "获取当前日期和时间，返回格式为 YYYY-MM-DD HH:MM:SS",
            _empty_params(),
            lambda: None,
            "base",
        ),
        ToolSpec(
            "get_user_info_tools",
            "获取当前登录用户的基本信息（用户名、邮箱、用户ID）",
            _empty_params(),
            lambda: None,
            "base",
        ),
        ToolSpec(
            "search_notes_tool",
            "搜索用户笔记。返回标题和 ID 摘要；需要全文时再调用 get_note_content_tool。",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "top_k": {"type": "integer", "description": "返回条数，默认 5"},
                },
                "required": ["query"],
            },
            lambda: None,
            "note_read",
        ),
        ToolSpec(
            "get_note_content_tool",
            "获取单篇笔记的完整内容。note_id 来自 search_notes_tool。",
            {
                "type": "object",
                "properties": {"note_id": {"type": "string"}},
                "required": ["note_id"],
            },
            lambda: None,
            "note_read",
        ),
        ToolSpec(
            "get_note_stats_tool",
            "获取各分类的笔记数量统计",
            _empty_params(),
            lambda: None,
            "note_read",
        ),
        ToolSpec(
            "get_related_notes_tool",
            "按标题找相关笔记",
            {
                "type": "object",
                "properties": {
                    "note_title": {"type": "string"},
                    "top_k": {"type": "integer"},
                },
                "required": ["note_title"],
            },
            lambda: None,
            "note_read",
        ),
        ToolSpec(
            "create_note_tool",
            "创建一条新笔记",
            {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "tags": {"type": "string", "description": "逗号分隔标签"},
                    "category": {"type": "string", "description": "分类名称"},
                },
                "required": ["title", "content"],
            },
            lambda: None,
            "note_write",
        ),
        ToolSpec(
            "update_note_tool",
            "更新已有笔记。只传要改的字段。",
            {
                "type": "object",
                "properties": {
                    "note_id": {"type": "string"},
                    "title": {"type": "string"},
                    "content": {"type": "string"},
                    "tags": {"type": "string"},
                    "category": {"type": "string"},
                },
                "required": ["note_id"],
            },
            lambda: None,
            "note_write",
        ),
        ToolSpec(
            "get_today_reviews_tool",
            "获取今日待回顾的笔记列表",
            _empty_params(),
            lambda: None,
            "review",
        ),
        ToolSpec(
            "mark_reviewed_tool",
            "标记一条回顾记录为已完成",
            {
                "type": "object",
                "properties": {"review_id": {"type": "integer"}},
                "required": ["review_id"],
            },
            lambda: None,
            "review",
        ),
    ]
    for spec in specs:
        registry.register(spec)


register_builtin_tools()
