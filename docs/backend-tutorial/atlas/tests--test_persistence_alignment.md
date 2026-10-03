# tests/test_persistence_alignment.py

[源码](D:/Project/learnLittle/tests/test_persistence_alignment.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

## 本文件导航

- [test_note_index_dispatches_after_commit_not_rollback_or_metadata_changes](#fn-c7bac31d2e63fa91)
- [test_note_index_dispatches_after_commit_not_rollback_or_metadata_changes.index](#fn-37756893f599909b)
- [test_note_index_dispatches_after_commit_not_rollback_or_metadata_changes.run](#fn-d98d4957681b485b)
- [test_hot_cache_rebuild_preserves_chronological_order](#fn-a1a794b4d5e994e8)
- [test_hot_cache_rebuild_preserves_chronological_order.run](#fn-c4b65847a116fcc1)
- [test_usage_preserves_provider_zero_counts](#fn-c6ea6e97a22b58ea)
- [test_additive_chat_migration_preserves_existing_titles_and_messages](#fn-ed475f903efafc59)
<a id="fn-c7bac31d2e63fa91"></a>

## test_note_index_dispatches_after_commit_not_rollback_or_metadata_changes

源码：[L14](D:/Project/learnLittle/tests/test_persistence_alignment.py:14)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

替换索引为记录器，分别测试创建提交、元数据更新、标题回滚、标题提交。确认只在有效正文事实提交后派发。

**输入与签名**

```python
def test_note_index_dispatches_after_commit_not_rollback_or_metadata_changes(client, monkeypatch)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
monkeypatch.setattr
client.portal.call
```

<a id="fn-37756893f599909b"></a>

## test_note_index_dispatches_after_commit_not_rollback_or_metadata_changes.index

源码：[L20](D:/Project/learnLittle/tests/test_persistence_alignment.py:20)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

记录被索引实体的 ID/标题，替代外部 embedding 与 Chroma。用于观察后台派发次数和读到的最新内容。

**输入与签名**

```python
async def index(note)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
indexed.append
```

<a id="fn-d98d4957681b485b"></a>

## test_note_index_dispatches_after_commit_not_rollback_or_metadata_changes.run

源码：[L25](D:/Project/learnLittle/tests/test_persistence_alignment.py:25)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

在测试事件循环执行四组事务，每次 drain 后断言索引列表。关键断言在 commit 之前也检查没有提前索引。

**输入与签名**

```python
async def run()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert not indexed
assert indexed == [(note_id, 'first')]
assert len(indexed) == 1
assert indexed[-1] == (note_id, 'committed')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
factory
db.add
User
db.commit
note_service.create_note
NoteCreate
drain_background_tasks
note_service.update_note
len
db.rollback
```

<a id="fn-a1a794b4d5e994e8"></a>

## test_hot_cache_rebuild_preserves_chronological_order

源码：[L54](D:/Project/learnLittle/tests/test_persistence_alignment.py:54)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

调用内部 run 检查 30 条输入在 buffer=20 后得到 11..30 正序。防止 LPUSH/反转组合错误。

**输入与签名**

```python
def test_hot_cache_rebuild_preserves_chronological_order(client)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.portal.call
```

<a id="fn-c4b65847a116fcc1"></a>

## test_hot_cache_rebuild_preserves_chronological_order.run

源码：[L57](D:/Project/learnLittle/tests/test_persistence_alignment.py:57)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

构造递增消息，重建 Redis 热缓存后读回并精确比较 ID 顺序。不是查询正式聊天历史。

**输入与签名**

```python
async def run()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert [row['id'] for row in result] == list(range(11, 31))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
str
range
rebuild_messages
get_recent_messages
list
```

<a id="fn-c6ea6e97a22b58ea"></a>

## test_usage_preserves_provider_zero_counts

源码：[L66](D:/Project/learnLittle/tests/test_persistence_alignment.py:66)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

断言供应商 completion_tokens=0 不变成文本估算，并检查完全没 usage 的向上估算。覆盖 truthiness 导致错误计量的回归。

**输入与签名**

```python
def test_usage_preserves_provider_zero_counts()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert parse_usage({'usage': {'prompt_tokens': 7, 'completion_tokens': 0}}, 'long prompt', 'tool') == (7, 0, 7)
assert parse_usage(None, 'abc', 'ab') == (2, 1, 3)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
parse_usage
```

<a id="fn-ed475f903efafc59"></a>

## test_additive_chat_migration_preserves_existing_titles_and_messages

源码：[L71](D:/Project/learnLittle/tests/test_persistence_alignment.py:71)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

在临时 SQLite 构造旧表/旧数据，真实调用 f1 upgrade/downgrade，检查标题保护、键字段与旧正文保留。只验证该增量迁移，不运行完整生产链。

**输入与签名**

```python
def test_additive_chat_migration_preserves_existing_titles_and_messages(tmp_path)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert connection.execute(text('SELECT id, title_manual FROM chat_sessions ORDER BY id')).all() == [('one', 0), ('two', 1)]
assert connection.scalar(text('SELECT content FROM chat_messages')) == 'existing message'
assert 'idempotency_key' in {column['name'] for column in inspect(connection).get_columns('chat_messages')}
assert 'title_manual' not in {column['name'] for column in inspect(connection).get_columns('chat_sessions')}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Path
importlib.util.spec_from_file_location
importlib.util.module_from_spec
spec.loader.exec_module
create_engine
engine.begin
connection.execute
text
Operations
MigrationContext.configure
module.upgrade
connection.execute(text('SELECT id, title_manual FROM chat_sessions ORDER BY id')).all
connection.scalar
inspect(connection).get_columns
inspect
module.downgrade
engine.dispose
```
