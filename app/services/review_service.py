"""艾宾浩斯间隔重复：今日待复习、完成打卡、统计。

间隔：1 / 2 / 4 / 7 / 15 / 30 天。打卡后取下一档，已经 30 天就停在 30。
quality 只落库，本阶段不参与间隔计算（留给 SM-2）。

创建笔记时 ensure_review_record：立刻可复习（next_review_at = now）。
已删笔记不进今日列表。跨用户一律 404。

format_today_reviews_text / complete_review_text 给后面 Agent 工具直接复用。
"""

from datetime import datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.failed_response import BusinessError, ErrorCode
from app.models.note import Note
from app.models.review import ReviewRecord

EBBINGHAUS_INTERVALS = [1, 2, 4, 7, 15, 30]


def next_interval(current_days: int) -> int:
    """当前间隔在表里则进一档；不在表里则回到 1 天。"""
    if current_days in EBBINGHAUS_INTERVALS:
        index = EBBINGHAUS_INTERVALS.index(current_days)
        return EBBINGHAUS_INTERVALS[min(index + 1, len(EBBINGHAUS_INTERVALS) - 1)]
    return EBBINGHAUS_INTERVALS[0]


def _not_found() -> BusinessError:
    return BusinessError(code=ErrorCode.REVIEW_NOT_FOUND, http_status=404)


def _dump(review: ReviewRecord, note: Note) -> dict:
    return {
        "review_id": review.id,
        "note_id": review.note_id,
        "note_title": note.title,
        "note_content": note.content,
        "review_count": review.review_count,
        "interval_days": review.interval_days,
        "next_review_at": review.next_review_at,
    }


async def ensure_review_record(
    db: AsyncSession, user_id: str, note_id: str
) -> ReviewRecord:
    """给新笔记建回顾记录；已有则原样返回。"""
    existing = (
        await db.execute(
            select(ReviewRecord).where(
                ReviewRecord.note_id == note_id,
                ReviewRecord.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    review = ReviewRecord(
        note_id=note_id,
        user_id=user_id,
        review_count=0,
        interval_days=1,
        next_review_at=datetime.now(),
    )
    db.add(review)
    await db.flush()
    await db.refresh(review)
    return review


async def get_today_reviews(db: AsyncSession, user_id: str) -> list[dict]:
    now = datetime.now()
    rows = (
        await db.execute(
            select(ReviewRecord, Note)
            .join(Note, ReviewRecord.note_id == Note.id)
            .where(
                and_(
                    ReviewRecord.user_id == user_id,
                    ReviewRecord.next_review_at <= now,
                    Note.deleted_at.is_(None),
                )
            )
            .order_by(ReviewRecord.next_review_at.asc(), ReviewRecord.id.asc())
        )
    ).all()
    return [_dump(review, note) for review, note in rows]


async def mark_reviewed(
    db: AsyncSession, user_id: str, review_id: int, quality: int = 3
) -> ReviewRecord:
    review = (
        await db.execute(
            select(ReviewRecord).where(
                ReviewRecord.id == review_id,
                ReviewRecord.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if review is None:
        raise _not_found()

    now = datetime.now()
    review.review_count += 1
    review.quality = quality
    review.reviewed_at = now
    review.interval_days = next_interval(review.interval_days)
    review.next_review_at = now + timedelta(days=review.interval_days)
    await db.flush()
    await db.refresh(review)
    return review


async def get_review_stats(db: AsyncSession, user_id: str) -> dict:
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    pending_today = (
        await db.execute(
            select(func.count())
            .select_from(ReviewRecord)
            .join(Note, ReviewRecord.note_id == Note.id)
            .where(
                ReviewRecord.user_id == user_id,
                ReviewRecord.next_review_at <= now,
                Note.deleted_at.is_(None),
            )
        )
    ).scalar_one()

    total_reviews = (
        await db.execute(
            select(func.coalesce(func.sum(ReviewRecord.review_count), 0)).where(
                ReviewRecord.user_id == user_id
            )
        )
    ).scalar_one()

    completed_today = (
        await db.execute(
            select(func.count())
            .select_from(ReviewRecord)
            .where(
                ReviewRecord.user_id == user_id,
                ReviewRecord.reviewed_at >= today_start,
            )
        )
    ).scalar_one()

    streak_days = 0
    check_date = today_start
    while True:
        day_end = check_date + timedelta(days=1)
        count = (
            await db.execute(
                select(func.count())
                .select_from(ReviewRecord)
                .where(
                    ReviewRecord.user_id == user_id,
                    ReviewRecord.reviewed_at >= check_date,
                    ReviewRecord.reviewed_at < day_end,
                )
            )
        ).scalar_one()
        if count > 0:
            streak_days += 1
            check_date -= timedelta(days=1)
        else:
            break

    return {
        "pending_today": int(pending_today or 0),
        "total_reviews": int(total_reviews or 0),
        "completed_today": int(completed_today or 0),
        "streak_days": streak_days,
    }


async def format_today_reviews_text(db: AsyncSession, user_id: str) -> str:
    """Agent 工具：今日待复习的纯文本。"""
    reviews = await get_today_reviews(db, user_id)
    if not reviews:
        return "今日没有待回顾的笔记"
    lines = [
        f"- [{item['note_title']}] (第{item['review_count'] + 1}次回顾)"
        for item in reviews
    ]
    return f"今日待回顾 ({len(reviews)} 篇):\n" + "\n".join(lines)


async def complete_review_text(
    db: AsyncSession, user_id: str, review_id: int, quality: int = 3
) -> str:
    """Agent 工具：打卡后返回下次日期。"""
    review = await mark_reviewed(db, user_id, review_id, quality)
    return f"回顾完成！下次回顾时间: {review.next_review_at.strftime('%Y-%m-%d')}"
