# app/db/redis_client.py

[源码](D:/Project/learnLittle/app/db/redis_client.py) | [任务流程 01](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

Redis 单例资源与注入/探针；并非所有使用者都采用相同容错策略。

## 本文件导航

- [set_redis](#fn-98fc47207dd46f8f)
- [get_redis](#fn-158a51acb1ca1043)
- [create_redis_client](#fn-38cfe7d8b0d51129)
- [init_redis](#fn-24e9eb9ad9821f7d)
- [close_redis](#fn-4593ef1925f364df)
- [check_redis](#fn-9eea03fb9a884688)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

_client: redis.Redis | None = None
```

<a id="fn-98fc47207dd46f8f"></a>

## set_redis

源码：[L19](D:/Project/learnLittle/app/db/redis_client.py:19)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

替换模块持有的 Redis 实例，测试用 FakeRedis。是进程级状态替换，不是给 Redis 写业务键。

**输入与签名**

```python
def set_redis(client: redis.Redis) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-158a51acb1ca1043"></a>

## get_redis

源码：[L25](D:/Project/learnLittle/app/db/redis_client.py:25)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

返回已经初始化的客户端，未准备好则 RuntimeError。这样业务不会拿到 None 后悄悄丢操作。

**输入与签名**

```python
def get_redis() -> redis.Redis
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _client
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
RuntimeError
```

<a id="fn-38cfe7d8b0d51129"></a>

## create_redis_client

源码：[L35](D:/Project/learnLittle/app/db/redis_client.py:35)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

根据 host/port/db 建异步 Redis 客户端，decode_responses=True 让命令返回字符串。连通验证在初始化或探针，不在这个构造函数内。

**输入与签名**

```python
def create_redis_client(settings: Settings) -> redis.Redis
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, decode_responses=True)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
redis.Redis
```

<a id="fn-24e9eb9ad9821f7d"></a>

## init_redis

源码：[L45](D:/Project/learnLittle/app/db/redis_client.py:45)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

复用注入实例或新建客户端，并通过 ping 验证。应用启动调用；初始化错误可阻止正常启动，不等于聊天缓存的容错读写。

**输入与签名**

```python
async def init_redis(settings: Settings) -> redis.Redis
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _client
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
create_redis_client
client.ping
logger.info
```

<a id="fn-4593ef1925f364df"></a>

## close_redis

源码：[L58](D:/Project/learnLittle/app/db/redis_client.py:58)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

关闭当前 Redis 客户端并清理模块引用。由生命周期调用，避免连接跨测试或跨运行残留。

**输入与签名**

```python
async def close_redis() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_client.aclose
logger.info
```

<a id="fn-9eea03fb9a884688"></a>

## check_redis

源码：[L67](D:/Project/learnLittle/app/db/redis_client.py:67)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

两秒内 ping，成功返回 True，失败 False。为 ready 探针服务，不检查每种 Redis 数据结构是否完整。

**输入与签名**

```python
async def check_redis() -> bool
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
asyncio.timeout
_client.ping
```
