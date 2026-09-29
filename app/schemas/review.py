"""艾宾浩斯回顾 Schema。"""

from datetime import datetime

from pydantic import BaseModel, Field


class ReviewItem(BaseModel):
    review_id: int
    note_id: str
    note_title: str
    note_content: str
    review_count: int
    interval_days: int
    next_review_at: datetime


class ReviewCompleteResponse(BaseModel):
    review_id: int
    next_review_at: datetime
    interval_days: int
    review_count: int


class ReviewStats(BaseModel):
    pending_today: int
    total_reviews: int
    completed_today: int
    streak_days: int


class ReviewCompleteQuery(BaseModel):
    quality: int = Field(default=3, ge=0, le=5)
