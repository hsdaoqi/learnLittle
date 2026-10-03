# app/core/rate_limit.py

[源码](D:/Project/learnLittle/app/core/rate_limit.py) | [任务流程 09](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

Redis 固定窗口，全局与具体 path 桶、特殊动作额度。

## 本文件导航

- [endpoint_limit_for](#fn-e58f8d8d7df2eed9)
- [identity_for](#fn-a2259e64ae710564)
- [_hit](#fn-84e7b7aee76f0884)
- [check_rate_limit](#fn-62afffca15017fe7)
- [check_named_limit](#fn-82c0ff222a21c766)
- [RateLimitMiddleware.dispatch](#fn-5d9614ad69a59e0c)

## 类与字段

### RateLimitMiddleware

继承请求中间件，把固定窗口检查接到路由之前。

声明位置：[L116](D:/Project/learnLittle/app/core/rate_limit.py:116)。父类：`BaseHTTPMiddleware`。


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

ENDPOINT_RATE_LIMITS = {'/api/v1/chat': 10, '/api/v1/knowledge/upload': 20, '/api/v1/note': 60, '/api/v1/auth/send-code': 10, '/api/v1/auth': 5}

SKIP_PREFIXES = ('/health', '/ready', '/docs', '/redoc', '/openapi.json', '/static')
```

<a id="fn-e58f8d8d7df2eed9"></a>

## endpoint_limit_for

源码：[L38](D:/Project/learnLittle/app/core/rate_limit.py:38)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

根据 URL 前缀决定接口窗口配额，认证、聊天和普通接口限制不同。返回数值供计数检查，并不是路由注册函数。

**输入与签名**

```python
def endpoint_limit_for(path: str, default: int) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return best_limit
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
ENDPOINT_RATE_LIMITS.items
path.startswith
len
```

<a id="fn-a2259e64ae710564"></a>

## identity_for

源码：[L48](D:/Project/learnLittle/app/core/rate_limit.py:48)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

尝试把合法 access JWT 解析成用户标识，否则按客户端 IP 标识匿名请求。SSE type 不算 access，限流身份与实际聊天鉴权是两段逻辑。

**输入与签名**

```python
def identity_for(request: Request, settings: Settings) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return str(user_id)
return f'anon:{ip}'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
request.headers.get
authorization.split
len
parts[0].lower
jwt.decode
payload.get
str
```

<a id="fn-84e7b7aee76f0884"></a>

## _hit

源码：[L67](D:/Project/learnLittle/app/core/rate_limit.py:67)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

对一个 Redis key INCR，首次设置 window+1 秒 TTL，返回整数计数。limit 参数在此未用于比较，超限判断在上层；INCR 与 EXPIRE 不是一条原子脚本。

**输入与签名**

```python
async def _hit(key: str, limit: int, window: int) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return int(count)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
redis.incr
redis.expire
int
```

<a id="fn-62afffca15017fe7"></a>

## check_rate_limit

源码：[L75](D:/Project/learnLittle/app/core/rate_limit.py:75)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

组织用户/IP 的全局和接口计数，超额抛业务限制错误。一个请求可能涉及多个计数键，不能理解为一条原子多键命令。

**输入与签名**

```python
async def check_rate_limit(identity: str, path: str, *, global_limit: int, default_limit: int, window: int) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
int
time.time
_hit
logger.warning
BusinessError
endpoint_limit_for
```

<a id="fn-82c0ff222a21c766"></a>

## check_named_limit

源码：[L106](D:/Project/learnLittle/app/core/rate_limit.py:106)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

给特定业务动作建立独立窗口计数，例如彻底删除。路由决定是否调用，不替代通用中间件额度。

**输入与签名**

```python
async def check_named_limit(identity: str, name: str, limit: int, window: int=60) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
int
time.time
_hit
BusinessError
```

<a id="fn-5d9614ad69a59e0c"></a>

## RateLimitMiddleware.dispatch

源码：[L117](D:/Project/learnLittle/app/core/rate_limit.py:117)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

请求进入路由前按开关/路径/身份检查限流，错误转为统一响应，否则 call_next。关闭限流不会跳过路由自己的鉴权。

**输入与签名**

```python
async def dispatch(self, request: Request, call_next)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await call_next(request)
return JSONResponse(status_code=exc.http_status, content=failed_response(code=exc.code, message=exc.message, detail=exc.detail))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
any
path.startswith
call_next
check_rate_limit
identity_for
JSONResponse
failed_response
```
