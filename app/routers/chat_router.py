"""聊天路由。

- POST /chat/query  ReAct SSE：thinking / response / tool_* / done / error
- 会话列表、改标题、删除、消息历史
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.success_response import success_response
from app.db.database import get_db_session
from app.schemas.chat import ChatSessionTitleUpdate, QueryRequest
from app.services import chat_service, query_service
from app.utils.auth_utils import get_chat_user_id, get_current_user_id

router = APIRouter()


@router.post("/chat/query", summary="ReAct 流式对话")
async def chat_query(
    request: Request,
    data: QueryRequest,
    user_id: str = Depends(get_chat_user_id),
):
    settings = request.app.state.settings
    return StreamingResponse(
        query_service.stream_query(
            request.app.state.db_session_factory, user_id, data, settings
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/sessions", summary="会话列表")
async def list_sessions(
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    return success_response(
        data=await chat_service.list_sessions(db, user_id, request.app.state.settings)
    )


@router.put("/chat/sessions/{session_id}/title", summary="修改会话标题")
async def update_title(
    request: Request,
    session_id: str,
    data: ChatSessionTitleUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    session = await chat_service.update_session_title(
        db, user_id, session_id, data.title, request.app.state.settings
    )
    return success_response(data={"id": session.id, "title": session.title})


@router.delete("/chat/sessions/{session_id}", summary="删除会话")
async def delete_session(
    request: Request,
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    await chat_service.delete_session(
        db, user_id, session_id, request.app.state.settings
    )
    return success_response(message="会话已删除")


@router.get("/chat/sessions/{session_id}/messages", summary="消息历史")
async def list_messages(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    return success_response(
        data=await chat_service.list_messages(db, user_id, session_id)
    )
