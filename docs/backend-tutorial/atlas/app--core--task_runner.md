# app/core/task_runner.py

[源码](D:/Project/learnLittle/app/core/task_runner.py) | [任务流程 09](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

进程内后台任务跟踪、同 key 串行与有界关机回收。

## 本文件导航

- [spawn_background_task](#fn-2ee8442ce5f0800e)
- [spawn_background_task.run](#fn-11b896a72682b4f3)
- [spawn_background_task.finished](#fn-6db541d31c8cfd3b)
- [drain_background_tasks](#fn-27eafe0fdd42d2b4)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

_tasks: set[asyncio.Task] = set()

_by_key: dict[str, asyncio.Task] = {}
```

<a id="fn-2ee8442ce5f0800e"></a>

## spawn_background_task

源码：[L11](D:/Project/learnLittle/app/core/task_runner.py:11)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

接收返回 awaitable 的 factory，创建并跟踪 task；同 key 关联前一个 task，以便顺序执行。返回任务对象，异常由内部记录；不提供跨进程或重启恢复。

**输入与签名**

```python
def spawn_background_task(factory, *, key: str='') -> asyncio.Task
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return task
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_by_key.get
asyncio.create_task
run
_tasks.add
task.add_done_callback
```

<a id="fn-11b896a72682b4f3"></a>

## spawn_background_task.run

源码：[L20](D:/Project/learnLittle/app/core/task_runner.py:20)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

有前驱时用 shield 等待其结束，再执行当前 factory；普通前驱异常不会阻止新工作。捕获并记录当前工作异常，不把后台失败反向抛到已完成请求。

**输入与签名**

```python
async def run()
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.shield
factory
logger.warning
```

<a id="fn-6db541d31c8cfd3b"></a>

## spawn_background_task.finished

源码：[L36](D:/Project/learnLittle/app/core/task_runner.py:36)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

任务完成回调，从跟踪集合移除引用；只有 key 仍指向该任务才删除 key。防止旧任务完成时误删后来任务的登记。

**输入与签名**

```python
def finished(done)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_tasks.discard
_by_key.get
_by_key.pop
```

<a id="fn-27eafe0fdd42d2b4"></a>

## drain_background_tasks

源码：[L45](D:/Project/learnLittle/app/core/task_runner.py:45)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

限时等待当前任务集合，然后取消还没结束的项并 gather 回收异常。应用退出和测试结束使用；不保证所有任务一定在关机前成功完成。

**输入与签名**

```python
async def drain_background_tasks(timeout: float=5.0) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.wait
list
task.cancel
asyncio.gather
```
