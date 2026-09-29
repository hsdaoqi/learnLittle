"""笔记服务：CRUD、批量操作与回收站。

约定：
- 列表/详情只返回未删除笔记，回收站单独入口
- 跨用户访问一律 404（不暴露资源存在性）
- 关键词搜索：MySQL FULLTEXT ngram 优先，失败或无命中回退标题加权 LIKE
- format 只在创建时写入（md / txt），更新接口不含该字段
- 回收站超过 recycle_bin_cleanup_days 天由定时任务物理删除并清向量
"""

import logging
from datetime import datetime, timedelta

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.failed_response import BusinessError, ErrorCode
from app.models.category import NoteCategory
from app.models.note import Note
from app.rag.text_splitter import TextSplitter
from app.rag.vector_store import get_vector_store
from app.schemas.note import NoteBatchRequest, NoteCreate, NoteSummary

logger = logging.getLogger(__name__)


def _not_found() -> BusinessError:
    return BusinessError(code=ErrorCode.NOTE_NOT_FOUND, http_status=404)


def _escape_like(keyword: str) -> str:
    """把用户输入里的 LIKE 通配符当成字面量。"""
    return keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


async def index_note(note: Note) -> None:
    """覆盖写入笔记向量：先删旧切片，空正文则只删不写。"""
    store = get_vector_store()
    store.delete_note(note.id)
    body = f"{note.title}\n\n{note.content}".strip()
    if not body:
        return
    settings = get_settings()
    chunks = TextSplitter(settings.chunk_size, settings.chunk_overlap).split(
        body, "md" if note.format == "md" else "txt"
    )
    if not chunks:
        return
    await store.upsert_chunks(
        documents=[c.content for c in chunks],
        metadatas=[
            {
                "user_id": note.user_id,
                "note_id": note.id,
                "title": note.title,
                "section_title": c.section_title,
                "chunk_index": c.chunk_index,
            }
            for c in chunks
        ],
        ids=[f"{note.id}_{c.chunk_index}" for c in chunks],
        collection="notes",
    )


def drop_note_vectors(note_id: str) -> None:
    try:
        get_vector_store().delete_note(note_id)
    except Exception as exc:
        logger.warning("删除笔记向量失败: note_id=%s err=%s", note_id, exc)


async def _try_index(note: Note) -> None:
    try:
        await index_note(note)
    except Exception as exc:
        logger.warning("写入笔记向量失败: note_id=%s err=%s", note.id, exc)


async def ensure_category(db: AsyncSession, user_id: str, category_id: str) -> None:
    """校验分类存在且属于当前用户（笔记挂载前置条件）。"""
    cat = (
        await db.execute(
            select(NoteCategory).where(
                NoteCategory.id == category_id,
                NoteCategory.user_id == user_id,
                NoteCategory.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if cat is None:
        raise BusinessError(code=ErrorCode.CATEGORY_NOT_FOUND, http_status=404)


async def create_note(db: AsyncSession, user_id: str, data: NoteCreate) -> Note:
    if data.category_id is not None:
        await ensure_category(db, user_id, data.category_id)

    note = Note(
        user_id=user_id,
        title=data.title,
        content=data.content,
        format=data.format,
        tags=data.tags if data.tags is not None else [],
        category_id=data.category_id,
    )
    db.add(note)
    await db.flush()
    # created_at 等服务端默认值列在 MySQL（无 RETURNING）下 flush 后过期，
    # 读取前必须显式刷新，否则触发隐式懒加载报 MissingGreenlet
    await db.refresh(note)
    from app.services.review_service import ensure_review_record

    await ensure_review_record(db, user_id, note.id)
    await _try_index(note)
    return note


async def get_active_note(db: AsyncSession, user_id: str, note_id: str) -> Note:
    note = (
        await db.execute(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == user_id,
                Note.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if note is None:
        raise _not_found()
    return note


async def list_notes(
    db: AsyncSession,
    user_id: str,
    *,
    category_id: str | None = None,
    uncategorized: bool = False,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    stmt = select(Note).where(Note.user_id == user_id, Note.deleted_at.is_(None))
    if uncategorized:
        stmt = stmt.where(Note.category_id.is_(None))
    elif category_id is not None:
        stmt = stmt.where(Note.category_id == category_id)
    if keyword:
        like = f"%{_escape_like(keyword)}%"
        stmt = stmt.where(
            or_(
                Note.title.like(like, escape="\\"), Note.content.like(like, escape="\\")
            )
        )

    total = (
        await db.execute(select(func.count()).select_from(stmt.subquery()))
    ).scalar_one()

    stmt = stmt.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
    notes = (
        (await db.execute(stmt.offset((page - 1) * page_size).limit(page_size)))
        .scalars()
        .all()
    )
    return {
        "items": [NoteSummary.model_validate(n).model_dump(mode="json") for n in notes],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def _note_hit(note: Note, score: float) -> dict:
    return {
        "note": NoteSummary.model_validate(note).model_dump(mode="json"),
        "score": score,
    }


async def _like_search(
    db: AsyncSession, user_id: str, keyword: str, top_k: int
) -> list[dict]:
    """LIKE 字面匹配：标题 1.0 优先，正文 0.5 补齐。"""
    pattern = f"%{_escape_like(keyword)}%"
    base = [Note.user_id == user_id, Note.deleted_at.is_(None)]

    title_notes = list(
        (
            await db.execute(
                select(Note)
                .where(*base, Note.title.like(pattern, escape="\\"))
                .order_by(Note.updated_at.desc())
                .limit(top_k)
            )
        )
        .scalars()
        .all()
    )
    results = [_note_hit(note, 1.0) for note in title_notes]
    remaining = top_k - len(title_notes)
    if remaining <= 0:
        return results

    conds = [*base, Note.content.like(pattern, escape="\\")]
    if title_notes:
        conds.append(Note.id.not_in([note.id for note in title_notes]))
    content_notes = list(
        (
            await db.execute(
                select(Note)
                .where(*conds)
                .order_by(Note.updated_at.desc())
                .limit(remaining)
            )
        )
        .scalars()
        .all()
    )
    results.extend(_note_hit(note, 0.5) for note in content_notes)
    return results


async def keyword_search(
    db: AsyncSession, user_id: str, query: str, top_k: int = 20
) -> dict:
    """关键词搜索：MySQL FULLTEXT ngram 优先，否则标题加权 LIKE。

    ngram 最小 token 为 2 字，单字符直接走 LIKE。测试环境是 SQLite，
    MATCH AGAINST 会失败并回退 LIKE，所以 pytest 不依赖 MySQL 索引。
    score 只用于排序权重，不是语义相似度。
    """
    keyword = (query or "").strip()
    if not keyword:
        return {"query": query, "results": []}

    if len(keyword) >= 2:
        try:
            match_where = text(
                "MATCH (notes.title, notes.content) AGAINST (:kw IN NATURAL LANGUAGE MODE)"
            )
            match_order = text(
                "MATCH (notes.title, notes.content) AGAINST (:kw IN NATURAL LANGUAGE MODE) DESC"
            )
            notes = list(
                (
                    await db.execute(
                        select(Note)
                        .where(
                            and_(
                                Note.user_id == user_id,
                                Note.deleted_at.is_(None),
                                match_where,
                            )
                        )
                        .order_by(match_order, Note.updated_at.desc())
                        .limit(top_k),
                        {"kw": keyword},
                    )
                )
                .scalars()
                .all()
            )
            if notes:
                return {
                    "query": keyword,
                    "results": [_note_hit(note, 0.9) for note in notes],
                }
        except Exception as exc:
            logger.warning(
                "FULLTEXT 查询失败，回退 LIKE: %s: %s", type(exc).__name__, exc
            )

    return {
        "query": keyword,
        "results": await _like_search(db, user_id, keyword, top_k),
    }


async def update_note(
    db: AsyncSession, user_id: str, note_id: str, fields: dict
) -> Note:
    """按传入字段部分更新；category_id 显式传 null 表示移出分类。format 创建后不可改。"""
    note = await get_active_note(db, user_id, note_id)
    fields.pop("format", None)

    if "category_id" in fields and fields["category_id"] is not None:
        await ensure_category(db, user_id, fields["category_id"])

    for key, value in fields.items():
        setattr(note, key, value)
    await db.flush()
    # onupdate 列（updated_at）在 flush 后被标记过期，异步下必须显式刷新，
    # 否则 Pydantic 同步读取属性会触发隐式懒加载而报 MissingGreenlet
    await db.refresh(note)
    await _try_index(note)
    return note


async def soft_delete_note(db: AsyncSession, user_id: str, note_id: str) -> None:
    """移入回收站（软删除）。"""
    note = await get_active_note(db, user_id, note_id)
    note.deleted_at = datetime.now()
    await db.flush()
    drop_note_vectors(note.id)


async def list_recycle_bin(db: AsyncSession, user_id: str) -> list[dict]:
    notes = (
        (
            await db.execute(
                select(Note)
                .where(Note.user_id == user_id, Note.deleted_at.isnot(None))
                .order_by(Note.deleted_at.desc())
            )
        )
        .scalars()
        .all()
    )
    days = get_settings().recycle_bin_cleanup_days
    now = datetime.now()
    items = []
    for note in notes:
        payload = NoteSummary.model_validate(note).model_dump(mode="json")
        elapsed = (now - note.deleted_at).days if note.deleted_at else 0
        payload["days_remaining"] = max(0, days - elapsed)
        items.append(payload)
    return items


async def move_note(
    db: AsyncSession, user_id: str, note_id: str, category_id: str | None
) -> Note:
    """把活跃笔记移到目标分类；category_id 为空表示未分类。"""
    return await update_note(db, user_id, note_id, {"category_id": category_id})


async def batch_notes(db: AsyncSession, user_id: str, data: NoteBatchRequest) -> dict:
    """逐条执行批量操作；单条失败不打断其余条目。"""
    success_ids: list[str] = []
    errors: list[dict] = []
    for note_id in data.note_ids:
        try:
            if data.operation == "delete":
                await soft_delete_note(db, user_id, note_id)
            elif data.operation == "pin":
                await update_note(db, user_id, note_id, {"is_pinned": True})
            elif data.operation == "unpin":
                await update_note(db, user_id, note_id, {"is_pinned": False})
            elif data.operation == "move":
                await move_note(db, user_id, note_id, data.target_category_id)
            elif data.operation == "permanent_delete":
                await permanent_delete_note(db, user_id, note_id)
            else:
                await restore_note(db, user_id, note_id)
            success_ids.append(note_id)
        except BusinessError as exc:
            errors.append({"note_id": note_id, "error": exc.message})
    return {
        "operation": data.operation,
        "total": len(data.note_ids),
        "success_count": len(success_ids),
        "error_count": len(errors),
        "errors": errors or None,
    }


async def cleanup_expired_notes(db: AsyncSession, days: int | None = None) -> int:
    """物理删除回收站中超过阈值的笔记，并清向量。"""
    cutoff = datetime.now() - timedelta(
        days=days or get_settings().recycle_bin_cleanup_days
    )
    expired = list(
        (
            await db.execute(
                select(Note).where(
                    Note.deleted_at.isnot(None),
                    Note.deleted_at <= cutoff,
                )
            )
        )
        .scalars()
        .all()
    )
    for note in expired:
        drop_note_vectors(note.id)
        await db.delete(note)
    await db.flush()
    return len(expired)


async def restore_note(db: AsyncSession, user_id: str, note_id: str) -> None:
    """从回收站恢复笔记；不在回收站的笔记视为不存在。"""
    note = (
        await db.execute(
            select(Note).where(
                Note.id == note_id,
                Note.user_id == user_id,
                Note.deleted_at.isnot(None),
            )
        )
    ).scalar_one_or_none()
    if note is None:
        raise _not_found()
    note.deleted_at = None
    await db.flush()
    await _try_index(note)


async def permanent_delete_note(db: AsyncSession, user_id: str, note_id: str) -> None:
    """物理删除笔记（不可恢复）。"""
    note = (
        await db.execute(
            select(Note).where(Note.id == note_id, Note.user_id == user_id)
        )
    ).scalar_one_or_none()
    if note is None:
        raise _not_found()
    drop_note_vectors(note.id)
    await db.delete(note)
    await db.flush()
