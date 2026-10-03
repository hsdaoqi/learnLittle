# app/ai_service/react_agent.py

[源码](D:/Project/learnLittle/app/ai_service/react_agent.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

真实 LangChain 工具循环、事件协议、工具重试护栏和答案反思。

## 本文件导航

- [set_react_streamer](#fn-01c3fbad004f985d)
- [get_react_streamer](#fn-2a84db94ecf8573f)
- [build_react_system_prompt](#fn-a29bf6fd3147a019)
- [chunk_text](#fn-1e73bfbca392153c)
- [chunk_reasoning](#fn-aefff028f5362bcd)
- [map_langchain_event](#fn-8ebbbab66297447e)
- [_create_chat_model](#fn-d57321ce6a10aeff)
- [_create_agent](#fn-83a5c96e1d4d6668)
- [_history_messages](#fn-be53e78cc1d24a96)
- [run_langchain_react](#fn-dbb853a64eb632ed)
- [run_react](#fn-6e1b44ad15aec546)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

ReactStreamer = Callable[..., AsyncIterator[dict[str, Any]]]

_injected: ReactStreamer | None = None

DEFAULT_SYSTEM_PROMPT = '你是学习助手。需要查笔记、统计、回顾或当前用户信息时调用工具。工具结果用简洁中文回答用户。不要编造 note_id / review_id。当 search_notes_tool 返回编号列表时，把「找到 N 篇…」和每条「N. 标题 (ID: xxx) - 摘要」原样交给用户，不要丢掉 ID。有检索资料时优先依据资料回答；资料不够就明说，不要编造文档内容。'

MAX_CONSECUTIVE_TOOL_CALLS = 6
```

<a id="fn-01c3fbad004f985d"></a>

## set_react_streamer

源码：[L34](D:/Project/learnLittle/app/ai_service/react_agent.py:34)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

替换ReAct 事件流的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_react_streamer(fn: ReactStreamer | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-2a84db94ecf8573f"></a>

## get_react_streamer

源码：[L39](D:/Project/learnLittle/app/ai_service/react_agent.py:39)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

返回ReAct 事件流当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_react_streamer() -> ReactStreamer | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-a29bf6fd3147a019"></a>

## build_react_system_prompt

源码：[L43](D:/Project/learnLittle/app/ai_service/react_agent.py:43)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

拼学习助手规则、额外步骤说明、RAG reference 与用户引用笔记。纯构造，不执行资料检索或鉴权。

**输入与签名**

```python
def build_react_system_prompt(message: str, *, rag_context: str='', extra_system: str='') -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '\n\n'.join(parts)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(extra_system or '').strip
parts.append
(rag_context or '').strip
referenced_notes_prompt
'\n\n'.join
```

<a id="fn-1e73bfbca392153c"></a>

## chunk_text

源码：[L65](D:/Project/learnLittle/app/ai_service/react_agent.py:65)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

兼容字符串 content 和文本块列表，只提取正文文本。忽略不是 text 的结构化片段。

**输入与签名**

```python
def chunk_text(chunk: Any) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return content
return ''.join(parts)
return ''
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
getattr
isinstance
parts.append
item.get
''.join
```

<a id="fn-aefff028f5362bcd"></a>

## chunk_reasoning

源码：[L80](D:/Project/learnLittle/app/ai_service/react_agent.py:80)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

从 additional_kwargs 等支持字段抽 reasoning 文本。提取不到返回空，不自行推测模型推理。

**输入与签名**

```python
def chunk_reasoning(chunk: Any) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return str(text)
return str(getattr(chunk, 'reasoning_content', '') or '')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
getattr
isinstance
extra.get
str
```

<a id="fn-8ebbbab66297447e"></a>

## map_langchain_event

源码：[L89](D:/Project/learnLittle/app/ai_service/react_agent.py:89)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

将模型/工具 v2 事件转 thinking/response/tool_start/tool_end，跟踪连续工具计数和耗时。超过六次仍先产 tool_start 再 error，使上层不会漏记可能写操作。

**输入与签名**

```python
def map_langchain_event(event: dict[str, Any], *, consecutive_tool_calls: int, tool_start_times: dict[str, float], now: float | None=None) -> tuple[list[dict[str, Any]], int]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return (produced, consecutive_tool_calls)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
event.get
time.time
(event.get('data') or {}).get
chunk_reasoning
produced.append
chunk_text
tool_start_times.pop
round
getattr
str
```

<a id="fn-d57321ce6a10aeff"></a>

## _create_chat_model

源码：[L165](D:/Project/learnLittle/app/ai_service/react_agent.py:165)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

构造流式 ChatOpenAI，启用 usage callback、超时且 SDK max_retries=0；仅支持协议才附 extra_body。不会把所有兼容网关都强行传 enable_thinking。

**输入与签名**

```python
def _create_chat_model(settings: Settings, *, enable_thinking: bool, timeout: int)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ChatOpenAI(**kwargs)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
ModelUsageCallback
(get_trace_context() or {}).get
get_trace_context
extra_body
ChatOpenAI
```

<a id="fn-83a5c96e1d4d6668"></a>

## _create_agent

源码：[L190](D:/Project/learnLittle/app/ai_service/react_agent.py:190)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

首选 langchain.agents.create_agent，ImportError 时兼容 create_react_agent。返回代理对象，工具由外层已经按权限/组筛好。

**输入与签名**

```python
def _create_agent(model, tools, system_prompt: str)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return create_agent(model=model, tools=tools or [], system_prompt=system_prompt)
return create_react_agent(model, tools or [], prompt=system_prompt)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
create_agent
create_react_agent
```

<a id="fn-be53e78cc1d24a96"></a>

## _history_messages

源码：[L201](D:/Project/learnLittle/app/ai_service/react_agent.py:201)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

摘要转 SystemMessage，结构化历史的 user/assistant 转对应消息，旧字符串历史则 SystemMessage。角色保留比把所有历史塞用户消息更准确。

**输入与签名**

```python
def _history_messages(history: str | list[dict], summary: str) -> list
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return messages
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(summary or '').strip
messages.append
SystemMessage
summary.strip
isinstance
cls
(history or '').strip
history.strip
```

<a id="fn-dbb853a64eb632ed"></a>

## run_langchain_react

源码：[L216](D:/Project/learnLittle/app/ai_service/react_agent.py:216)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

在整轮超时内建模型/工具/agent，消费事件并累计答案；未触碰副作用时允许一次 L2 修复，末尾可 L1 自检并替换草稿。模型/工具失败发 error，不默认无限重试。

**输入与签名**

```python
async def run_langchain_react(question: str, user_id: str, session_factory, settings: Settings, *, history: str | list[dict]='', summary: str='', rag_context: str='', enable_thinking: bool=False, timeout: int | None=None, tool_groups: list[str] | None=None, extra_system: str='', reflect: bool=True, read_only: bool=False) -> AsyncIterator[dict[str, Any]]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield item
yield failure
return None
yield {'type': 'reflection', 'stage': 'repairing', 'round': 1}
yield {'type': 'response_replace', 'content': ''}
yield {'type': 'response_replace', 'content': refined}
yield event
yield {'type': 'stream_done', 'full_response': final}
```

另有 2 个出口/断言，完整条件见源码。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
agent_timeout
build_react_system_prompt
build_langchain_tools
_create_chat_model
asyncio.timeout
range
_create_agent
_history_messages
HumanMessage
visible_question
agent.astream_events
map_langchain_event
item.get
accumulated.append
registry.get
no_retry_tools
logger.warning
build_repair_note
type
''.join
stream_l1_refine
```

<a id="fn-6e1b44ad15aec546"></a>

## run_react

源码：[L324](D:/Project/learnLittle/app/ai_service/react_agent.py:324)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

选择注入或真实 ReAct，传用户/上下文/工具分组/只读等参数，并负责关闭下游生成器。测试注入可不需要真实模型超时参数。

**输入与签名**

```python
async def run_react(question: str, user_id: str, session_factory, settings: Settings, *, history: str | list[dict]='', summary: str='', rag_context: str='', enable_thinking: bool=False, timeout: int | None=None, tool_groups: list[str] | None=None, extra_system: str='', reflect: bool=True, read_only: bool=False) -> AsyncIterator[dict[str, Any]]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield event
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
fn
aclosing
```
