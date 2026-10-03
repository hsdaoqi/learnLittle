# tests/test_thinking.py

[源码](D:/Project/learnLittle/tests/test_thinking.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

## 本文件导航

- [_settings](#fn-9bf1cb209d3f7286)
- [_auth](#fn-d0fde36ca4d8fbde)
- [_read_sse](#fn-c4c23ca859000efa)
- [test_resolve_agent_thinking_plain_on_off](#fn-96c2a6bf62b67452)
- [test_resolve_agent_thinking_attachment_mutex](#fn-e43caf61212b9c98)
- [test_complete_roles_default_off_and_independent](#fn-a2e7c7f7700dfbf8)
- [test_agent_timeout_doubles_when_thinking](#fn-0647dae48917a1f1)
- [test_thinking_protocol_auto_dashscope_vs_openai_gateway](#fn-7fe7cc59013cde19)
- [test_thinking_protocol_forced_none_even_on_dashscope](#fn-a6ba947120d39a3a)
- [test_resolve_agent_thinking_unsupported_on_gpt_gateway](#fn-b5e56bef925dc84f)
- [test_query_thinking_applied_without_attachments](#fn-5fc026348147a90c)
- [test_query_thinking_applied_without_attachments.fake_react](#fn-30555ed38309a14f)
- [test_query_thinking_disabled_when_attachment_ids](#fn-a9144090dc34f164)
- [test_query_thinking_disabled_when_attachment_ids.fake_react](#fn-92d9d9f65866e58b)
- [test_query_thinking_skipped_when_protocol_none](#fn-cc4a27bd77481e82)
- [test_query_thinking_skipped_when_protocol_none.fake_react](#fn-72c0a39d6d517ba3)
<a id="fn-9bf1cb209d3f7286"></a>

## _settings

源码：[L21](D:/Project/learnLittle/tests/test_thinking.py:21)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

构造测试 Settings 默认无 key/60 秒超时，允许覆盖。真实 .env 由 autouse fixture 屏蔽。

**输入与签名**

```python
def _settings(**kwargs) -> Settings
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return Settings(**defaults)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
defaults.update
Settings
```

<a id="fn-d0fde36ca4d8fbde"></a>

## _auth

源码：[L27](D:/Project/learnLittle/tests/test_thinking.py:27)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

隔离 client 注册登录返回 access headers。只为测试准备身份，不测试完整邮箱发送。

**输入与签名**

```python
def _auth(client: TestClient, username: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'Authorization': f'Bearer {tokens['access_token']}'}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.post
client.post('/api/v1/auth/login', json={'username': username, 'password': 'passw0rd123'}).json
```

<a id="fn-c4c23ca859000efa"></a>

## _read_sse

源码：[L35](D:/Project/learnLittle/tests/test_thinking.py:35)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

用 TestClient 消费主聊天流并合并 bytes/str 成正文，先断言 HTTP 200。具体事件语义由各用例检查。

**输入与签名**

```python
def _read_sse(client: TestClient, headers: dict, payload: dict) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert resp.status_code == 200
return ''.join((chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk for chunk in resp.iter_text()))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.stream
''.join
isinstance
chunk.decode
resp.iter_text
```

<a id="fn-96c2a6bf62b67452"></a>

## test_resolve_agent_thinking_plain_on_off

源码：[L44](D:/Project/learnLittle/tests/test_thinking.py:44)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

验证无附件基本开关、applied/reason 和无需 notice。只测纯决策函数。

**输入与签名**

```python
def test_resolve_agent_thinking_plain_on_off()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert off.applied is False
assert off.reason == 'off'
assert off.sse_notice() is None
assert on.applied is True
assert on.reason == 'agent'
assert on.sse_notice() is None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
resolve_agent_thinking
off.sse_notice
on.sse_notice
```

<a id="fn-e43caf61212b9c98"></a>

## test_resolve_agent_thinking_attachment_mutex

源码：[L56](D:/Project/learnLittle/tests/test_thinking.py:56)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

验证附件即关闭、用户请求思考才发附件提示。没有测试图片理解功能。

**输入与签名**

```python
def test_resolve_agent_thinking_attachment_mutex()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert decision.requested is True
assert decision.applied is False
assert decision.reason == 'attachment'
assert notice is not None
assert notice['stage'] == 'attachment'
assert ATTACHMENT_THINKING_NOTICE in notice['content']
assert ignored.sse_notice() is None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
resolve_agent_thinking
decision.sse_notice
ignored.sse_notice
```

<a id="fn-a2e7c7f7700dfbf8"></a>

## test_complete_roles_default_off_and_independent

源码：[L70](D:/Project/learnLittle/tests/test_thinking.py:70)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

验证三个辅助角色默认关、分别打开生效以及 DashScope extra_body。避免把请求主开关套给全部模型。

**输入与签名**

```python
def test_complete_roles_default_off_and_independent()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert thinking_protocol(settings) == 'dashscope'
assert complete_thinking_for('classifier', settings) is False
assert complete_thinking_for('plan', settings) is False
assert complete_thinking_for('reflection', settings) is False
assert complete_thinking_for('agent', settings) is False
assert complete_thinking_for('classifier', settings) is True
assert complete_thinking_for('plan', settings) is True
assert complete_thinking_for('reflection', settings) is True
```

另有 2 个出口/断言，完整条件见源码。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_settings
thinking_protocol
complete_thinking_for
extra_body
```

<a id="fn-0647dae48917a1f1"></a>

## test_agent_timeout_doubles_when_thinking

源码：[L90](D:/Project/learnLittle/tests/test_thinking.py:90)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

比较默认/显式超时在思考开关下倍增。测试纯数值策略，不等待真实超时。

**输入与签名**

```python
def test_agent_timeout_doubles_when_thinking()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert agent_timeout(settings, False) == 60
assert agent_timeout(settings, True) == 120
assert agent_timeout(settings, True, timeout=40) == 80
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_settings
agent_timeout
```

<a id="fn-7fe7cc59013cde19"></a>

## test_thinking_protocol_auto_dashscope_vs_openai_gateway

源码：[L97](D:/Project/learnLittle/tests/test_thinking.py:97)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

比较不同配置 URL，要求普通兼容网关不带扩展，角色开关也受协议约束。只是本地协议判断，不访问这些地址。

**输入与签名**

```python
def test_thinking_protocol_auto_dashscope_vs_openai_gateway()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert thinking_protocol(dash) == 'dashscope'
assert thinking_protocol(gpt) == 'none'
assert extra_body(True, gpt) is None
assert payload_thinking_fields(True, gpt) == {}
assert payload_thinking_fields(False, dash) == {'enable_thinking': False}
assert complete_thinking_for('classifier', _settings(llm_base_url='https://sub.advanced.ccwu.cc/v1', classifier_enable_thinking=True)) is False
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_settings
thinking_protocol
extra_body
payload_thinking_fields
complete_thinking_for
```

<a id="fn-a6ba947120d39a3a"></a>

## test_thinking_protocol_forced_none_even_on_dashscope

源码：[L111](D:/Project/learnLittle/tests/test_thinking.py:111)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

显式 none 必须覆盖域名自动识别。便于部署禁用不支持的扩展行为。

**输入与签名**

```python
def test_thinking_protocol_forced_none_even_on_dashscope()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert thinking_protocol(settings) == 'none'
assert extra_body(True, settings) is None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_settings
thinking_protocol
extra_body
```

<a id="fn-b5e56bef925dc84f"></a>

## test_resolve_agent_thinking_unsupported_on_gpt_gateway

源码：[L120](D:/Project/learnLittle/tests/test_thinking.py:120)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

请求为 true 但协议不支持时 applied=false 且有说明。requested 与 applied 应当分别保留。

**输入与签名**

```python
def test_resolve_agent_thinking_unsupported_on_gpt_gateway()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert decision.requested is True
assert decision.applied is False
assert decision.reason == 'unsupported'
assert notice is not None
assert notice['stage'] == 'unsupported'
assert UNSUPPORTED_THINKING_NOTICE in notice['content']
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_settings
resolve_agent_thinking
decision.sse_notice
```

<a id="fn-5fc026348147a90c"></a>

## test_query_thinking_applied_without_attachments

源码：[L132](D:/Project/learnLittle/tests/test_thinking.py:132)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

通过主接口捕获 ReAct 参数与 done 字段，断言普通支持场景应用思考。fake 代替真实模型。

**输入与签名**

```python
def test_query_thinking_applied_without_attachments(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert captured.get('enable_thinking') is True
assert ATTACHMENT_THINKING_NOTICE not in body
assert '"enable_thinking": true' in body or '"enable_thinking":true' in body
assert '"thinking_reason": "agent"' in body or '"thinking_reason":"agent"' in body
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
set_react_streamer
_auth
_read_sse
captured.get
```

<a id="fn-30555ed38309a14f"></a>

## test_query_thinking_applied_without_attachments.fake_react

源码：[L135](D:/Project/learnLittle/tests/test_thinking.py:135)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

记录 enable_thinking，输出固定思考答案与 stream_done。让接口测试只关心开关传递。

**输入与签名**

```python
async def fake_react(question, user_id, session_factory, settings, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'response', 'content': '思考后的答案'}
yield {'type': 'stream_done', 'full_response': '思考后的答案'}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
kwargs.get
```

<a id="fn-a9144090dc34f164"></a>

## test_query_thinking_disabled_when_attachment_ids

源码：[L157](D:/Project/learnLittle/tests/test_thinking.py:157)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

主请求含附件 ID 时断言 ReAct 接到 false，流含附件说明和 requested=true。不是多模态测试。

**输入与签名**

```python
def test_query_thinking_disabled_when_attachment_ids(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert captured.get('enable_thinking') is False
assert ATTACHMENT_THINKING_NOTICE in body
assert '"stage": "attachment"' in body or '"stage":"attachment"' in body
assert '"enable_thinking": false' in body or '"enable_thinking":false' in body
assert '"thinking_reason": "attachment"' in body or '"thinking_reason":"attachment"' in body
assert '"thinking_requested": true' in body or '"thinking_requested":true' in body
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
set_react_streamer
_auth
_read_sse
captured.get
```

<a id="fn-92d9d9f65866e58b"></a>

## test_query_thinking_disabled_when_attachment_ids.fake_react

源码：[L160](D:/Project/learnLittle/tests/test_thinking.py:160)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

记录应用开关并返回固定看图文案。文案是测试替身，不能作为已实现视觉模型的证据。

**输入与签名**

```python
async def fake_react(question, user_id, session_factory, settings, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'response', 'content': '看图回答'}
yield {'type': 'stream_done', 'full_response': '看图回答'}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
kwargs.get
```

<a id="fn-cc4a27bd77481e82"></a>

## test_query_thinking_skipped_when_protocol_none

源码：[L188](D:/Project/learnLittle/tests/test_thinking.py:188)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

改 app settings 为普通网关后请求思考，断言普通模式及 unsupported 提示。验证路由使用当前 app 配置。

**输入与签名**

```python
def test_query_thinking_skipped_when_protocol_none(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert captured.get('enable_thinking') is False
assert UNSUPPORTED_THINKING_NOTICE in body
assert '"thinking_reason": "unsupported"' in body or '"thinking_reason":"unsupported"' in body
assert '"enable_thinking": false' in body or '"enable_thinking":false' in body
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
set_react_streamer
_auth
client.app.state.settings.model_copy
_read_sse
captured.get
```

<a id="fn-72c0a39d6d517ba3"></a>

## test_query_thinking_skipped_when_protocol_none.fake_react

源码：[L191](D:/Project/learnLittle/tests/test_thinking.py:191)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

捕获开关并输出普通回答。用来断言 unsupported 情况未把 true 误传下去。

**输入与签名**

```python
async def fake_react(question, user_id, session_factory, settings, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'response', 'content': '普通回答'}
yield {'type': 'stream_done', 'full_response': '普通回答'}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
kwargs.get
```
