# app/services/query_service.py

[源码](D:/Project/learnLittle/app/services/query_service.py) | [任务流程 06](D:/Project/learnLittle/docs/backend-tutorial/06-query.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

用户先提交、并行上下文、图执行、助手提交和后台维护的主编排。

## 本文件导航

- [_sse_data](#fn-1625c94e2ce7df7a)
- [compose_answer](#fn-10a1684f3425d594)
- [_key](#fn-31ca38cc1c75bb7d)
- [_load_memory](#fn-42601906661b7e9d)
- [_retrieve](#fn-173e3f0d4288efea)
- [_update_title](#fn-d4bc3adb0e485d3f)
- [_summarize](#fn-f6b8f9c690822056)
- [stream_query](#fn-70fa6bd14343edb2)
- [stream_query.<lambda@241:12>](#fn-6d7f1d0a8db00fee)
- [stream_query.<lambda@245:12>](#fn-12f5015f8d2ba14b)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)
```

<a id="fn-1625c94e2ce7df7a"></a>

## _sse_data

源码：[L35](D:/Project/learnLittle/app/services/query_service.py:35)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

把包含 type 的 payload 编成 data: JSON 帧，供当前聊天使用。事件类别在 JSON 内，而不是单独的 event 行；这里只编码，不保存消息。

**输入与签名**

```python
def _sse_data(payload: dict) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'data: {json.dumps(payload, ensure_ascii=False)}\n\n'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
json.dumps
```

<a id="fn-10a1684f3425d594"></a>

## compose_answer

源码：[L39](D:/Project/learnLittle/app/services/query_service.py:39)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

生成无模型时的本地降级回答，分别处理跳过检索、检索无结果、知识库或笔记命中。保留资料编号和来源，不宣称整个项目没有模型能力。

**输入与签名**

```python
def compose_answer(question: str, hits: list[dict], *, used_retrieval: bool=True) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'「{question}」看起来和你已有的知识库、笔记不太相关，这一轮没有检索资料。如果问的是文档里的内容，试着换更具体的关键词；闲聊的话可以直接继续。'
return '知识库和笔记里都没有检索到相关内容。请先上传文档或写笔记，或换一个更具体的问题。'
return '\n'.join(lines).strip()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
enumerate
hit.get
lines.extend
(hit.get('content') or '').strip
lines.append
'\n'.join(lines).strip
'\n'.join
```

<a id="fn-31ca38cc1c75bb7d"></a>

## _key

源码：[L64](D:/Project/learnLittle/app/services/query_service.py:64)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

空幂等 key 返回 None，否则哈希 user_id、角色和客户端 key。保证两用户及 user/assistant 的消息键分开，但不包含 session_id。

**输入与签名**

```python
def _key(user_id, key, role)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
return hashlib.sha256(f'{user_id}:{role}:{key}'.encode()).hexdigest()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
hashlib.sha256(f'{user_id}:{role}:{key}'.encode()).hexdigest
hashlib.sha256
f'{user_id}:{role}:{key}'.encode
```

<a id="fn-42601906661b7e9d"></a>

## _load_memory

源码：[L70](D:/Project/learnLittle/app/services/query_service.py:70)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

用独立 SQL session 查当前消息 ID 之前的本会话全量消息，连同摘要文字和覆盖到的 ID 返回。新链不先用 Redis 热窗口截断。

**输入与签名**

```python
async def _load_memory(factory, session_id, before_id)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return (rows, summary.summary_text if summary else '', summary.last_message_id if summary else 0)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
factory
list
(await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id, ChatMessage.id < before_id).order_by(ChatMessage.id))).scalars().all
(await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id, ChatMessage.id < before_id).order_by(ChatMessage.id))).scalars
db.execute
select(ChatMessage).where(ChatMessage.session_id == session_id, ChatMessage.id < before_id).order_by
select(ChatMessage).where
select
get_summary
```

<a id="fn-173e3f0d4288efea"></a>

## _retrieve

源码：[L81](D:/Project/learnLittle/app/services/query_service.py:81)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

给 RAG 总流程套超时：门控、可选聊天 HyDE、双源检索、摘要；返回原 hits/提示副本/决策。普通错误或超时记录日志并返回 unavailable，不阻断后续 Agent。

**输入与签名**

```python
async def _retrieve(question, user_id, top_k, settings)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ([], [], decision)
return (hits, context, decision)
return ([], [], RouteDecision(False, float('inf'), 'unavailable'))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.timeout
decide_retrieval
generate_hyde
get_vector_store().search_both
get_vector_store
summarize_hits
logger.warning
RouteDecision
float
```

<a id="fn-d4bc3adb0e485d3f"></a>

## _update_title

源码：[L96](D:/Project/learnLittle/app/services/query_service.py:96)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

读会话手动标记和用户轮次数，早期轮次才生成标题，再用非手动且旧标题相等的条件 UPDATE 提交。模型等待期间不占同一个会话对象，防止慢模型覆盖人工改名。

**输入与签名**

```python
async def _update_title(factory, session_id, question, settings)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
factory
db.get
db.scalar
select(func.count(ChatMessage.id)).where
select
func.count
generate_session_title
db.execute
update(ChatSession).where(ChatSession.id == session_id, ChatSession.title_manual.is_(False), ChatSession.title == previous_title).values
update(ChatSession).where
update
ChatSession.title_manual.is_
db.commit
invalidate_session_list
```

<a id="fn-f6b8f9c690822056"></a>

## _summarize

源码：[L119](D:/Project/learnLittle/app/services/query_service.py:119)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

新建 SQL session，调用里程碑摘要检查并 commit。由后台任务执行，不让 done 等它完成。

**输入与签名**

```python
async def _summarize(factory, session_id, settings)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
factory
check_and_summarize
db.commit
```

<a id="fn-70fa6bd14343edb2"></a>

## stream_query

源码：[L125](D:/Project/learnLittle/app/services/query_service.py:125)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

当前聊天总编排：SSE 槽、防重、用户先提交、并行 RAG/SQL 历史、预算、图执行、事件追加/替换、助手提交、后台维护后 done。error 终止不写假成功回答，finally 清 trace/释放槽；副作用不在一个总 SQL 事务里。

**输入与签名**

```python
async def stream_query(factory, user_id, data, settings)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield _sse_data({'type': 'error', 'content': '并发连接数已达上限，请稍后重试'})
return None
yield _sse_data({'type': 'error', 'content': '同一幂等键不能用于不同请求'})
yield _sse_data({'type': 'meta', 'session_id': session.id, 'user_message': _message_dump(existing)})
yield _sse_data({'type': 'response_replace', 'content': reply.content})
yield _sse_data({'type': 'done', 'session_id': session.id, 'answer': reply.content, 'title': session.title, 'assistant_message': _message_dump(reply), 'replayed': True})
yield _sse_data({'type': 'error', 'content': '该请求已接收，请查看会话；为避免重复操作不会自动重放'})
yield _sse_data({'type': 'meta', 'session_id': session_id, 'user_message': user_dump})
```

另有 8 个出口/断言，完整条件见源码。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
acquire_sse_slot
_sse_data
data.message.strip
visible_question
_key
settings.model_copy
factory
db.scalar
select(ChatMessage).where
select
get_session
_message_dump
create_session
_add_message
db.commit
push_message
invalidate_session_list
usage_service.set_trace_context
asyncio.gather
_retrieve
_load_memory
rag_context_text
build_agent_history
len
resolve_agent_thinking
bool
thinking.sse_notice
stream_chat_graph
compose_answer
aclosing
event.get
event.items
parts.append
tools.append
''.join
answer.strip
spawn_background_task
get_react_streamer
routing.get
item.get
logger.exception
usage_service.clear_trace_context
release_sse_slot
```

<a id="fn-6d7f1d0a8db00fee"></a>

## stream_query.<lambda@241:12>

源码：[L241](D:/Project/learnLittle/app/services/query_service.py:241)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

捕获当前 factory/session/question/settings，返回标题协程供后台 task runner 稍后 await。创建 lambda 时尚未调用模型。

**输入与签名**

```python
lambda: _update_title(factory, session_id, question, settings)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 _update_title(factory, session_id, question, settings)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_update_title
```

<a id="fn-12f5015f8d2ba14b"></a>

## stream_query.<lambda@245:12>

源码：[L245](D:/Project/learnLittle/app/services/query_service.py:245)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

捕获会话与配置，返回摘要维护协程供后台按 session key 串行。助手提交后登记，不让 done 等压缩完成。

**输入与签名**

```python
lambda: _summarize(factory, session_id, settings)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 _summarize(factory, session_id, settings)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_summarize
```
