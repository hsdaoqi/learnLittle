"""知识库路由。

- POST   /knowledge/upload              上传：SSE 推送解析 / 切片 / 写向量进度
- GET    /knowledge/documents           文档列表
- GET    /knowledge/search              按当前用户检索切片
- GET    /knowledge/documents/{doc_id}  文档详情
- DELETE /knowledge/documents/{doc_id}  删除文档（元数据 + 本地文件 + 向量）
"""

import logging

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.failed_response import BusinessError, ErrorCode
from app.core.success_response import success_response
from app.db.database import get_db_session
from app.schemas.knowledge import KnowledgeDocumentResponse, KnowledgeSearchResponse
from app.services import knowledge_service
from app.utils.auth_utils import get_current_user_id
from app.utils.file_handler import (
    calculate_md5_bytes,
    read_upload_limited,
    validate_upload_file,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/knowledge/upload", summary="上传知识库文档（SSE 进度）")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    settings = request.app.state.settings
    if not file.filename:
        raise BusinessError(code=ErrorCode.UNSUPPORTED_FILE_TYPE, detail="缺少文件名")

    content = await read_upload_limited(file, settings.max_upload_size_mb)
    validate_upload_file(file.filename, len(content), settings.max_upload_size_mb)
    md5 = calculate_md5_bytes(content)
    if await knowledge_service.find_duplicate(db, user_id, md5):
        raise BusinessError(code=ErrorCode.DOCUMENT_ALREADY_EXISTS, http_status=409)

    filename = file.filename
    declared_type = file.content_type
    session_factory = request.app.state.db_session_factory

    async def event_generator():
        async with session_factory() as session:
            try:
                async for event in knowledge_service.iter_save_document(
                    session,
                    user_id=user_id,
                    original_filename=filename,
                    content=content,
                    declared_type=declared_type,
                    settings=settings,
                    md5=md5,
                ):
                    yield event
                await session.commit()
                yield knowledge_service.sse_event({"event_type": "finish"})
            except Exception:
                await session.rollback()
                logger.exception("知识库文档处理失败")
                yield knowledge_service.sse_event(
                    {
                        "event_type": "error",
                        "message": "文档处理失败，请稍后重试",
                    }
                )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/knowledge/documents", summary="文档列表")
async def list_documents(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    return success_response(data=await knowledge_service.list_documents(db, user_id))


@router.get("/knowledge/search", summary="检索知识库")
async def search_documents(
    q: str = Query(..., min_length=1, max_length=200, description="检索词"),
    top_k: int = Query(default=5, ge=1, le=20),
    user_id: str = Depends(get_current_user_id),
):
    items = await knowledge_service.search_documents(user_id, q, top_k)
    return success_response(
        data=KnowledgeSearchResponse(items=items, total=len(items)).model_dump()
    )


@router.get("/knowledge/documents/{doc_id}", summary="文档详情")
async def get_document(
    doc_id: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    doc = await knowledge_service.get_document(db, user_id, doc_id)
    return success_response(
        data=KnowledgeDocumentResponse.model_validate(doc).model_dump(mode="json")
    )


@router.delete("/knowledge/documents/{doc_id}", summary="删除文档")
async def delete_document(
    doc_id: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    await knowledge_service.delete_document(db, user_id, doc_id)
    return success_response(message="文档已删除")
