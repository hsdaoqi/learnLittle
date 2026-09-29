"""聊天路由。

- POST /chat/ask  同步问答（兼容；内部仍检索+拼/改写完整答案）
- POST /chat/stream  SSE：meta / token / done
- 会话列表、改标题、删除、消息历史
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.success_response import success_response
from app.db.database import get_db_session
from app.schemas.chat import ChatAskRequest, ChatSessionTitleUpdate
from app.services import chat_service
from app.utils.auth_utils import get_current_user_id

router = APIRouter()


@router.post("/chat/ask", summary="知识库问答（同步）")
async def ask(
    request: Request,
    data: ChatAskRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    return success_response(
        data=await chat_service.ask(
            db,
            user_id,
            data,
            request.app.state.settings,
            session_factory=request.app.state.db_session_factory,
        )
    )


@router.post("/chat/stream", summary="知识库问答（SSE）")
async def stream_ask(
    request: Request,
    data: ChatAskRequest,
    user_id: str = Depends(get_current_user_id),
):
    settings = request.app.state.settings
    return StreamingResponse(
        chat_service.stream_ask(
            request.app.state.db_session_factory, user_id, data, settings
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
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
