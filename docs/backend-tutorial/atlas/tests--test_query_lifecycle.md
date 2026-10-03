# tests/test_query_lifecycle.py

[源码](D:/Project/learnLittle/tests/test_query_lifecycle.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

## 本文件导航

- [auth](#fn-ccf03d8ca534c20b)
- [query](#fn-cd8b117803739350)
- [test_query_rag_failure_preserves_user_message_and_final_answer](#fn-d4d107d181bc3005)
- [test_query_rag_failure_preserves_user_message_and_final_answer.failed_rag](#fn-0d9c3355649c7a4f)
- [test_query_rag_failure_preserves_user_message_and_final_answer.fake_react](#fn-16239bf7c22c568a)
- [test_query_idempotency_replays_once_and_isolates_users](#fn-0d843eba4e120c98)
- [test_query_idempotency_replays_once_and_isolates_users.fake](#fn-e5ee2da787d5dd9f)
- [test_inflight_duplicate_does_not_run_agent_twice](#fn-57d7814e37c7ff66)
- [test_inflight_duplicate_does_not_run_agent_twice.fake](#fn-9523fa13a78b6d7d)
- [test_inflight_duplicate_does_not_run_agent_twice.run](#fn-3bbfc3172ec72d80)
- [test_inflight_duplicate_does_not_run_agent_twice.run.collect](#fn-a36d3f30890ce3d4)
- [test_full_sql_memory_is_not_limited_by_redis_window](#fn-c0a8adb75b66bb6b)
- [test_full_sql_memory_is_not_limited_by_redis_window.seed](#fn-d9e14872691caa1e)
- [test_full_sql_memory_is_not_limited_by_redis_window.fake](#fn-778f4d4d0493119a)
- [test_slow_title_does_not_block_done_or_overwrite_manual_title](#fn-6d9b84b7660ed2ef)
- [test_slow_title_does_not_block_done_or_overwrite_manual_title.slow_title](#fn-71274ee88ca8e162)
- [test_slow_title_does_not_block_done_or_overwrite_manual_title.fake](#fn-969e1ba325bab439)
- [test_slow_title_does_not_block_done_or_overwrite_manual_title.wait_started](#fn-b9fed36b5d75331d)
- [test_slow_title_does_not_block_done_or_overwrite_manual_title.finish](#fn-e5c3e834a0dfaa03)
- [test_titles_update_in_early_rounds_only](#fn-e0d9df23b8350ac9)
- [test_titles_update_in_early_rounds_only.title](#fn-a0709ea6c0799512)
- [test_titles_update_in_early_rounds_only.run](#fn-a7eae975f2a95435)
- [test_registration_requires_verified_email_by_default](#fn-ccb87fc394b80ad7)
- [test_registration_requires_verified_email_by_default.verify](#fn-ea9db416d8dc531f)
- [test_sse_token_single_use_and_not_profile_auth](#fn-8a3fda62125f3540)
- [test_sse_token_single_use_and_not_profile_auth.expire](#fn-3eb2e1c720b46841)
- [test_chat_graph_cancellation_closes_model_stream](#fn-e9904a65d0c158e2)
- [test_chat_graph_cancellation_closes_model_stream.endless](#fn-e606966f588b5739)
<a id="fn-ccf03d8ca534c20b"></a>

## auth

源码：[L15](D:/Project/learnLittle/tests/test_query_lifecycle.py:15)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

测试注册登录，返回 headers 和 user_id，先断言注册成功。帮助后续 SQL 断言定位用户。

**输入与签名**

```python
def auth(client, name)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert response.status_code == 200
return ({'Authorization': f'Bearer {tokens['access_token']}'}, user_id)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.post
response.json
client.post('/api/v1/auth/login', json={'username': name, 'password': 'passw0rd123'}).json
```

<a id="fn-cd8b117803739350"></a>

## query

源码：[L27](D:/Project/learnLittle/tests/test_query_lifecycle.py:27)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

POST 主 query 并断言 HTTP 200，再从 data: 行解出事件列表。流内 error 仍可能是 HTTP 200，后续必须看 type。

**输入与签名**

```python
def query(client, headers, **payload)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert response.status_code == 200
return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith('data: ')]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.post
json.loads
response.text.splitlines
line.startswith
```

<a id="fn-d4d107d181bc3005"></a>

## test_query_rag_failure_preserves_user_message_and_final_answer

源码：[L33](D:/Project/learnLittle/tests/test_query_lifecycle.py:33)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

让 RAG 抛错但 fake ReAct 先草稿后替换，断言检索前已有用户消息、最终 corrected 同时出现在 done 和 SQL。覆盖先保存与替换一致性。

**输入与签名**

```python
def test_query_rag_failure_preserves_user_message_and_final_answer(client, monkeypatch)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert seen == {'saved_first': 1, 'history': []}
assert done['type'] == 'done'
assert done['answer'] == done['assistant_message']['content'] == 'corrected'
assert done['used_retrieval'] is False
assert [row['content'] for row in rows] == ['hello', 'corrected']
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
auth
monkeypatch.setattr
set_react_streamer
query
client.get(f'/api/v1/chat/sessions/{done['session_id']}/messages', headers=headers).json
client.get
```

<a id="fn-0d9c3355649c7a4f"></a>

## test_query_rag_failure_preserves_user_message_and_final_answer.failed_rag

源码：[L38](D:/Project/learnLittle/tests/test_query_lifecycle.py:38)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

在抛检索异常前独立查消息数量，记录用户是否先提交。避免只看响应假设持久化顺序。

**输入与签名**

```python
async def failed_rag(question, owner, settings)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
factory
db.scalar
select
func.count
RuntimeError
```

<a id="fn-16239bf7c22c568a"></a>

## test_query_rag_failure_preserves_user_message_and_final_answer.fake_react

源码：[L43](D:/Project/learnLittle/tests/test_query_lifecycle.py:43)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

记录传入 history，依次发 draft、response_replace corrected、stream_done。测试服务端不能把新旧稿拼在一起。

**输入与签名**

```python
async def fake_react(question, owner, session_factory, settings, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'response', 'content': 'draft'}
yield {'type': 'response_replace', 'content': 'corrected'}
yield {'type': 'stream_done', 'full_response': 'corrected'}
```

<a id="fn-0d843eba4e120c98"></a>

## test_query_idempotency_replays_once_and_isolates_users

源码：[L63](D:/Project/learnLittle/tests/test_query_lifecycle.py:63)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

同用户同 key 重复只执行一次并重用助手 ID，正文冲突拒绝，其他用户同 key 可独立执行，跨会话归属拒绝。覆盖幂等范围而非工具通用 exactly-once。

**输入与签名**

```python
def test_query_idempotency_replays_once_and_isolates_users(client)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert first['assistant_message']['id'] == second['assistant_message']['id']
assert second['replayed'] is True
assert len(calls) == 1
assert conflict[-1]['type'] == 'error'
assert other_result['session_id'] != first['session_id']
assert len(calls) == 2
assert forbidden[-1]['type'] == 'error'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
auth
set_react_streamer
query
len
```

<a id="fn-e5ee2da787d5dd9f"></a>

## test_query_idempotency_replays_once_and_isolates_users.fake

源码：[L68](D:/Project/learnLittle/tests/test_query_lifecycle.py:68)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

每次被调用记录一次并 yield answer。调用次数直接反映是否错误重跑 Agent。

**输入与签名**

```python
async def fake(*args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'response', 'content': 'answer'}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
calls.append
```

<a id="fn-57d7814e37c7ff66"></a>

## test_inflight_duplicate_does_not_run_agent_twice

源码：[L88](D:/Project/learnLittle/tests/test_query_lifecycle.py:88)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

让首请求暂停在 Agent，期间提交重复 key，要求立即 error 且 Agent 一次、最终两条消息。检验在途不是等同已完成重放。

**输入与签名**

```python
def test_inflight_duplicate_does_not_run_agent_twice(client, monkeypatch)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
auth
asyncio.Event
set_react_streamer
client.portal.call
```

<a id="fn-9523fa13a78b6d7d"></a>

## test_inflight_duplicate_does_not_run_agent_twice.fake

源码：[L96](D:/Project/learnLittle/tests/test_query_lifecycle.py:96)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

设置 entered 事件并等待 release，制造首轮已接收未完成窗口。释放后才生成答案。

**输入与签名**

```python
async def fake(*args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'response', 'content': 'answer'}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
calls.append
entered.set
release.wait
```

<a id="fn-3bbfc3172ec72d80"></a>

## test_inflight_duplicate_does_not_run_agent_twice.run

源码：[L104](D:/Project/learnLittle/tests/test_query_lifecycle.py:104)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

并发启动首流、等待 entered、调用重复流，释放首轮后检查调用数及 SQL。运行于 TestClient portal 的异步环境。

**输入与签名**

```python
async def run()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert '"type": "error"' in duplicate[-1]
assert len(calls) == 1
assert await db.scalar(select(func.count(ChatMessage.id))) == 2
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
QueryRequest
asyncio.create_task
collect
asyncio.wait_for
entered.wait
release.set
len
factory
db.scalar
select
func.count
```

<a id="fn-a36d3f30890ce3d4"></a>

## test_inflight_duplicate_does_not_run_agent_twice.run.collect

源码：[L109](D:/Project/learnLittle/tests/test_query_lifecycle.py:109)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

完整消费相同 QueryRequest 的服务流并返回原始 SSE 帧列表。用于对比首轮与重复请求，不经过 HTTP 路由。

**输入与签名**

```python
async def collect()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [event async for event in query_service.stream_query(factory, user_id, data, config)]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
query_service.stream_query
```

<a id="fn-c0a8adb75b66bb6b"></a>

## test_full_sql_memory_is_not_limited_by_redis_window

源码：[L125](D:/Project/learnLittle/tests/test_query_lifecycle.py:125)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

预置 30 条 SQL 历史，下一轮捕获 Agent 输入并断言全部可见。验证新主链不先削成 Redis 热窗口。

**输入与签名**

```python
def test_full_sql_memory_is_not_limited_by_redis_window(client)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert events[-1]['type'] == 'done'
assert len(captured) == 30
assert captured[0]['content'] == 'message-0'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
auth
client.portal.call
set_react_streamer
query
len
```

<a id="fn-d9e14872691caa1e"></a>

## test_full_sql_memory_is_not_limited_by_redis_window.seed

源码：[L130](D:/Project/learnLittle/tests/test_query_lifecycle.py:130)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

建立会话和 30 条交错角色消息并 commit，返回 ID。准备的是 SQL 事实，不预填 Redis。

**输入与签名**

```python
async def seed()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return session.id
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
factory
ChatSession
db.add
db.flush
range
ChatMessage
db.commit
```

<a id="fn-778f4d4d0493119a"></a>

## test_full_sql_memory_is_not_limited_by_redis_window.fake

源码：[L141](D:/Project/learnLittle/tests/test_query_lifecycle.py:141)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

把 history 加入 captured 并返回简短答案。外层用此观察真实上下文选择。

**输入与签名**

```python
async def fake(*args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'response', 'content': 'answer'}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
captured.extend
```

<a id="fn-6d9b84b7660ed2ef"></a>

## test_slow_title_does_not_block_done_or_overwrite_manual_title

源码：[L153](D:/Project/learnLittle/tests/test_query_lifecycle.py:153)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

让自动标题等待，检查聊天先 done，再人工改名、释放自动任务，最终仍手动标题。验证后台延迟和条件 UPDATE 保护。

**输入与签名**

```python
def test_slow_title_does_not_block_done_or_overwrite_manual_title(client, monkeypatch)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert done['type'] == 'done'
assert result.status_code == 200
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
auth
asyncio.Event
monkeypatch.setattr
set_react_streamer
query
client.portal.call
client.put
```

<a id="fn-71274ee88ca8e162"></a>

## test_slow_title_does_not_block_done_or_overwrite_manual_title.slow_title

源码：[L159](D:/Project/learnLittle/tests/test_query_lifecycle.py:159)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

通知 started 后阻塞等待，释放才返回 automatic-title。可控制造模型慢于用户编辑的竞争。

**输入与签名**

```python
async def slow_title(question, settings)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 'automatic-title'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
started.set
release.wait
```

<a id="fn-969e1ba325bab439"></a>

## test_slow_title_does_not_block_done_or_overwrite_manual_title.fake

源码：[L164](D:/Project/learnLittle/tests/test_query_lifecycle.py:164)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

只输出 answer 让聊天快速结束，耗时放在标题假函数中。隔离标题与主生成的影响。

**输入与签名**

```python
async def fake(*args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'response', 'content': 'answer'}
```

<a id="fn-b9fed36b5d75331d"></a>

## test_slow_title_does_not_block_done_or_overwrite_manual_title.wait_started

源码：[L172](D:/Project/learnLittle/tests/test_query_lifecycle.py:172)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

限时等待标题任务确实开始。确保测试手动改名发生在读旧标题之后，而非靠随机 sleep。

**输入与签名**

```python
async def wait_started()
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.wait_for
started.wait
```

<a id="fn-e5c3e834a0dfaa03"></a>

## test_slow_title_does_not_block_done_or_overwrite_manual_title.finish

源码：[L181](D:/Project/learnLittle/tests/test_query_lifecycle.py:181)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

释放慢标题，drain 全部任务，再 SQL 断言 title/manual 都没被覆盖。验证最终事实不只看改名接口响应。

**输入与签名**

```python
async def finish()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert session.title == 'manual-title'
assert session.title_manual is True
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
release.set
drain_background_tasks
factory
db.get
```

<a id="fn-e0d9df23b8350ac9"></a>

## test_titles_update_in_early_rounds_only

源码：[L192](D:/Project/learnLittle/tests/test_query_lifecycle.py:192)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

以第二轮和第四轮状态调用标题维护，断言只前者触发生成。测试默认早期轮次数限制。

**输入与签名**

```python
def test_titles_update_in_early_rounds_only(client, monkeypatch)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
auth
monkeypatch.setattr
client.portal.call
```

<a id="fn-a0709ea6c0799512"></a>

## test_titles_update_in_early_rounds_only.title

源码：[L197](D:/Project/learnLittle/tests/test_query_lifecycle.py:197)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

记录生成问题并直接返回问题为标题。调用列表反映是否超过轮次仍调用模型。

**输入与签名**

```python
async def title(question, settings)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return question
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
called.append
```

<a id="fn-a7eae975f2a95435"></a>

## test_titles_update_in_early_rounds_only.run

源码：[L203](D:/Project/learnLittle/tests/test_query_lifecycle.py:203)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

造两条 user 消息、更新标题并核查，再加两条后再次尝试，检查没有第四轮调用。直接测后台 helper 而非完整 SSE。

**输入与签名**

```python
async def run()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert (await db.get(ChatSession, session_id)).title == 'second-round'
assert called == ['second-round']
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
factory
ChatSession
db.add
db.flush
range
ChatMessage
str
db.commit
query_service._update_title
db.get
```

<a id="fn-ccb87fc394b80ad7"></a>

## test_registration_requires_verified_email_by_default

源码：[L224](D:/Project/learnLittle/tests/test_query_lifecycle.py:224)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

恢复强制邮箱配置，断言缺邮箱/错 code 为 400，正确 fake code 成功。防止 fixture 的兼容注册掩盖默认规则。

**输入与签名**

```python
def test_registration_requires_verified_email_by_default(client, monkeypatch)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert response.status_code == 400
assert client.post('/api/v1/auth/register', json=payload).status_code == 400
assert client.post('/api/v1/auth/register', json=payload).status_code == 200
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.post
monkeypatch.setattr
```

<a id="fn-ea9db416d8dc531f"></a>

## test_registration_requires_verified_email_by_default.verify

源码：[L233](D:/Project/learnLittle/tests/test_query_lifecycle.py:233)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

只接受固定 123456，替代 Redis/SMTP 验证。用于路由必填与错误路径，不验证真实发信。

**输入与签名**

```python
async def verify(email, code)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return code == '123456'
```

<a id="fn-8a3fda62125f3540"></a>

## test_sse_token_single_use_and_not_profile_auth

源码：[L244](D:/Project/learnLittle/tests/test_query_lifecycle.py:244)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

检查 60 秒 JWT、资料接口拒绝 SSE 票、聊天首次成功第二次 401、Redis 条目缺失也拒绝。验证用途限制和单次消费。

**输入与签名**

```python
def test_sse_token_single_use_and_not_profile_auth(client)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert result['expires_in'] == 60
assert payload['exp'] - payload['iat'] == 60
assert client.get('/api/v1/user/me', headers=short).status_code == 401
assert query(client, short, message='hello')[-1]['type'] == 'done'
assert client.post('/api/v1/chat/query', headers=short, json={'message': 'hello'}).status_code == 401
assert client.post('/api/v1/chat/query', headers={'Authorization': f'Bearer {another}'}, json={'message': 'hello'}).status_code == 401
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
auth
client.post('/api/v1/auth/sse-token', headers=headers).json
client.post
decode_token
client.get
query
client.portal.call
```

<a id="fn-3eb2e1c720b46841"></a>

## test_sse_token_single_use_and_not_profile_auth.expire

源码：[L260](D:/Project/learnLittle/tests/test_query_lifecycle.py:260)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

直接删一次性票的 Redis jti 条目模拟失效。不是实际等待六十秒，也不改 JWT 签名。

**输入与签名**

```python
async def expire()
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().delete
get_redis
decode_token
```

<a id="fn-e9904a65d0c158e2"></a>

## test_chat_graph_cancellation_closes_model_stream

源码：[L269](D:/Project/learnLittle/tests/test_query_lifecycle.py:269)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

注入无限流，在首 response 后关闭图，断言下游 finally 执行。防止断流后模型生成器泄漏。

**输入与签名**

```python
async def test_chat_graph_cancellation_closes_model_stream()
```

装饰器/挂载：

```python
@pytest.mark.asyncio
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert closed == [True]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
set_react_streamer
stream_chat_graph
Settings
aclosing
```

<a id="fn-e606966f588b5739"></a>

## test_chat_graph_cancellation_closes_model_stream.endless

源码：[L274](D:/Project/learnLittle/tests/test_query_lifecycle.py:274)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

持续 yield chunk 并主动让出循环，finally 记录关闭。用于观察取消传播，不会访问真实 LLM。

**输入与签名**

```python
async def endless(*args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'response', 'content': 'chunk'}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.sleep
closed.append
```
