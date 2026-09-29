"""用量统计。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.success_response import success_response
from app.db.database import get_db_session
from app.services.usage_service import get_usage_summary
from app.utils.auth_utils import get_current_user_id

router = APIRouter()


@router.get("/usage/summary", summary="模型调用用量与费用汇总")
async def usage_summary(
    days: int = Query(30, ge=1, le=365),
    session_id: str | None = Query(default=None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    data = await get_usage_summary(db, user_id, session_id=session_id, days=days)
    return success_response(data=data)
