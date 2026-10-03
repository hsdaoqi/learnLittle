"""聊天会话与 RAG 问答 Schema。"""

from datetime import datetime

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=128)
    session_id: str | None = Field(default=None, description="为空则创建新会话")
    message: str = Field(min_length=1, max_length=20000)
    top_k: int = Field(default=5, ge=1, le=10)
    enable_thinking: bool = Field(
        default=False,
        description="深度思考；只作用于主问答模型。分类器 / 计划由环境变量独立控制",
    )
    attachment_ids: list[str] = Field(
        default_factory=list,
        max_length=8,
        description="附件 ID。本阶段不解析多模态，非空时自动关闭主模型深度思考",
    )


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


class ChatSessionTitleUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
