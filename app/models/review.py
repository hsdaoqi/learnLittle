"""回顾记录，对应 MySQL 表 review_records。

一篇活跃笔记一条记录。间隔按艾宾浩斯：1 / 2 / 4 / 7 / 15 / 30 天。
quality 先存着，给以后 SM-2 升级用。
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ReviewRecord(Base):
    __tablename__ = "review_records"
    __table_args__ = (UniqueConstraint("note_id", name="uq_review_records_note_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    note_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    quality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    next_review_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ReviewRecord(id={self.id}, note_id={self.note_id})>"
