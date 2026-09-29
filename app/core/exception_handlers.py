"""全局异常处理器注册。

统一把三类异常转换为标准失败响应（含 request_id）：
- BusinessError：业务异常，按其 http_status 返回
- RequestValidationError：Pydantic 参数校验失败，422
- Exception：未预期异常，兜底返回 500（不向客户端泄露堆栈）
"""

import logging
import traceback

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.failed_response import BusinessError, failed_response, ErrorCode

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """"""

    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
        logger.warning(
            "业务异常： %s %s - code = %s,message = %s",
            request.method, request.url.path, exc.code, exc.message
        )
        return JSONResponse(
            status_code=exc.http_status,
            content=failed_response(code=exc.code, message=exc.message, detail=exc.detail)
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [" -> ".join(str(loc) for loc in err["loc"]) + f": {err['msg']}" for err in exc.errors()]
        detail = "; ".join(errors)
        logger.warning("参数校验失败: %s %s - %s", request.method, request.url.path, detail)
        return JSONResponse(
            status_code=422,
            content=failed_response(
                code=ErrorCode.FORMAT_VALIDATION_FAILED,
                message="请求参数校验失败",
                detail=detail,
            ),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "未预期异常: %s %s\n%s", request.method, request.url.path, traceback.format_exc(),
        )
        return JSONResponse(
            status_code=500,
            content=failed_response(code=ErrorCode.INTERNAL_ERROR),
        )
