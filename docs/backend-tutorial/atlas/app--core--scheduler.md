# app/core/scheduler.py

[源码](D:/Project/learnLittle/app/core/scheduler.py) | [任务流程 09](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

每天过期笔记/分类清理的调度和事务包装。

## 本文件导航

- [_run_cleanup](#fn-9e32b0e2f63c07c0)
- [cleanup_expired_notes](#fn-d1109e8c973c0155)
- [cleanup_expired_categories](#fn-6d4afa818faf9518)
- [init_scheduler](#fn-846f03783d7bcf98)
- [shutdown_scheduler](#fn-62e83c2ba1e1c2b6)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
```

<a id="fn-9e32b0e2f63c07c0"></a>

## _run_cleanup

源码：[L21](D:/Project/learnLittle/app/core/scheduler.py:21)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

为一次清理创建 SQL engine/session，调用传入清理函数，提交成功结果，异常回滚并记录，最后释放资源。是定时任务事务包装器，不复用某个 HTTP 请求的会话。

**输入与签名**

```python
async def _run_cleanup(job_name: str, cleanup_fn, days: int) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return count
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
create_database_engine
create_session_factory
factory
cleanup_fn
db.commit
logger.info
db.rollback
logger.exception
engine.dispose
```

<a id="fn-d1109e8c973c0155"></a>

## cleanup_expired_notes

源码：[L42](D:/Project/learnLittle/app/core/scheduler.py:42)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

调度器的笔记清理入口，把 note service 的过期删除交给统一包装器。不要与同名 service 函数混淆：这里负责调度适配。

**输入与签名**

```python
async def cleanup_expired_notes() -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await _run_cleanup('清理过期笔记', cleanup, get_settings().recycle_bin_cleanup_days)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_run_cleanup
get_settings
```

<a id="fn-6d4afa818faf9518"></a>

## cleanup_expired_categories

源码：[L48](D:/Project/learnLittle/app/core/scheduler.py:48)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

调度器的分类清理入口，委托 category service 执行业务删除。删除规则在 service，资源/事务在包装器。

**输入与签名**

```python
async def cleanup_expired_categories() -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await _run_cleanup('清理过期分类', cleanup, get_settings().recycle_bin_cleanup_days)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_run_cleanup
get_settings
```

<a id="fn-846f03783d7bcf98"></a>

## init_scheduler

源码：[L54](D:/Project/learnLittle/app/core/scheduler.py:54)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

为模块已构造的 scheduler 登记每日 03:00 笔记、03:30 分类清理并启动，运行中则返回。由 lifespan 在非 reload、非 test 时调用，不是所有 import 都启动调度。

**输入与签名**

```python
def init_scheduler() -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
scheduler.add_job
CronTrigger
scheduler.start
logger.info
```

<a id="fn-62e83c2ba1e1c2b6"></a>

## shutdown_scheduler

源码：[L78](D:/Project/learnLittle/app/core/scheduler.py:78)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

scheduler 正在运行时调用 shutdown(wait=False) 并记录日志。没有清空模块引用，也不是清空回收站的命令。

**输入与签名**

```python
def shutdown_scheduler() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
scheduler.shutdown
logger.info
```
