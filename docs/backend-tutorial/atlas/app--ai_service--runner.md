# app/ai_service/runner.py

[源码](D:/Project/learnLittle/app/ai_service/runner.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

无模型关键词工具与测试注入；真实模型工具循环只在 ReAct 主链。

## 本文件导航

- [set_agent_runner](#fn-a716a29dbc0493c2)
- [get_agent_runner](#fn-9d570780bb61bd29)
- [match_local_tool](#fn-4071a0437f28ef48)
- [should_use_agent](#fn-bc6d529cb47bed95)
- [run_local_tool](#fn-a3f33d4584857464)
- [run_agent](#fn-2f0e35aed80e5e70)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

AgentEvent = dict[str, Any]

AgentRunner = Callable[[str, str, Any, Settings, str], AsyncIterator[AgentEvent]]

_injected: AgentRunner | None = None

TOOL_KEYWORDS: list[tuple[str, list[str]]] = [('search_notes_tool', ['搜索笔记', '查找笔记', '找笔记', '搜一下笔记', '相关笔记']), ('get_today_reviews_tool', ['今日待回顾', '待复习', '今天复习', '艾宾浩斯', '回顾列表']), ('get_note_stats_tool', ['笔记统计', '分类统计', '有多少笔记', '笔记数量']), ('get_user_info_tools', ['我是谁', '我的邮箱', '用户信息', '当前用户']), ('what_time_is_now', ['现在几点', '当前时间', '今天几号', '现在时间'])]
```

<a id="fn-a716a29dbc0493c2"></a>

## set_agent_runner

源码：[L35](D:/Project/learnLittle/app/ai_service/runner.py:35)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

替换本地降级 Agent 事件流的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_agent_runner(fn: AgentRunner | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-9d570780bb61bd29"></a>

## get_agent_runner

源码：[L40](D:/Project/learnLittle/app/ai_service/runner.py:40)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

返回本地降级 Agent 事件流当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_agent_runner() -> AgentRunner | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-4071a0437f28ef48"></a>

## match_local_tool

源码：[L44](D:/Project/learnLittle/app/ai_service/runner.py:44)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按固定关键词表返回首个匹配工具名，无匹配 None。是无模型的有限意图规则，不是完整自然语言理解。

**输入与签名**

```python
def match_local_tool(question: str) -> str | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return name
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(question or '').strip
any
```

<a id="fn-bc6d529cb47bed95"></a>

## should_use_agent

源码：[L52](D:/Project/learnLittle/app/ai_service/runner.py:52)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

Agent 关闭返回 False，有注入或本地工具关键词时才选择无模型降级。图在此之前优先判断真实模型或 ReAct 替身，不能拿这条规则替代完整图路由。

**输入与签名**

```python
def should_use_agent(question: str, settings: Settings) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return False
return True
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
match_local_tool
```

<a id="fn-a3f33d4584857464"></a>

## run_local_tool

源码：[L62](D:/Project/learnLittle/app/ai_service/runner.py:62)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

绑定当前用户，根据关键词选择一个工具，发 start/end/response；异常发 tool_end error 后结束。搜索传问题，其余这组本地工具用无参调用。

**输入与签名**

```python
async def run_local_tool(question: str, user_id: str, session_factory, settings: Settings, history: str='') -> AsyncIterator[AgentEvent]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
yield {'type': 'tool_start', 'name': name}
yield {'type': 'tool_end', 'name': name, 'error': str(exc)}
yield {'type': 'tool_end', 'name': name, 'result': result}
yield {'type': 'response', 'content': result}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
match_local_tool
registry.bind
bind_user_tools
bound.get
fn
logger.warning
str
```

<a id="fn-2f0e35aed80e5e70"></a>

## run_agent

源码：[L90](D:/Project/learnLittle/app/ai_service/runner.py:90)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

优先选择注入 runner，否则执行本地关键词工具并转发事件。没有第二套 HTTP 模型工具循环；真实模型问答统一交 LangChain ReAct。

**输入与签名**

```python
async def run_agent(question: str, user_id: str, session_factory, settings: Settings, history: str='') -> AsyncIterator[AgentEvent]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield event
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_injected
run_local_tool
```
