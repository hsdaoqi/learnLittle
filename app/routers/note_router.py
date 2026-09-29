"""笔记路由。

- POST   /note                     创建笔记（format=md|txt，创建后不可改）
- GET    /note                     笔记列表（分类/关键词/未分类过滤 + 分页）
- GET    /note/recycle-bin         回收站列表（含剩余天数）
- POST   /note/batch               批量 delete / pin / unpin / move / restore / permanent_delete
- POST   /note/search              关键词搜索（FULLTEXT ngram，失败回退标题加权 LIKE）
- POST   /note/autocomplete        AI 内联补全
- POST   /note/write-assistant     AI 写作辅助（continue / expand / summary）
- POST   /note/auto-tag            AI 自动打标签
- GET    /note/{note_id}           笔记详情
- PUT    /note/{note_id}           更新笔记（部分字段 / 置顶；不含 format）
- PUT    /note/{note_id}/category  移动分类（null = 未分类）
- DELETE /note/{note_id}           移入回收站（软删除）
- POST   /note/{note_id}/restore   从回收站恢复
- DELETE /note/{note_id}/permanent 彻底删除（不可恢复）

注意路由顺序：静态路径必须注册在 /note/{note_id} 之前。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.failed_response import BusinessError, ErrorCode
from app.core.rate_limit import check_named_limit
from app.core.success_response import success_response
from app.db.database import get_db_session
from app.models.user import User
from app.schemas.auth import NoteExportEmailRequest
from app.schemas.note import (
    AutocompleteRequest,
    AutoTagRequest,
    NoteBatchRequest,
    NoteCreate,
    NoteMoveRequest,
    NoteResponse,
    NoteSearchRequest,
    NoteUpdate,
    WriteAssistantRequest,
)
from app.services import email_service, note_ai_service, note_service, usage_service
from app.utils.auth_utils import get_current_user_id

router = APIRouter()


@router.post("/note", summary="创建笔记")
async def create_note(
    data: NoteCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    note = await note_service.create_note(db, user_id, data)
    return success_response(
        data={
            "id": note.id,
            "title": note.title,
            "format": note.format,
            "created_at": note.created_at,
        }
    )


@router.get("/note", summary="笔记列表")
async def list_notes(
    category_id: str | None = Query(default=None, description="按分类过滤"),
    uncategorized: bool = Query(default=False, description="只看未分类"),
    keyword: str | None = Query(
        default=None, max_length=100, description="标题/内容关键词"
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    result = await note_service.list_notes(
        db,
        user_id,
        category_id=category_id,
        uncategorized=uncategorized,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )
    return success_response(data=result)


@router.get("/note/recycle-bin", summary="回收站列表")
async def recycle_bin(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    return success_response(data=await note_service.list_recycle_bin(db, user_id))


@router.post("/note/batch", summary="批量操作笔记")
async def batch_operation(
    data: NoteBatchRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    result = await note_service.batch_notes(db, user_id, data)
    return success_response(
        data=result,
        message=f"批量操作完成：成功 {result['success_count']} 篇，失败 {result['error_count']} 篇",
    )


@router.post("/note/search", summary="关键词搜索笔记")
async def search_notes(
    data: NoteSearchRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    return success_response(
        data=await note_service.keyword_search(db, user_id, data.query, data.top_k)
    )


@router.post("/note/autocomplete", summary="AI 内联补全")
async def autocomplete(
    data: AutocompleteRequest,
    user_id: str = Depends(get_current_user_id),
):
    usage_service.set_trace_context(user_id=user_id, stage="note_ai")
    try:
        text = await note_ai_service.autocomplete(data.content, data.cursor_position)
    finally:
        usage_service.clear_trace_context()
    return success_response(data={"completion": text})


@router.post("/note/write-assistant", summary="AI 写作辅助")
async def write_assistant(
    data: WriteAssistantRequest,
    user_id: str = Depends(get_current_user_id),
):
    usage_service.set_trace_context(user_id=user_id, stage="note_ai")
    try:
        text = await note_ai_service.write_assist(data.content, data.mode)
    finally:
        usage_service.clear_trace_context()
    return success_response(data={"result": text})


@router.post("/note/auto-tag", summary="AI 自动打标签")
async def auto_tag(
    data: AutoTagRequest,
    user_id: str = Depends(get_current_user_id),
):
    usage_service.set_trace_context(user_id=user_id, stage="note_ai")
    try:
        tags = await note_ai_service.suggest_tags(data.title, data.content)
    finally:
        usage_service.clear_trace_context()
    return success_response(data={"tags": tags})


@router.get("/note/{note_id}", summary="笔记详情")
async def get_note(
    note_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    note = await note_service.get_active_note(db, user_id, note_id)
    return success_response(
        data=NoteResponse.model_validate(note).model_dump(mode="json")
    )


@router.put("/note/{note_id}", summary="更新笔记")
async def update_note(
    note_id: str,
    data: NoteUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    note = await note_service.update_note(
        db, user_id, note_id, data.model_dump(exclude_unset=True)
    )
    return success_response(
        data=NoteResponse.model_validate(note).model_dump(mode="json")
    )


@router.put("/note/{note_id}/category", summary="移动笔记到分类")
async def move_note_to_category(
    note_id: str,
    data: NoteMoveRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    note = await note_service.move_note(db, user_id, note_id, data.category_id)
    return success_response(
        data=NoteResponse.model_validate(note).model_dump(mode="json")
    )


@router.delete("/note/{note_id}", summary="删除笔记（移入回收站）")
async def delete_note(
    note_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    await note_service.soft_delete_note(db, user_id, note_id)
    return success_response(message="已移入回收站")


@router.post("/note/{note_id}/restore", summary="从回收站恢复")
async def restore_note(
    note_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    await note_service.restore_note(db, user_id, note_id)
    return success_response(message="已恢复")


@router.post("/note/{note_id}/export-email", summary="把笔记发到邮箱")
async def export_note_email(
    note_id: str,
    data: NoteExportEmailRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    note = await note_service.get_active_note(db, user_id, note_id)
    to = data.to
    if not to:
        user = (
            await db.execute(select(User).where(User.uuid == user_id))
        ).scalar_one_or_none()
        to = user.email if user else None
    if not to:
        raise BusinessError(
            code=ErrorCode.INVALID_PARAMETER, message="未绑定邮箱，请填写收件人"
        )
    attachment = email_service.note_attachment(note.title, note.content, data.format)
    body = f"笔记「{note.title}」见附件。"
    try:
        await email_service.send_email(
            to,
            f"笔记导出：{note.title}",
            body,
            attachments=[attachment],
        )
    except BusinessError:
        raise
    except Exception as exc:
        raise BusinessError(code=ErrorCode.EMAIL_SEND_FAILED, http_status=502) from exc
    return success_response(
        message="已发送", data={"to": to, "filename": attachment["filename"]}
    )


@router.delete("/note/{note_id}/permanent", summary="彻底删除笔记")
async def permanent_delete_note(
    note_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    if request.app.state.settings.rate_limit_enabled:
        await check_named_limit(user_id, "perm_delete", 30)
    await note_service.permanent_delete_note(db, user_id, note_id)
    return success_response(message="已彻底删除")
