"""笔记模型，对应 MySQL 表 notes。

支持软删除（14 天回收站惯例）、置顶、标签、分类：
- deleted_at 非 NULL 表示已在回收站
- tags 用 JSON 列存标签数组
- category_id 指向分类；分类被物理删除时 SET NULL → 笔记变"未分类"
- 后续 RAG 阶段会在此模型基础上双写向量库（本阶段只做 MySQL）
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[str] = mapped_column(String(10), nullable=False, server_default="md")
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)
    category_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("note_categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Note(id={self.id}, title={self.title[:20]})>"
