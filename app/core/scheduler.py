"""后台定时任务。

uvicorn --reload 会拉起父子两个进程。调度器只在非 reload 的主进程启动，
避免同一清理任务一天跑两次。
"""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _run_cleanup(job_name: str, cleanup_fn, days: int) -> int:
    from app.db.database import create_database_engine, create_session_factory

    settings = get_settings()
    engine = create_database_engine(settings)
    factory = create_session_factory(engine)
    try:
        async with factory() as db:
            try:
                count = await cleanup_fn(db, days=days)
                await db.commit()
                logger.info("定时%s完成: 删除 %s 个", job_name, count)
                return count
            except Exception:
                await db.rollback()
                logger.exception("定时%s失败", job_name)
                raise
    finally:
        await engine.dispose()


async def cleanup_expired_notes() -> int:
    from app.services.note_service import cleanup_expired_notes as cleanup

    return await _run_cleanup("清理过期笔记", cleanup, get_settings().recycle_bin_cleanup_days)


async def cleanup_expired_categories() -> int:
    from app.services.category_service import cleanup_expired_categories as cleanup

    return await _run_cleanup("清理过期分类", cleanup, get_settings().recycle_bin_cleanup_days)


def init_scheduler() -> None:
    if scheduler.running:
        return
    days = get_settings().recycle_bin_cleanup_days
    scheduler.add_job(
        cleanup_expired_notes,
        trigger=CronTrigger(hour=3, minute=0),
        id="cleanup_expired_notes",
        name="清理过期笔记",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.add_job(
        cleanup_expired_categories,
        trigger=CronTrigger(hour=3, minute=30),
        id="cleanup_expired_categories",
        name="清理过期分类",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info("定时任务已启动（03:00 笔记 / 03:30 分类，超过 %s 天的回收站）", days)


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("定时任务调度器已关闭")
