"""知识库文档服务：落盘、解析切片、向量入库、检索。

同一用户同一 MD5 视为重复上传。
向量写入失败时抛错，由请求会话回滚 DB，并清理已落盘文件。
上传走 SSE：processing / completed，结束标记由路由补 finish。
"""

import json
import logging
import uuid
from collections.abc import AsyncIterator
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.core.failed_response import BusinessError, ErrorCode
from app.models.knowledge import KnowledgeDocument
from app.rag.document_parser import parse_document
from app.rag.text_splitter import TextSplitter
from app.rag.vector_store import get_vector_store
from app.schemas.knowledge import (
    KnowledgeDocumentListResponse,
    KnowledgeDocumentResponse,
)
from app.utils.file_handler import (
    calculate_md5_bytes,
    ensure_dir,
    get_safe_filename,
    infer_mime,
    validate_upload_file,
)

logger = logging.getLogger(__name__)


def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def _processing(filename: str, progress: int, stage: str, message: str) -> str:
    return sse_event(
        {
            "event_type": "processing",
            "filename": filename,
            "progress": progress,
            "stage": stage,
            "message": message,
        }
    )


def _doc_type(filename: str) -> str:
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext == "markdown":
        return "md"
    return ext or "txt"


async def find_duplicate(
    db: AsyncSession, user_id: str, md5: str
) -> KnowledgeDocument | None:
    return (
        await db.execute(
            select(KnowledgeDocument).where(
                KnowledgeDocument.user_id == user_id,
                KnowledgeDocument.md5_hash == md5,
            )
        )
    ).scalar_one_or_none()


async def _index_chunks(doc: KnowledgeDocument, chunks) -> None:
    if not chunks:
        return
    store = get_vector_store()
    ids = [f"{doc.id}_{chunk.chunk_index}" for chunk in chunks]
    metadatas = [
        {
            "user_id": doc.user_id,
            "document_id": str(doc.id),
            "filename": doc.filename,
            "section_title": chunk.section_title,
            "chunk_index": chunk.chunk_index,
        }
        for chunk in chunks
    ]
    await store.upsert_chunks(
        documents=[chunk.content for chunk in chunks],
        metadatas=metadatas,
        ids=ids,
    )


async def save_document(
    db: AsyncSession,
    *,
    user_id: str,
    original_filename: str,
    content: bytes,
    declared_type: str | None,
    settings: Settings,
    md5: str | None = None,
) -> KnowledgeDocument:
    async for event in iter_save_document(
        db,
        user_id=user_id,
        original_filename=original_filename,
        content=content,
        declared_type=declared_type,
        settings=settings,
        md5=md5,
    ):
        payload = json.loads(event.split("data:", 1)[1].strip())
        if payload.get("event_type") == "completed":
            doc_id = payload["document_id"]
            return await get_document(db, user_id, doc_id)
    raise RuntimeError("文档处理未完成")


async def iter_save_document(
    db: AsyncSession,
    *,
    user_id: str,
    original_filename: str,
    content: bytes,
    declared_type: str | None,
    settings: Settings,
    md5: str | None = None,
) -> AsyncIterator[str]:
    """落盘 → 解析 → 切片 → 写向量，每步推一条 processing，最后 completed。"""
    file_size = len(content)
    validate_upload_file(original_filename, file_size, settings.max_upload_size_mb)
    digest = md5 or calculate_md5_bytes(content)
    existing = await find_duplicate(db, user_id, digest)
    if existing is not None:
        raise BusinessError(code=ErrorCode.DOCUMENT_ALREADY_EXISTS, http_status=409)

    safe_name = get_safe_filename(original_filename)
    stored_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    dest_dir = Path(settings.upload_dir) / user_id
    file_path = dest_dir / stored_name

    yield _processing(safe_name, 0, "saving", "正在保存文件...")
    ensure_dir(str(dest_dir))
    file_path.write_bytes(content)
    yield _processing(safe_name, 20, "saved", "文件保存完成")

    try:
        yield _processing(safe_name, 30, "parsing", "正在解析文档内容...")
        text = parse_document(content, original_filename)
        yield _processing(safe_name, 50, "parsed", "文档解析完成")

        yield _processing(safe_name, 60, "splitting", "正在文本切片...")
        splitter = TextSplitter(settings.chunk_size, settings.chunk_overlap)
        chunks = splitter.split(text, _doc_type(original_filename))
        yield _processing(
            safe_name, 75, "splitted", f"文本切片完成，共 {len(chunks)} 个片段"
        )

        yield _processing(safe_name, 85, "vectorizing", "正在向量化...")
        doc = KnowledgeDocument(
            user_id=user_id,
            filename=safe_name,
            file_path=str(file_path),
            file_size=file_size,
            file_type=infer_mime(safe_name, declared_type),
            md5_hash=digest,
            chunk_count=len(chunks),
        )
        db.add(doc)
        await db.flush()
        await db.refresh(doc)
        await _index_chunks(doc, chunks)
    except Exception:
        try:
            file_path.unlink(missing_ok=True)
        except OSError as exc:
            logger.warning("文档处理失败后清理文件失败: %s", exc)
        raise

    yield _processing(safe_name, 100, "vectorized", "向量化入库完成")
    yield sse_event(
        {
            "event_type": "completed",
            "filename": safe_name,
            "progress": 100,
            "document_id": doc.id,
            "document": KnowledgeDocumentResponse.model_validate(doc).model_dump(
                mode="json"
            ),
            "message": "文档处理完成",
        }
    )


async def list_documents(db: AsyncSession, user_id: str) -> dict:
    rows = (
        (
            await db.execute(
                select(KnowledgeDocument)
                .where(KnowledgeDocument.user_id == user_id)
                .order_by(KnowledgeDocument.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    docs = list(rows)
    return KnowledgeDocumentListResponse(
        documents=[KnowledgeDocumentResponse.model_validate(d) for d in docs],
        total=len(docs),
    ).model_dump(mode="json")


async def get_document(
    db: AsyncSession, user_id: str, doc_id: int
) -> KnowledgeDocument:
    doc = (
        await db.execute(
            select(KnowledgeDocument).where(
                KnowledgeDocument.id == doc_id,
                KnowledgeDocument.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if doc is None:
        raise BusinessError(code=ErrorCode.DOCUMENT_NOT_FOUND, http_status=404)
    return doc


async def delete_document(db: AsyncSession, user_id: str, doc_id: int) -> None:
    doc = await get_document(db, user_id, doc_id)
    try:
        Path(doc.file_path).unlink(missing_ok=True)
    except OSError as exc:
        logger.warning("删除知识库文件失败: %s", exc)
    try:
        get_vector_store().delete_document(doc.id)
    except Exception as exc:
        logger.warning("删除知识库向量失败: %s", exc)
    await db.delete(doc)
    await db.flush()


async def search_documents(user_id: str, query: str, top_k: int = 5) -> list[dict]:
    keyword = query.strip()
    if not keyword:
        raise BusinessError(code=ErrorCode.INVALID_PARAMETER, detail="检索词不能为空")
    return await get_vector_store().search(keyword, user_id, top_k, collection="rag")
