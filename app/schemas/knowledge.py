"""知识库文档 Schema。"""

from datetime import datetime

from pydantic import BaseModel


class KnowledgeDocumentResponse(BaseModel):
    """文档元数据（不含本地路径，避免把存储细节暴露给前端）。"""

    id: int
    filename: str
    file_size: int
    file_type: str
    md5_hash: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeDocumentListResponse(BaseModel):
    documents: list[KnowledgeDocumentResponse]
    total: int


class KnowledgeSearchHit(BaseModel):
    content: str
    score: float
    document_id: int
    filename: str
    section_title: str = ""
    chunk_index: int = 0


class KnowledgeSearchResponse(BaseModel):
    items: list[KnowledgeSearchHit]
    total: int
