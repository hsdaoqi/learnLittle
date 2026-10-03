# tests/test_chat_routes.py

[源码](D:/Project/learnLittle/tests/test_chat_routes.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

## 本文件导航

- [auth](#fn-01a16a02d2d7ab3d)
- [query](#fn-e9d9afef8136d5e2)
- [test_chat_routes_have_one_query_entry](#fn-e9fa451329b87f4f)
- [test_chat_router_calls_query_service_directly](#fn-c971a67eb0af2032)
- [test_chat_router_calls_query_service_directly.fake](#fn-4bb441596fb8ef61)
- [test_query_preserves_session_crud_and_user_isolation](#fn-8fbe807e8698873e)
- [test_query_preserves_session_crud_and_user_isolation.fake](#fn-4b9898a0ba2178c8)
- [test_local_fallback_preserves_sources_and_does_not_claim_no_llm](#fn-cfaa38e14f370b73)
- [test_query_without_model_still_executes_local_tool](#fn-d0397c1078f8798a)
- [test_auxiliary_completion_still_records_provider_usage](#fn-2c950f0759ad3cd5)
- [test_auxiliary_completion_still_records_provider_usage.fake_post](#fn-616d7f3bc0539b62)
- [test_auxiliary_completion_still_records_provider_usage.complete](#fn-0b9965e2f105b5b2)
<a id="fn-01a16a02d2d7ab3d"></a>

## auth

源码：[L7](D:/Project/learnLittle/tests/test_chat_routes.py:7)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

通过测试 client 注册并登录，返回 access headers 和用户 ID。给聊天归属及实际用量写库测试准备身份，不连接正式账号服务。

**输入与签名**

```python
def auth(client, name)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert result.status_code == 200
return ({'Authorization': f'Bearer {token}'}, result.json()['data']['user_id'])
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.post
client.post('/api/v1/auth/login', json={'username': name, 'password': 'passw0rd123'}).json
result.json
```

<a id="fn-e9d9afef8136d5e2"></a>

## query

源码：[L18](D:/Project/learnLittle/tests/test_chat_routes.py:18)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

向唯一聊天入口发送请求，确认 SSE 类型后把 data JSON 帧转成事件列表。供测试断言最终消息和工具事件，不执行额外模型调用。

**输入与签名**

```python
def query(client, headers, **payload)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert response.status_code == 200
assert response.headers['content-type'].startswith('text/event-stream')
return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith('data: ')]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.post
response.headers['content-type'].startswith
json.loads
response.text.splitlines
line.startswith
```

<a id="fn-e9fa451329b87f4f"></a>

## test_chat_routes_have_one_query_entry

源码：[L28](D:/Project/learnLittle/tests/test_chat_routes.py:28)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

核对 OpenAPI 仅保留 query 与会话管理；旧 ask/stream 返回 404，chat_service 不再有独立问答函数。防止重复入口被重新接入。

**输入与签名**

```python
def test_chat_routes_have_one_query_entry(client)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert chat_paths == {'/api/v1/chat/query', '/api/v1/chat/sessions', '/api/v1/chat/sessions/{session_id}/title', '/api/v1/chat/sessions/{session_id}', '/api/v1/chat/sessions/{session_id}/messages'}
assert response.status_code == 404
assert not hasattr(chat_service, name)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.app.openapi
path.startswith
auth
client.post
hasattr
```

<a id="fn-c971a67eb0af2032"></a>

## test_chat_router_calls_query_service_directly

源码：[L48](D:/Project/learnLittle/tests/test_chat_routes.py:48)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

替换 query_service 流并验证 router 原样传工厂、用户、消息、配置。确认主链不再绕 chat_service 兼容包装。

**输入与签名**

```python
def test_chat_router_calls_query_service_directly(client, monkeypatch)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert events[-1] == {'type': 'done', 'answer': 'answer'}
assert captured == {'factory': client.app.state.db_session_factory, 'owner': user_id, 'message': 'hello', 'settings': client.app.state.settings}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
auth
monkeypatch.setattr
query
```

<a id="fn-4bb441596fb8ef61"></a>

## test_chat_router_calls_query_service_directly.fake

源码：[L52](D:/Project/learnLittle/tests/test_chat_routes.py:52)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

捕获路由传入参数，输出固定 response/done 帧。只替换问答编排，不替换认证依赖，因而仍验证用户归属传递。

**输入与签名**

```python
async def fake(factory, owner, data, settings)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield 'data: {"type": "response", "content": "answer"}\n\n'
yield 'data: {"type": "done", "answer": "answer"}\n\n'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
captured.update
```

<a id="fn-8fbe807e8698873e"></a>

## test_query_preserves_session_crud_and_user_isolation

源码：[L70](D:/Project/learnLittle/tests/test_chat_routes.py:70)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

通过注入回答创建会话，验证列表、完整消息、手动标题、删除及其他用户的 404。清理旧入口不能破坏会话产品功能。

**输入与签名**

```python
def test_query_preserves_session_crud_and_user_isolation(client)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert done['type'] == 'done'
assert [session['id'] for session in sessions] == [session_id]
assert client.get('/api/v1/chat/sessions', headers=other).json()['data'] == []
assert [item['content'] for item in messages] == ['hello', 'answer']
assert client.get(f'{base}/messages', headers=other).status_code == 404
assert client.put(f'{base}/title', headers=other, json={'title': 'bad'}).status_code == 404
assert client.delete(base, headers=other).status_code == 404
assert renamed.status_code == 200
```

另有 5 个出口/断言，完整条件见源码。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
auth
set_react_streamer
query
client.get('/api/v1/chat/sessions', headers=headers).json
client.get
client.get('/api/v1/chat/sessions', headers=other).json
client.get(f'{base}/messages', headers=headers).json
client.put
client.delete
renamed.json
```

<a id="fn-4b9898a0ba2178c8"></a>

## test_query_preserves_session_crud_and_user_isolation.fake

源码：[L74](D:/Project/learnLittle/tests/test_chat_routes.py:74)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

输出固定 answer 事件，避免外部模型。会话创建与消息提交仍由真实 query_service 执行。

**输入与签名**

```python
async def fake(*args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'response', 'content': 'answer'}
```

<a id="fn-cfaa38e14f370b73"></a>

## test_local_fallback_preserves_sources_and_does_not_claim_no_llm

源码：[L102](D:/Project/learnLittle/tests/test_chat_routes.py:102)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

检查本地摘录保留来源、无检索与无命中文案不同，并验证中文 SSE JSON。避免遗留文案误称全项目未接模型。

**输入与签名**

```python
def test_local_fallback_preserves_sources_and_does_not_claim_no_llm()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert '[1] [笔记] title' in answer
assert 'body' in answer
assert '尚未接入大模型' not in answer
assert '没有检索资料' in query_service.compose_answer('hello', [], used_retrieval=False)
assert '没有检索到' in query_service.compose_answer('hello', [])
assert json.loads(event.removeprefix('data: '))['content'] == '中文'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
query_service.compose_answer
query_service._sse_data
json.loads
event.removeprefix
```

<a id="fn-d0397c1078f8798a"></a>

## test_query_without_model_still_executes_local_tool

源码：[L115](D:/Project/learnLittle/tests/test_chat_routes.py:115)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

无模型密钥时真实调用时间工具，核对 start/end/done 的结果一致且无模型用量。删除旧 HTTP 工具循环不能破坏本地降级。

**输入与签名**

```python
def test_query_without_model_still_executes_local_tool(client)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert starts == [{'type': 'tool_start', 'name': 'what_time_is_now'}]
assert ends[0]['name'] == 'what_time_is_now'
assert not ends[0].get('error')
assert events[-1]['type'] == 'done'
assert events[-1]['answer'] == ends[0]['result']
assert summary['total_calls'] == 0
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
auth
query
ends[0].get
client.get('/api/v1/usage/summary', headers=headers).json
client.get
```

<a id="fn-2c950f0759ad3cd5"></a>

## test_auxiliary_completion_still_records_provider_usage

源码：[L129](D:/Project/learnLittle/tests/test_chat_routes.py:129)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

用假的 HTTP 响应驱动真实辅助补全及用量落库，再从 summary 核对官方输入13、输出2及 title 阶段。确认移除旧流客户端没有影响非流补全。

**输入与签名**

```python
def test_auxiliary_completion_still_records_provider_usage(client, monkeypatch)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert client.portal.call(complete) == 'title'
assert summary['total_calls'] == 1
assert summary['total_prompt_tokens'] == 13
assert summary['total_completion_tokens'] == 2
assert summary['total_tokens'] == 15
assert summary['by_stage'] == [{'stage': 'title', 'calls': 1, 'prompt_tokens': 13, 'completion_tokens': 2}]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
auth
monkeypatch.setattr
client.portal.call
client.get('/api/v1/usage/summary', headers=headers).json
client.get
```

<a id="fn-616d7f3bc0539b62"></a>

## test_auxiliary_completion_still_records_provider_usage.fake_post

源码：[L137](D:/Project/learnLittle/tests/test_chat_routes.py:137)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

检查辅助调用走非流式 chat/completions，返回含官方 usage 的固定响应。只替换 HTTP post，不跳过计时器、解析或真实数据库提交。

**输入与签名**

```python
async def fake_post(self, url, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert url.endswith('/chat/completions')
assert kwargs['json']['stream'] is False
return httpx.Response(200, json={'choices': [{'message': {'content': 'title'}}], 'usage': {'prompt_tokens': 13, 'completion_tokens': 2, 'total_tokens': 15}})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
url.endswith
httpx.Response
```

<a id="fn-0b9965e2f105b5b2"></a>

## test_auxiliary_completion_still_records_provider_usage.complete

源码：[L147](D:/Project/learnLittle/tests/test_chat_routes.py:147)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

设置测试用户与 title 归属，调用真实补全并在 finally 清上下文。通过 client 的异步执行环境运行，避免正式模型请求。

**输入与签名**

```python
async def complete()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await complete_openai_compatible('prompt', client.app.state.settings)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
usage_service.set_trace_context
complete_openai_compatible
usage_service.clear_trace_context
```
