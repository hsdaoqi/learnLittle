# alembic/env.py

[源码](D:/Project/learnLittle/alembic/env.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

Alembic 在线/离线入口与异步连接桥接；直接执行会采用配置数据库，文档工具不会导入它。

## 本文件导航

- [run_migrations_offline](#fn-64555558ba6b0d9e)
- [do_run_migrations](#fn-a1a8bf4441d38aa9)
- [run_async_migrations](#fn-567aa9735384029b)
- [run_migrations_online](#fn-3f58270bd73f0136)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
config = context.config

target_metadata = Base.metadata
```

<a id="fn-64555558ba6b0d9e"></a>

## run_migrations_offline

源码：[L37](D:/Project/learnLittle/alembic/env.py:37)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

配置 URL、metadata 与 literal_binds，在离线事务上下文运行迁移以输出 SQL。不建立真实数据库连接，但生成脚本仍需人工审查。

**输入与签名**

```python
def run_migrations_offline() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
config.get_main_option
context.configure
context.begin_transaction
context.run_migrations
```

<a id="fn-a1a8bf4441d38aa9"></a>

## do_run_migrations

源码：[L50](D:/Project/learnLittle/alembic/env.py:50)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

收到同步 connection 后配置 Alembic 并执行版本链。由异步连接的 run_sync 桥接调用。

**输入与签名**

```python
def do_run_migrations(connection: Connection) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
context.configure
context.begin_transaction
context.run_migrations
```

<a id="fn-567aa9735384029b"></a>

## run_async_migrations

源码：[L56](D:/Project/learnLittle/alembic/env.py:56)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

创建无连接池迁移 engine，连接后 run_sync 调同步迁移，最后 dispose。它连接实际配置数据库，与静态文档扫描不同。

**输入与签名**

```python
async def run_async_migrations() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
async_engine_from_config
config.get_section
connectable.connect
connection.run_sync
connectable.dispose
```

<a id="fn-3f58270bd73f0136"></a>

## run_migrations_online

源码：[L67](D:/Project/learnLittle/alembic/env.py:67)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

用 asyncio.run 启动在线异步迁移协程。只适合 CLI 入口，不是 HTTP 请求内随手调用的建表工具。

**输入与签名**

```python
def run_migrations_online() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.run
run_async_migrations
```
