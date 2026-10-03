# tests/test_usage.py

[源码](D:/Project/learnLittle/tests/test_usage.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

## 本文件导航

- [_auth](#fn-13dcd5a6e699de65)
- [test_estimate_tokens_rounds_up](#fn-4037f51aacbd77f2)
- [test_usage_summary_empty](#fn-7b3b9aa071a1efea)
- [test_note_ai_records_usage](#fn-ec3df9ae82070225)
- [test_note_ai_records_usage.fake_complete](#fn-1b46eafb6cd78d80)
- [test_usage_isolated_by_user](#fn-a6b579312bd7fcef)
- [test_usage_isolated_by_user.fake_complete](#fn-f763b1cbd6fc5642)
- [test_usage_requires_auth](#fn-8d7dc20e5269390b)
<a id="fn-13dcd5a6e699de65"></a>

## _auth

源码：[L9](D:/Project/learnLittle/tests/test_usage.py:9)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

在测试 client 注册登录取得 access headers。为用量按用户归属的断言准备独立身份。

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

<a id="fn-4037f51aacbd77f2"></a>

## test_estimate_tokens_rounds_up

源码：[L17](D:/Project/learnLittle/tests/test_usage.py:17)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

断言空、偶数字符、奇数字符的估算为 0/1/2。验证 usage 估算而非 TokenCounter 的另一套 fallback。

**输入与签名**

```python
def test_estimate_tokens_rounds_up()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert estimate_tokens('') == 0
assert estimate_tokens('ab') == 1
assert estimate_tokens('abc') == 2
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
estimate_tokens
```

<a id="fn-7b3b9aa071a1efea"></a>

## test_usage_summary_empty

源码：[L23](D:/Project/learnLittle/tests/test_usage.py:23)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

新用户无调用时检查总数、Token、费用和分组均为空/零。不是把缺数据当 API 故障。

**输入与签名**

```python
def test_usage_summary_empty(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert resp.status_code == 200
assert data['total_calls'] == 0
assert data['total_tokens'] == 0
assert data['total_cost_cny'] == 0
assert data['by_stage'] == []
assert data['by_model'] == []
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_auth
client.get
resp.json
```

<a id="fn-ec3df9ae82070225"></a>

## test_note_ai_records_usage

源码：[L35](D:/Project/learnLittle/tests/test_usage.py:35)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

一次注入补全后查 summary，要求一条 note_ai 记录、输入输出正数及本地费用。验证计量链真实落测试 SQL。

**输入与签名**

```python
def test_note_ai_records_usage(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert resp.status_code == 200
assert summary['total_calls'] == 1
assert summary['total_prompt_tokens'] > 0
assert summary['total_completion_tokens'] > 0
assert summary['by_stage'][0]['stage'] == 'note_ai'
assert summary['total_cost_cny'] > 0
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
set_note_ai_fn
_auth
client.post
client.get('/api/v1/usage/summary', headers=header).json
client.get
```

<a id="fn-1b46eafb6cd78d80"></a>

## test_note_ai_records_usage.fake_complete

源码：[L36](D:/Project/learnLittle/tests/test_usage.py:36)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

返回固定非空补全，保证估算输出 Token 可观察。无供应商 usage，走文本估算。

**输入与签名**

```python
async def fake_complete(prompt: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '补全结果ABCD'
```

<a id="fn-a6b579312bd7fcef"></a>

## test_usage_isolated_by_user

源码：[L55](D:/Project/learnLittle/tests/test_usage.py:55)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

A 调一次补全后分别查 A/B，要求 A 一次 B 零次。防止聚合缺用户条件泄露用量。

**输入与签名**

```python
def test_usage_isolated_by_user(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert alice_data['total_calls'] == 1
assert bob_data['total_calls'] == 0
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
set_note_ai_fn
_auth
client.post
client.get('/api/v1/usage/summary', headers=alice).json
client.get
client.get('/api/v1/usage/summary', headers=bob).json
```

<a id="fn-f763b1cbd6fc5642"></a>

## test_usage_isolated_by_user.fake_complete

源码：[L56](D:/Project/learnLittle/tests/test_usage.py:56)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

返回 ok 的稳定补全，触发 A 的计量。没有真实模型调用成本。

**输入与签名**

```python
async def fake_complete(prompt: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 'ok'
```

<a id="fn-8d7dc20e5269390b"></a>

## test_usage_requires_auth

源码：[L73](D:/Project/learnLittle/tests/test_usage.py:73)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

不带 Token 请求 summary 要求 401。保证用量不是公开统计接口。

**输入与签名**

```python
def test_usage_requires_auth(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert resp.status_code == 401
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.get
```
