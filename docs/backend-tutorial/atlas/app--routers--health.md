# app/routers/health.py

[源码](D:/Project/learnLittle/app/routers/health.py) | [任务流程 09](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

进程健康与 SQL/Redis 就绪探针。

## 本文件导航

- [health_check](#fn-38b99047079e6ae4)
- [readiness_check](#fn-6ac0872997e6c7a5)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
router = APIRouter()
```

<a id="fn-38b99047079e6ae4"></a>

## health_check

源码：[L12](D:/Project/learnLittle/app/routers/health.py:12)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

立即返回进程存活响应，使用自己的 code=200 信封。不会连接外部依赖，适合区分进程存活与业务就绪。

**输入与签名**

```python
async def health_check() -> dict[str, object]
```

装饰器/挂载：

```python
@router.get('/health', summary='存活探针')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'code': 200, 'message': 'success', 'data': {'status': 'healthy'}}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
router.get
```

<a id="fn-6ac0872997e6c7a5"></a>

## readiness_check

源码：[L22](D:/Project/learnLittle/app/routers/health.py:22)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

检查 SQL 和 Redis 状态，均可用 HTTP 200 否则 503。不是 SMTP、模型、Chroma 或真实检索效果探针。

**输入与签名**

```python
async def readiness_check(request: Request) -> JSONResponse
```

装饰器/挂载：

```python
@router.get('/ready', summary='就绪探针')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return JSONResponse(status_code=response_status, content={'code': response_status, 'message': 'success' if all_ok else 'services not ready', 'data': {'status': 'ready' if all_ok else 'not_ready', 'dependencies': {'mysql': database_ok, 'r ... [截短，完整见源码]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
check_database
check_redis
JSONResponse
router.get
```
