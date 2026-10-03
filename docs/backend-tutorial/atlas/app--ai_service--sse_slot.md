# app/ai_service/sse_slot.py

[源码](D:/Project/learnLittle/app/ai_service/sse_slot.py) | [任务流程 09](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

主聊天按用户并发计数，Redis 故障退进程内。

## 本文件导航

- [acquire_sse_slot](#fn-4ba6c0a2aa1e3dba)
- [release_sse_slot](#fn-2e195cb3417d9924)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

_local_counts: dict[str, int] = {}
```

<a id="fn-4ba6c0a2aa1e3dba"></a>

## acquire_sse_slot

源码：[L18](D:/Project/learnLittle/app/ai_service/sse_slot.py:18)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

Redis INCR 按用户检查并发上限，首次设 120 秒 TTL，超限撤回本次计数；失败退本进程字典。不是可靠长连接租约，TTL 不续期。

**输入与签名**

```python
async def acquire_sse_slot(user_id: str, settings: Settings) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return False
return True
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
max
get_redis
redis.incr
redis.expire
redis.decr
logger.warning
_local_counts.get
```

<a id="fn-2e195cb3417d9924"></a>

## release_sse_slot

源码：[L44](D:/Project/learnLittle/app/ai_service/sse_slot.py:44)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

尝试 Redis DECR，失败则减少本地计数并防负值。依赖与申请阶段一致的后端可用状态，不是持久化资源锁。

**输入与签名**

```python
async def release_sse_slot(user_id: str) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().decr
get_redis
logger.debug
max
_local_counts.get
```
