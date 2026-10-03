# app/core/after_commit.py

[源码](D:/Project/learnLittle/app/core/after_commit.py) | [任务流程 09](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

Session 事件监听，成功提交派发、回滚丢弃派生工作。

## 本文件导航

- [defer_after_commit](#fn-08da561b779c14bd)
- [_committed](#fn-80be83d068819dda)
- [_rolled_back](#fn-acc23d579f581ecc)
<a id="fn-08da561b779c14bd"></a>

## defer_after_commit

源码：[L9](D:/Project/learnLittle/app/core/after_commit.py:9)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

将异步工作工厂放到 session.info 的字典，以 key 去重覆盖。现在只登记，不立即调用；用于避免 SQL 回滚后却已经同步向量。

**输入与签名**

```python
def defer_after_commit(session, key, factory)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
session.info.setdefault
```

<a id="fn-80be83d068819dda"></a>

## _committed

源码：[L14](D:/Project/learnLittle/app/core/after_commit.py:14)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

SQLAlchemy after_commit 监听器取出登记的工厂，交给后台 task runner。任务在进程内运行，提交 SQL 与派发任务之间不是持久化 Outbox 协议。

**输入与签名**

```python
def _committed(session)
```

装饰器/挂载：

```python
@event.listens_for(Session, 'after_commit')
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
session.info.pop('after_commit_jobs', {}).items
session.info.pop
spawn_background_task
event.listens_for
```

<a id="fn-acc23d579f581ecc"></a>

## _rolled_back

源码：[L20](D:/Project/learnLittle/app/core/after_commit.py:20)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

after_rollback 监听器丢弃待派发工作，保证失败事务不执行这些后续动作。不会撤销此前已完成的外部动作。

**输入与签名**

```python
def _rolled_back(session)
```

装饰器/挂载：

```python
@event.listens_for(Session, 'after_rollback')
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
session.info.pop
event.listens_for
```
