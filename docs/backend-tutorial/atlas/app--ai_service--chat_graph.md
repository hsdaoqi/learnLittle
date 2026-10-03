# app/ai_service/chat_graph.py

[源码](D:/Project/learnLittle/app/ai_service/chat_graph.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

可取消 LangGraph 分类/执行图与有界输出队列。

## 本文件导航

- [stream_chat_graph](#fn-276c2fbfdee4033c)
- [stream_chat_graph.classify](#fn-81d43d8d4a15d7f1)
- [stream_chat_graph.forward](#fn-d9c17c2b44376c22)
- [stream_chat_graph.react](#fn-b6429330e43a13d3)
- [stream_chat_graph.plan](#fn-f9d2e3b7241dcc1a)
- [stream_chat_graph.<lambda@77:20>](#fn-7e72b2b7cfc8e532)
- [stream_chat_graph.<lambda@81:16>](#fn-896ca593cf230f17)
- [stream_chat_graph.run](#fn-abc4690d1936c2b8)

## 类与字段

### ChatState

LangGraph TypedDict 状态，目前只声明 route；事件不是都塞 state，而是队列转发。

声明位置：[L17](D:/Project/learnLittle/app/ai_service/chat_graph.py:17)。父类：`TypedDict`。

```python
route: str
```

<a id="fn-276c2fbfdee4033c"></a>

## stream_chat_graph

源码：[L21](D:/Project/learnLittle/app/ai_service/chat_graph.py:21)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

构造分类->ReAct/Plan 的可取消 StateGraph，用容量 128 的队列向调用者输出事件。结束/取消时回收生产任务，避免客户端断开后继续无限生成。

**输入与签名**

```python
async def stream_chat_graph(question, user_id, session_factory, settings, *, history, summary, rag_context, enable_thinking, fallback_answer)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield event
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.Queue
object
dict
StateGraph
graph.add_node
graph.add_edge
graph.add_conditional_edges
asyncio.create_task
run
queue.get
task.done
task.cancel
asyncio.gather
```

<a id="fn-81d43d8d4a15d7f1"></a>

## stream_chat_graph.classify

源码：[L32](D:/Project/learnLittle/app/ai_service/chat_graph.py:32)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

对可见问题调用分类器，把路由元数据和分类说明写队列，返回 route 状态。Plan 可用性同时考虑 Agent 开关和规划配置。

**输入与签名**

```python
async def classify(state)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'route': result.route}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
classify_query
visible_question
plan_available
queue.put
result.thinking_text
```

<a id="fn-d9c17c2b44376c22"></a>

## stream_chat_graph.forward

源码：[L46](D:/Project/learnLittle/app/ai_service/chat_graph.py:46)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

在 aclosing 内消费子流并逐事件放入共享队列。队列满会等待，给图输出提供背压。

**输入与签名**

```python
async def forward(stream)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
aclosing
queue.put
```

<a id="fn-b6429330e43a13d3"></a>

## stream_chat_graph.react

源码：[L51](D:/Project/learnLittle/app/ai_service/chat_graph.py:51)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

优先运行配置/注入的新 ReAct；无模型而有本地工具意图则旧 runner；否则输出本地参考答案。设置 agent 计量阶段，不保证任何配置下都调用真实 LLM。

**输入与签名**

```python
async def react(state)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
usage_service.set_trace_stage
get_react_streamer
forward
run_react
should_use_agent
visible_question
'\n'.join
run_agent
queue.put
```

<a id="fn-f9d2e3b7241dcc1a"></a>

## stream_chat_graph.plan

源码：[L62](D:/Project/learnLittle/app/ai_service/chat_graph.py:62)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

转发 Plan 事件，遇 plan_fallback 返回 route=react，否则完成状态。只由 Plan 自己判定何时降级安全，不在这里无条件重跑。

**输入与签名**

```python
async def plan(state)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'route': 'react'}
return {'route': 'complete'}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
run_plan
aclosing
queue.put
```

<a id="fn-7e72b2b7cfc8e532"></a>

## stream_chat_graph.<lambda@77:20>

源码：[L77](D:/Project/learnLittle/app/ai_service/chat_graph.py:77)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

分类条件边把 plan_execute 映射为 plan 节点，其他 route 映射为 react。由 StateGraph 调用，不执行模型本身。

**输入与签名**

```python
lambda state: "plan" if state["route"] == "plan_execute" else "react"
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 'plan' if state['route'] == 'plan_execute' else 'react'
```

<a id="fn-896ca593cf230f17"></a>

## stream_chat_graph.<lambda@81:16>

源码：[L81](D:/Project/learnLittle/app/ai_service/chat_graph.py:81)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

Plan 后条件边读取 state.route，选择 react 或 complete->END。它配合 plan 节点返回值实现安全降级。

**输入与签名**

```python
lambda state: state["route"]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 state['route']
```

<a id="fn-abc4690d1936c2b8"></a>

## stream_chat_graph.run

源码：[L86](D:/Project/learnLittle/app/ai_service/chat_graph.py:86)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

后台执行编译图，普通异常转 error，非取消情况下用 sentinel 通知消费者结束。取消中避免再向满队列写结束标记导致收尾卡住。

**输入与签名**

```python
async def run()
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
graph.compile().ainvoke
graph.compile
queue.put
asyncio.current_task().cancelling
asyncio.current_task
```
