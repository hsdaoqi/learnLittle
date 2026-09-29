"""间隔重复回顾路由。

- GET  /review/today
- POST /review/{review_id}/complete?quality=3
- GET  /review/stats
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.success_response import success_response
from app.db.database import get_db_session
from app.schemas.review import ReviewCompleteResponse, ReviewItem, ReviewStats
from app.services import review_service
from app.utils.auth_utils import get_current_user_id

router = APIRouter()


@router.get("/review/today", summary="今日待回顾")
async def get_today_reviews(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    reviews = await review_service.get_today_reviews(db, user_id)
    items = [
        ReviewItem.model_validate(item).model_dump(mode="json") for item in reviews
    ]
    return success_response(data={"reviews": items, "count": len(items)})


@router.post("/review/{review_id}/complete", summary="标记回顾完成")
async def mark_reviewed(
    review_id: int,
    quality: int = Query(default=3, ge=0, le=5),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    review = await review_service.mark_reviewed(db, user_id, review_id, quality)
    return success_response(
        data=ReviewCompleteResponse(
            review_id=review.id,
            next_review_at=review.next_review_at,
            interval_days=review.interval_days,
            review_count=review.review_count,
        ).model_dump(mode="json")
    )


@router.get("/review/stats", summary="回顾统计")
async def get_review_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    stats = await review_service.get_review_stats(db, user_id)
    return success_response(data=ReviewStats.model_validate(stats).model_dump())
