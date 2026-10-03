"""Tracked tasks with keyed serialization and bounded application shutdown."""

import asyncio
import logging

logger = logging.getLogger(__name__)
_tasks: set[asyncio.Task] = set()
_by_key: dict[str, asyncio.Task] = {}


def spawn_background_task(factory, *, key: str = "") -> asyncio.Task:
    """派发后台异步任务。

    1. 防丢失：全局集合强引用，防止被 Python 垃圾回收机制中断。
    2. 按 Key 排队：相同 key 的任务自动串行化执行（后一个等前一个），防止并发乱序。
    3. 自清理：任务执行完毕后自动从任务池中注销释放内存。
    """
    previous = _by_key.get(key) if key else None

    async def run():
        if previous is not None:
            try:
                await asyncio.shield(previous)
            except Exception:
                pass
        try:
            await factory()
        except Exception:
            logger.warning("后台任务失败: %s", key, exc_info=True)

    task = asyncio.create_task(run())
    _tasks.add(task)
    if key:
        _by_key[key] = task

    def finished(done):
        _tasks.discard(done)
        if key and _by_key.get(key) is done:
            _by_key.pop(key, None)

    task.add_done_callback(finished)
    return task


async def drain_background_tasks(timeout: float = 5.0) -> None:
    if not _tasks:
        return
    _, pending = await asyncio.wait(list(_tasks), timeout=timeout)
    for task in pending:
        task.cancel()
    await asyncio.gather(*pending, return_exceptions=True)
