"""聊天会话与 RAG 问答 Schema。"""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatAskRequest(BaseModel):
    session_id: str | None = Field(default=None, description="为空则创建新会话")
    message: str = Field(min_length=1, max_length=20000)
    top_k: int = Field(default=5, ge=1, le=10)


class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatMessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatAskResponse(BaseModel):
    session_id: str
    answer: str
    sources: list[dict]
    used_retrieval: bool = True
    used_agent: bool = False
    tool_calls: list[dict] = Field(default_factory=list)
    route_distance: float | None = None
    title: str | None = None
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse


class ChatSessionTitleUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
