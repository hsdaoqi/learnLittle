"""统一成功响应封装。

所有业务 API 的成功响应都通过 success_response() 构造，保证格式统一：

    {"code": 0, "message": "ok", "data": ..., "request_id": "..."}
"""

import uuid
from typing import Any


def success_response(
        data: Any = None,
        message: str = "ok",
        code: int = 0,
        request_id: str | None = None,
) -> dict:
    """构造统一格式的成功响应。

    request_id 不传时自动生成，用于日志与问题追踪。
    """
    return {
        "code": code,
        "message": message,
        "data": data,
        "request_id": request_id or str(uuid.uuid4()),
    }
