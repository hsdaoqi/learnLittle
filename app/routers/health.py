from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette import status

from app.db.database import check_database
from app.db.redis_client import check_redis

router = APIRouter()


@router.get("/health", summary="存活探针")
async def health_check() -> dict[str, object]:
    """只确认 API 进程能够响应，不检查外部依赖。"""
    return {
        "code": 200,
        "message": "success",
        "data": {"status": "healthy"},
    }


@router.get("/ready", summary="就绪探针")
async def readiness_check(request: Request) -> JSONResponse:
    database_ok = await check_database(request.app.state.db_engine)
    redis_ok = await check_redis()
    all_ok = database_ok and redis_ok
    response_status = (
        status.HTTP_200_OK
        if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(
        status_code=response_status,
        content={
            "code": response_status,
            "message": "success" if all_ok else "services not ready",
            "data": {
                "status": "ready" if all_ok else "not_ready",
                "dependencies": {"mysql": database_ok, "redis": redis_ok},
            },
        },
    )
