# tests/conftest.py

[源码](D:/Project/learnLittle/tests/conftest.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

## 本文件导航

- [isolated_configuration](#fn-c064b6220f71b753)
- [client](#fn-c5e1c02c3af20fa9)
- [client._create_tables](#fn-89dbbea1d8e95e3d)
- [client.override_session](#fn-536b8abfdc74e78d)
<a id="fn-c064b6220f71b753"></a>

## isolated_configuration

源码：[L30](D:/Project/learnLittle/tests/conftest.py:30)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

autouse fixture 禁止 Settings 读真实 .env 并清配置缓存，yield 后清计划/分类/反思/ReAct 注入。让本机模型配置不污染测试，不启动外网模型。

**输入与签名**

```python
def isolated_configuration(monkeypatch)
```

装饰器/挂载：

```python
@pytest.fixture(autouse=True)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
monkeypatch.setitem
get_settings.cache_clear
set_plan_fn
set_plan_streamer
set_classifier_fn
set_critique_fn
set_react_streamer
pytest.fixture
```

<a id="fn-c5e1c02c3af20fa9"></a>

## client

源码：[L48](D:/Project/learnLittle/tests/conftest.py:48)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

建临时 SQLite、fakeredis、Ephemeral Chroma 和 test Settings，覆盖依赖并提供 TestClient；结束等待后台任务、释放 engine、清注入。不是启动真实 TCP 服务或操作业务数据库。

**输入与签名**

```python
def client(tmp_path)
```

装饰器/挂载：

```python
@pytest.fixture()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield test_client
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
create_async_engine
db_path.as_posix
async_sessionmaker
redis_module.set_redis
fakeredis.aioredis.FakeRedis
Settings
str
set_vector_store
VectorStoreService
chromadb.EphemeralClient
create_app
asyncio.run
_create_tables
set_usage_session_factory
TestClient
test_client.portal.call
close_vector_store
set_embed_fn
set_rerank_fn
reset_cross_encoder
set_hyde_fn
set_route_fn
set_summary_fn
set_summarize_fn
set_note_ai_fn
set_react_streamer
reset_embedding_cache
clear_trace_context
set_session_factory
pytest.fixture
```

<a id="fn-89dbbea1d8e95e3d"></a>

## client._create_tables

源码：[L72](D:/Project/learnLittle/tests/conftest.py:72)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

在临时 engine 上通过 metadata.create_all 建测试表，然后 dispose 以免连接跨事件循环。它不测试完整生产 Alembic 链。

**输入与签名**

```python
async def _create_tables()
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
engine.begin
connection.run_sync
engine.dispose
```

<a id="fn-536b8abfdc74e78d"></a>

## client.override_session

源码：[L82](D:/Project/learnLittle/tests/conftest.py:82)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

测试版 Depends，每次独立 session，正常 commit、异常 rollback。保留事务语义才能检测 after_commit 索引时序。

**输入与签名**

```python
async def override_session()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield session
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
session_factory
session.commit
session.rollback
```
