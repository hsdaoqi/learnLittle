# app/core/exception_handlers.py

[源码](D:/Project/learnLittle/app/core/exception_handlers.py) | [任务流程 01](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

把业务、校验与未预期异常转换为 HTTP 失败信封。

## 本文件导航

- [register_exception_handlers](#fn-70a8ee1c65560fc7)
- [register_exception_handlers.business_error_handler](#fn-67e54730811d1d4d)
- [register_exception_handlers.validation_error_handler](#fn-9bb4f47b3dc6c52b)
- [register_exception_handlers.general_exception_handler](#fn-68a9a04cad9a6fac)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)
```

<a id="fn-70a8ee1c65560fc7"></a>

## register_exception_handlers

源码：[L21](D:/Project/learnLittle/app/core/exception_handlers.py:21)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

向指定 FastAPI 应用登记业务、请求校验和兜底异常处理器。函数本身完成注册，内层 handler 在未来请求失败时才执行。

**输入与签名**

```python
def register_exception_handlers(app: FastAPI) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-67e54730811d1d4d"></a>

## register_exception_handlers.business_error_handler

源码：[L25](D:/Project/learnLittle/app/core/exception_handlers.py:25)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

读取 BusinessError 携带的状态、code 和 detail，交给 failed_response。保留业务可识别原因，不将所有失败都变成 500。

**输入与签名**

```python
async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse
```

装饰器/挂载：

```python
@app.exception_handler(BusinessError)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return JSONResponse(status_code=exc.http_status, content=failed_response(code=exc.code, message=exc.message, detail=exc.detail))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
logger.warning
JSONResponse
failed_response
app.exception_handler
```

<a id="fn-9bb4f47b3dc6c52b"></a>

## register_exception_handlers.validation_error_handler

源码：[L36](D:/Project/learnLittle/app/core/exception_handlers.py:36)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

把 FastAPI/Pydantic 的参数验证异常格式化为统一失败响应。发生于路由业务逻辑之前，不能当作数据库约束错误。

**输入与签名**

```python
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse
```

装饰器/挂载：

```python
@app.exception_handler(RequestValidationError)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return JSONResponse(status_code=422, content=failed_response(code=ErrorCode.FORMAT_VALIDATION_FAILED, message='请求参数校验失败', detail=detail))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
' -> '.join
str
exc.errors
'; '.join
logger.warning
JSONResponse
failed_response
app.exception_handler
```

<a id="fn-68a9a04cad9a6fac"></a>

## register_exception_handlers.general_exception_handler

源码：[L50](D:/Project/learnLittle/app/core/exception_handlers.py:50)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

记录未处理异常并返回通用服务端失败信封。避免把完整堆栈直接作为用户响应；事务回滚仍由拥有事务的代码负责。

**输入与签名**

```python
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse
```

装饰器/挂载：

```python
@app.exception_handler(Exception)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return JSONResponse(status_code=500, content=failed_response(code=ErrorCode.INTERNAL_ERROR))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
logger.error
traceback.format_exc
JSONResponse
failed_response
app.exception_handler
```
