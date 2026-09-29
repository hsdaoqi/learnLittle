"""笔记模板 Schema。"""

from datetime import datetime

from pydantic import BaseModel, Field


class NoteTemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    content_structure: dict | None = None
    category: str | None = Field(default=None, max_length=100)
    sort_order: int = Field(default=0, ge=0)


class NoteTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    content_structure: dict | None = None
    category: str | None = Field(default=None, max_length=100)
    sort_order: int | None = Field(default=None, ge=0)


class NoteTemplateApply(BaseModel):
    """用模板新建一篇笔记。"""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    category_id: str | None = Field(default=None, max_length=36)
    format: str = Field(default="md", pattern="^(md|txt)$")


class NoteTemplateResponse(BaseModel):
    id: int
    name: str
    content_structure: dict | None = None
    category: str | None = None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
