"""笔记相关 Pydantic Schema。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class NoteCreate(BaseModel):
    """创建笔记请求。"""

    title: str = Field(min_length=1, max_length=500, description="标题")
    content: str = Field(description="内容（Markdown 或纯文本）")
    category_id: str | None = Field(default=None, max_length=36, description="分类 ID")
    tags: list[str] | None = Field(default=None, description="标签数组")
    format: str = Field(default="md", pattern="^(md|txt)$", description="文档类型，创建后不可改")


class NoteUpdate(BaseModel):
    """更新笔记请求（部分字段可选，只更新传入的字段）。"""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    content: str | None = None
    category_id: str | None = Field(default=None, max_length=36, description="移动分类；传 null 移出分类")
    tags: list[str] | None = None
    is_pinned: bool | None = None


class NoteResponse(BaseModel):
    """笔记信息响应。"""

    id: str
    title: str
    content: str
    format: str
    tags: list[str] | None = None
    category_id: str | None = None
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NoteSummary(BaseModel):
    """笔记列表项（不含正文，列表接口瘦身）。"""

    id: str
    title: str
    format: str
    tags: list[str] | None = None
    category_id: str | None = None
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    days_remaining: int | None = None

    model_config = {"from_attributes": True}


class NoteMoveRequest(BaseModel):
    """把单篇笔记移到目标分类；category_id 为空表示未分类。"""

    category_id: str | None = Field(default=None, max_length=36)


class NoteBatchRequest(BaseModel):
    note_ids: list[str] = Field(min_length=1)
    operation: Literal["delete", "pin", "unpin", "move", "permanent_delete", "restore"]
    target_category_id: str | None = Field(default=None, max_length=36)

    @model_validator(mode="after")
    def validate_batch(self):
        if self.operation == "move":
            # 允许 null：批量移出分类
            pass
        if self.operation == "permanent_delete" and len(self.note_ids) > 50:
            raise ValueError("单次批量彻底删除最多 50 条")
        if self.operation == "restore" and len(self.note_ids) > 100:
            raise ValueError("单次批量恢复最多 100 条")
        return self


class NoteSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200, description="搜索关键词")
    top_k: int = Field(default=20, ge=1, le=50, description="返回条数")


class NoteSearchHit(BaseModel):
    note: NoteSummary
    score: float


class AutocompleteRequest(BaseModel):
    content: str = Field(default="", description="当前笔记内容")
    cursor_position: int = Field(default=0, ge=0)


class WriteAssistantRequest(BaseModel):
    content: str = Field(default="", description="笔记内容")
    mode: str = Field(default="continue", pattern="^(continue|expand|summary)$")


class AutoTagRequest(BaseModel):
    title: str = Field(default="", max_length=500)
    content: str = Field(default="")
