"""回顾相关 Agent 工具。

本阶段不接 LangChain / Plan-Execute。这两个函数给后面的 Agent
直接当 tool 用：入参是独立 db session + user_id，返回纯文本。
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import review_service


async def get_today_reviews_tool(db: AsyncSession, user_id: str) -> str:
    return await review_service.format_today_reviews_text(db, user_id)


async def mark_reviewed_tool(
    db: AsyncSession, user_id: str, review_id: int, quality: int = 3
) -> str:
    return await review_service.complete_review_text(db, user_id, review_id, quality)


REVIEW_TOOL_SPECS = (
    {
        "name": "get_today_reviews_tool",
        "description": "获取今日待回顾的笔记列表",
        "fn": get_today_reviews_tool,
    },
    {
        "name": "mark_reviewed_tool",
        "description": "标记一条回顾记录为已完成",
        "fn": mark_reviewed_tool,
    },
)
