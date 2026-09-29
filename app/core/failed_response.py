"""统一失败响应封装：业务错误码体系 + 业务异常。

错误码分段（与 HTTP 状态码解耦，前端按 code 处理）：
- 400xx: 请求参数错误
- 401xx: 认证失败
- 403xx: 权限不足
- 404xx: 资源不存在
- 409xx: 冲突
- 429xx: 限流
- 500xx: 服务端错误

每个功能阶段只新增当前用到的错误码。
"""

import uuid


class ErrorCode:
    """业务错误码常量。"""

    SUCCESS = 0

    # 400xx - 请求参数错误
    FORMAT_VALIDATION_FAILED = 40002  # 格式校验失败
    INVALID_PARAMETER = 40003  # 参数值无效
    FILE_TOO_LARGE = 40004  # 文件超过大小限制
    UNSUPPORTED_FILE_TYPE = 40005  # 不支持的文件类型
    EMAIL_CODE_INVALID = 40006  # 邮箱验证码错误或已过期
    EMAIL_SEND_FAILED = 40007  # 邮件发送失败

    # 401xx - 认证失败
    TOKEN_EXPIRED = 40101  # Access Token 已过期
    TOKEN_INVALID = 40102  # Token 无效
    PASSWORD_ERROR = 40103  # 用户名或密码错误
    ACCOUNT_LOCKED = 40104  # 账户已锁定（登录失败次数过多）
    REFRESH_TOKEN_INVALID = 40105  # Refresh Token 无效或已失效

    # 404xx - 资源不存在
    NOTE_NOT_FOUND = 40401  # 笔记不存在
    USER_NOT_FOUND = 40403  # 用户不存在
    DOCUMENT_NOT_FOUND = 40404  # 知识库文档不存在
    SESSION_NOT_FOUND = 40402  # 聊天会话不存在
    CATEGORY_NOT_FOUND = 40407  # 分类不存在
    TEMPLATE_NOT_FOUND = 40408  # 笔记模板不存在
    REVIEW_NOT_FOUND = 40409  # 回顾记录不存在
    DEVICE_SESSION_NOT_FOUND = 40405  # 设备会话不存在
    # 409xx - 冲突
    USERNAME_EXISTS = 40901  # 用户名已存在
    EMAIL_EXISTS = 40903  # 邮箱已被占用
    CATEGORY_NAME_EXISTS = 40904  # 同级分类下已存在同名分类
    DOCUMENT_ALREADY_EXISTS = 40905  # 同一用户已上传过相同 MD5 的文档

    # 500xx - 服务端错误
    INTERNAL_ERROR = 50001  # 内部错误
    LLM_CALL_FAILED = 50002  # 大模型调用失败
    EMBEDDING_CALL_FAILED = 50003  # Embedding 调用失败
    EMBEDDING_DIM_MISMATCH = 50004  # 向量库维度与当前模型不一致
    ENDPOINT_RATE_LIMIT = 42901  # 接口限流（含发验证码冷却）
    GLOBAL_RATE_LIMIT = 42902  # 全局限流


_ERROR_MESSAGES: dict[int, str] = {
    ErrorCode.FORMAT_VALIDATION_FAILED: "请求参数校验失败",
    ErrorCode.INVALID_PARAMETER: "参数值无效",
    ErrorCode.FILE_TOO_LARGE: "文件超过大小限制",
    ErrorCode.UNSUPPORTED_FILE_TYPE: "不支持的文件类型",
    ErrorCode.TOKEN_EXPIRED: "Access Token 已过期",
    ErrorCode.TOKEN_INVALID: "Token 无效",
    ErrorCode.EMAIL_CODE_INVALID: "验证码错误或已过期",
    ErrorCode.EMAIL_SEND_FAILED: "邮件发送失败，请稍后重试",
    ErrorCode.ENDPOINT_RATE_LIMIT: "请求过于频繁，请稍后再试",
    ErrorCode.GLOBAL_RATE_LIMIT: "请求过于频繁，请稍后再试",
    ErrorCode.PASSWORD_ERROR: "用户名或密码错误",
    ErrorCode.ACCOUNT_LOCKED: "账户已锁定，请 15 分钟后重试",
    ErrorCode.REFRESH_TOKEN_INVALID: "Refresh Token 无效或已失效",
    ErrorCode.NOTE_NOT_FOUND: "笔记不存在",
    ErrorCode.USER_NOT_FOUND: "用户不存在",
    ErrorCode.DOCUMENT_NOT_FOUND: "知识库文档不存在",
    ErrorCode.SESSION_NOT_FOUND: "会话不存在",
    ErrorCode.CATEGORY_NOT_FOUND: "分类不存在",
    ErrorCode.TEMPLATE_NOT_FOUND: "模板不存在",
    ErrorCode.USERNAME_EXISTS: "用户名已存在",
    ErrorCode.REVIEW_NOT_FOUND: "回顾记录不存在",
    ErrorCode.EMAIL_EXISTS: "该邮箱已被使用",
    ErrorCode.CATEGORY_NAME_EXISTS: "同级分类下已存在同名分类",
    ErrorCode.DOCUMENT_ALREADY_EXISTS: "该文档已存在，无需重复上传",
    ErrorCode.DEVICE_SESSION_NOT_FOUND: "设备会话不存在",
    ErrorCode.INTERNAL_ERROR: "服务器内部错误",
    ErrorCode.LLM_CALL_FAILED: "大模型调用失败",
    ErrorCode.EMBEDDING_CALL_FAILED: "向量化调用失败",
    ErrorCode.EMBEDDING_DIM_MISMATCH: "向量库维度与当前 Embedding 模型不一致，请清空 data/chroma 后重建",
}


class BusinessError(Exception):
    """业务异常：由全局异常处理器统一转换为标准失败响应。

    Attributes:
        code: 业务错误码（见 ErrorCode）
        message: 错误描述；不传则使用错误码默认消息
        detail: 可选的调试详情（开发排查用）
        http_status: HTTP 状态码
    """

    def __init__(
        self,
        code: int,
        message: str | None = None,
        detail: str | None = None,
        http_status: int = 400,
    ):
        self.code = code
        self.message = message or _ERROR_MESSAGES.get(code, "未知错误")
        self.detail = detail
        self.http_status = http_status
        super().__init__(self.message)


def failed_response(
    code: int,
    message: str | None = None,
    detail: str | None = None,
    request_id: str | None = None,
) -> dict:
    """构造统一格式的失败响应。"""
    return {
        "code": code,
        "message": message or _ERROR_MESSAGES.get(code, "未知错误"),
        "detail": detail,
        "request_id": request_id or str(uuid.uuid4()),
    }
