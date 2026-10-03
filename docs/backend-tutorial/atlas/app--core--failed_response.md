# app/core/failed_response.py

[源码](D:/Project/learnLittle/app/core/failed_response.py) | [任务流程 01](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

错误码、BusinessError 载体与失败响应字典。

## 本文件导航

- [BusinessError.__init__](#fn-415ea399f006a134)
- [failed_response](#fn-19c94f48c34ddd63)

## 类与字段

### ErrorCode

纯业务码常量集合，与 HTTP 状态分离；没有函数也仍是重要接口契约。

声明位置：[L18](D:/Project/learnLittle/app/core/failed_response.py:18)。父类：`无显式父类`。

```python
SUCCESS = 0

FORMAT_VALIDATION_FAILED = 40002

INVALID_PARAMETER = 40003

FILE_TOO_LARGE = 40004

UNSUPPORTED_FILE_TYPE = 40005

EMAIL_CODE_INVALID = 40006

EMAIL_SEND_FAILED = 40007

TOKEN_EXPIRED = 40101

TOKEN_INVALID = 40102

PASSWORD_ERROR = 40103

ACCOUNT_LOCKED = 40104

REFRESH_TOKEN_INVALID = 40105

NOTE_NOT_FOUND = 40401

USER_NOT_FOUND = 40403

DOCUMENT_NOT_FOUND = 40404

SESSION_NOT_FOUND = 40402

CATEGORY_NOT_FOUND = 40407

TEMPLATE_NOT_FOUND = 40408

REVIEW_NOT_FOUND = 40409

DEVICE_SESSION_NOT_FOUND = 40405

USERNAME_EXISTS = 40901

EMAIL_EXISTS = 40903

CATEGORY_NAME_EXISTS = 40904

DOCUMENT_ALREADY_EXISTS = 40905

INTERNAL_ERROR = 50001

LLM_CALL_FAILED = 50002

EMBEDDING_CALL_FAILED = 50003

EMBEDDING_DIM_MISMATCH = 50004

ENDPOINT_RATE_LIMIT = 42901

GLOBAL_RATE_LIMIT = 42902
```

### BusinessError

携带 code/message/detail/http_status 的异常，由 handler 转为 HTTP 响应。

声明位置：[L95](D:/Project/learnLittle/app/core/failed_response.py:95)。父类：`Exception`。


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
_ERROR_MESSAGES: dict[int, str] = {ErrorCode.FORMAT_VALIDATION_FAILED: '请求参数校验失败', ErrorCode.INVALID_PARAMETER: '参数值无效', ErrorCode.FILE_TOO_LARGE: '文件超过大小限制', ErrorCode.UNSUPPORTED_FILE_TYPE: '不支持的文件类型', ErrorCode.TOKEN_EXPIRED: 'Access Token 已过期', ErrorCode.TOKEN_INVALID: 'Token 无效', ErrorCode.EMAIL_CODE_INVALID: '验证码错误或已过期', ErrorCode.EMAIL_SEND_FAILED: '邮件发送失败，请稍后重试', ErrorCode.ENDPOINT_RATE_LIMIT: '请求过于频繁，请稍后再试', ErrorCode.GLOBAL_RATE_LIMIT: '请求过于频繁，请稍后再试', ErrorCode.PASSWORD_ERROR: '用户名或密码错误', ErrorCode.ACCOUNT_LOCKED: '账户已锁定，请 15 分钟后重试', ErrorCode.REFRESH_TOKEN_INVALID: 'Refresh Token 无效或已失效', ErrorCode.NOTE_NOT_FOUND: '笔记不存在', ErrorCode.USER_NOT_FOUND: '用户不存在', ErrorCode.DOCUMENT_NOT_FOUND: '知识库文档不存在', ErrorCode.SESSION_NOT_FOUND: '会话不存在', ErrorCode.CATEGORY_NOT_FOUND: '分类不存在', ErrorCode.TEMPLATE_NOT_FOUND: '模板不存在', ErrorCode.USERNAME_EXISTS: '用户名已存在', ErrorCode.REVIEW_NOT_FOUND: '回顾记录不存在', ErrorCode.EMAIL_EXISTS: '该邮箱已被使用', ErrorCode.CATEGORY_NAME_EXISTS: '同级分类下已存在同名分类', ErrorCode.DOCUMENT_ALREADY_EXISTS: '该文档已存在，无需重复上传', ErrorCode.DEVICE_SESSION_NOT_FOUND: '设备会话不存在', ErrorCode.INTERNAL_ERROR: '服务器内部错误', ErrorCode.LLM_CALL_FAILED: '大模型调用失败', ErrorCode.EMBEDDING_CALL_FAILED: '向量化调用失败', ErrorCode.EMBEDDING_DIM_MISMATCH: '向量库维度与当前 Embedding 模型不一致，请清空 data/chroma 后重建'}
```

<a id="fn-415ea399f006a134"></a>

## BusinessError.__init__

源码：[L105](D:/Project/learnLittle/app/core/failed_response.py:105)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

把业务 code、可选 message/detail 与 HTTP 状态存到异常实例，并选取默认错误文案。它是可被统一 handler 识别的信号，不是直接返回给浏览器的 Response。

**输入与签名**

```python
def __init__(self, code: int, message: str | None=None, detail: str | None=None, http_status: int=400)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_ERROR_MESSAGES.get
super().__init__
super
```

<a id="fn-19c94f48c34ddd63"></a>

## failed_response

源码：[L119](D:/Project/learnLittle/app/core/failed_response.py:119)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

构造带 code/message/detail/request_id 的普通字典。HTTP 状态由 handler 或中间件的 JSONResponse 决定，本函数本身不创建 Response。

**输入与签名**

```python
def failed_response(code: int, message: str | None=None, detail: str | None=None, request_id: str | None=None) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'code': code, 'message': message or _ERROR_MESSAGES.get(code, '未知错误'), 'detail': detail, 'request_id': request_id or str(uuid.uuid4())}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_ERROR_MESSAGES.get
str
uuid.uuid4
```
