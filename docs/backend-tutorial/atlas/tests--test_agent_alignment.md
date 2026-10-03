# tests/test_agent_alignment.py

[源码](D:/Project/learnLittle/tests/test_agent_alignment.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

## 本文件导航

- [settings](#fn-29159b4b8359fe12)
- [test_memory_covers_unsummarized_gap_and_preserves_roles](#fn-c868f606433f6d54)
- [test_history_respects_tiny_remaining_budget](#fn-f100021dfa9d9e8f)
- [test_legacy_zero_reserve_still_leaves_room_for_agent_tools](#fn-30a1769770aea5bf)
- [test_tool_loop_limit_still_reports_started_write_for_replay_guard](#fn-8eab36803eb3954b)
- [test_planning_deadline_falls_back_without_executing_tools](#fn-b4d889d8d7403790)
- [test_planning_deadline_falls_back_without_executing_tools.stalled](#fn-10ea9957395c086d)
- [test_classifier_deadline_falls_back_to_react](#fn-5aeb5d09ba684163)
- [test_classifier_deadline_falls_back_to_react.stalled](#fn-1bb0f746d36abb32)
- [test_plan_rejects_invalid_dependency_graph](#fn-d8533bbcc918adc7)
- [test_dynamic_tools_execute_and_readonly_steps_exclude_writes](#fn-dfef1440af354660)
- [test_dynamic_tools_execute_and_readonly_steps_exclude_writes.<lambda@111:11>](#fn-a14dfc4638e78af8)
- [test_plan_step_passes_real_dependency_ids_to_agent](#fn-518f774d4dc7cdcc)
- [test_plan_step_passes_real_dependency_ids_to_agent.fake_react](#fn-d4a0e38df4d1686b)
- [test_plan_step_passes_real_dependency_ids_to_agent.make_plan](#fn-60aeae814fb394bd)
- [test_plan_step_passes_real_dependency_ids_to_agent.by_step](#fn-dbc45ed059f68083)
- [test_plan_parallel_reads_serial_writes_and_cancellation](#fn-5f9c8aa3ed6354e0)
- [test_plan_parallel_reads_serial_writes_and_cancellation.step_stream](#fn-01d29b8931a8abf3)
- [test_plan_parallel_reads_serial_writes_and_cancellation.make_plan](#fn-ac48debf4718378f)
- [test_plan_does_not_replay_after_write](#fn-c3b5ad250dc8fa31)
- [test_plan_does_not_replay_after_write.make_plan](#fn-3905ad19d9aff420)
- [test_plan_does_not_replay_after_write.failing_step](#fn-f13ddc4cf1fa890b)
- [test_react_repairs_read_failure_only](#fn-b8e7073db754fb6f)
- [test_react_repairs_read_failure_only.FakeAgent.astream_events](#fn-0ba93bdacfa7f319)
- [test_react_repairs_read_failure_only.<lambda@241:53>](#fn-9b4888afc53c22d5)
- [test_react_repairs_read_failure_only.<lambda@242:48>](#fn-5b996c4b275b58cc)
- [test_reflection_status_is_live_and_replaces_draft](#fn-2e6e0865c007f7b6)
- [test_reflection_status_is_live_and_replaces_draft.critique](#fn-50e78cdd613c2851)
- [test_reflection_status_is_live_and_replaces_draft.refine](#fn-25b62c173398d740)
- [test_reflection_status_is_live_and_replaces_draft.FakeAgent.astream_events](#fn-3408d920c13c2554)
- [test_reflection_status_is_live_and_replaces_draft.<lambda@281:53>](#fn-36180ba9129eccbc)
- [test_reflection_status_is_live_and_replaces_draft.<lambda@282:48>](#fn-3fbc0ff28399f36f)
- [ToolCallingModel.bind_tools](#fn-00c92f5af88654b9)
- [ToolCallingModel._stream](#fn-3d1e9280b081effb)
- [test_real_langchain_tool_loop_records_each_model_call](#fn-f5c5aea51d30b35e)
- [test_real_langchain_tool_loop_records_each_model_call.execute](#fn-bdd513a107456ced)
- [test_real_langchain_tool_loop_records_each_model_call.record](#fn-34ef48af8237c5ce)
- [test_real_langchain_tool_loop_records_each_model_call.<lambda@327:53>](#fn-ae9315f1bb05f0bb)
- [test_classifier_uses_role_model_and_thinking](#fn-33619f79787e28bb)
- [test_classifier_uses_role_model_and_thinking.complete](#fn-fa319b1bd0a89f1c)
- [test_usage_stages_do_not_leak_between_parallel_steps](#fn-881ee18bb499ca04)
- [test_usage_stages_do_not_leak_between_parallel_steps.branch](#fn-382be845dac0d78d)

## 类与字段

### FakeAgent

测试替身类，显式方法在本文件详解；实例只提供该测试需要的可控行为，不代表生产模型实现。

声明位置：[L233](D:/Project/learnLittle/tests/test_agent_alignment.py:233)。父类：`无显式父类`。

### FakeAgent

测试替身类，显式方法在本文件详解；实例只提供该测试需要的可控行为，不代表生产模型实现。

声明位置：[L277](D:/Project/learnLittle/tests/test_agent_alignment.py:277)。父类：`无显式父类`。

### ToolCallingModel

测试替身类，显式方法在本文件详解；实例只提供该测试需要的可控行为，不代表生产模型实现。

声明位置：[L288](D:/Project/learnLittle/tests/test_agent_alignment.py:288)。父类：`FakeMessagesListChatModel`。

<a id="fn-29159b4b8359fe12"></a>

## settings

源码：[L19](D:/Project/learnLittle/tests/test_agent_alignment.py:19)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

生成不读 .env、无真实 key 的 Settings，允许用 kwargs 改特定测试参数。保证测试差异只来自显式配置。

**输入与签名**

```python
def settings(**kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return Settings(_env_file=None, app_env='test', llm_api_key='', **kwargs)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Settings
```

<a id="fn-c868f606433f6d54"></a>

## test_memory_covers_unsummarized_gap_and_preserves_roles

源码：[L23](D:/Project/learnLittle/tests/test_agent_alignment.py:23)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

构造长历史与摘要覆盖点，断言未摘要 30 条不被旧窗口截断，长正文保留，摘要后从正确 ID 开始。再验证转换后的 Human/AI 角色。

**输入与签名**

```python
def test_memory_covers_unsummarized_gap_and_preserves_roles()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert len(history) == 30
assert history[10]['content'] == messages[10]['content']
assert len(history) == 20
assert history[0]['content'] == 'message 21'
assert isinstance(converted[1], HumanMessage)
assert isinstance(converted[2], AIMessage)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
range
build_agent_history
settings
len
react._history_messages
isinstance
```

<a id="fn-f100021dfa9d9e8f"></a>

## test_history_respects_tiny_remaining_budget

源码：[L42](D:/Project/learnLittle/tests/test_agent_alignment.py:42)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

用极小剩余额度和超长单条历史，断言选中消息仍符合预算。覆盖新链不能为保留最新一条而无限超额的边界。

**输入与签名**

```python
def test_history_respects_tiny_remaining_budget()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert history
assert sum((count_message(item['content']) for item in history)) + 2 <= 100
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
settings
build_agent_history
sum
count_message
```

<a id="fn-30a1769770aea5bf"></a>

## test_legacy_zero_reserve_still_leaves_room_for_agent_tools

源码：[L52](D:/Project/learnLittle/tests/test_agent_alignment.py:52)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

把 scratchpad 配零并输入巨大历史，断言仍扣 4000 自动预留。保护旧 .env 在新 Agent 主链的兼容语义。

**输入与签名**

```python
def test_legacy_zero_reserve_still_leaves_room_for_agent_tools()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert sum((count_message(item['content']) for item in history)) + 2 <= quota
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
settings
build_agent_history
sum
count_message
```

<a id="fn-8eab36803eb3954b"></a>

## test_tool_loop_limit_still_reports_started_write_for_replay_guard

源码：[L59](D:/Project/learnLittle/tests/test_agent_alignment.py:59)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

把连续工具次数设六再开始更新工具，断言事件先 tool_start 后 error。保证循环上限不会隐藏已开始的写操作。

**输入与签名**

```python
def test_tool_loop_limit_still_reports_started_write_for_replay_guard()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert [event['type'] for event in events] == ['tool_start', 'error']
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
react.map_langchain_event
```

<a id="fn-b4d889d8d7403790"></a>

## test_planning_deadline_falls_back_without_executing_tools

源码：[L68](D:/Project/learnLittle/tests/test_agent_alignment.py:68)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

注入卡住的规划器并设短超时，断言唯一结果为 plan_fallback。证明规划阶段没执行工具时可以安全降级。

**输入与签名**

```python
async def test_planning_deadline_falls_back_without_executing_tools()
```

装饰器/挂载：

```python
@pytest.mark.asyncio
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert events == [{'type': 'plan_fallback', 'reason': 'plan_failed'}]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
plan.set_plan_fn
plan.run_plan
settings
```

<a id="fn-10ea9957395c086d"></a>

## test_planning_deadline_falls_back_without_executing_tools.stalled

源码：[L69](D:/Project/learnLittle/tests/test_agent_alignment.py:69)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

睡十秒模拟规划模型无响应，短 timeout 会提前取消。不是生产延时逻辑，也不执行工具。

**输入与签名**

```python
async def stalled(_)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.sleep
```

<a id="fn-5aeb5d09ba684163"></a>

## test_classifier_deadline_falls_back_to_react

源码：[L80](D:/Project/learnLittle/tests/test_agent_alignment.py:80)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

替换 L2 分类为卡住协程并设短超时，断言 source=fallback、route=react。验证复杂路由判断失败不拖死对话。

**输入与签名**

```python
async def test_classifier_deadline_falls_back_to_react(monkeypatch)
```

装饰器/挂载：

```python
@pytest.mark.asyncio
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert result.route == 'react'
assert result.source == 'fallback'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
monkeypatch.setattr
settings(classifier_timeout=0.01).model_copy
settings
query_classifier.classify_query
```

<a id="fn-1bb0f746d36abb32"></a>

## test_classifier_deadline_falls_back_to_react.stalled

源码：[L83](D:/Project/learnLittle/tests/test_agent_alignment.py:83)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

接受任意调用参数后睡十秒，以触发分类超时。用来验证调用者 deadline 而非分类模型质量。

**输入与签名**

```python
async def stalled(*args, **kwargs)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.sleep
```

<a id="fn-d8533bbcc918adc7"></a>

## test_plan_rejects_invalid_dependency_graph

源码：[L99](D:/Project/learnLittle/tests/test_agent_alignment.py:99)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

参数化输入未知依赖、自环、重复 ID 和未注册工具，要求 ValueError。它验证结构拒绝，不执行任何笔记操作。

**输入与签名**

```python
def test_plan_rejects_invalid_dependency_graph(steps)
```

装饰器/挂载：

```python
@pytest.mark.parametrize('steps', [[{'step': 1, 'action': 'a', 'depends_on': [2]}], [{'step': 1, 'action': 'a', 'depends_on': [1]}], [{'step': 1, 'action': 'a'}, {'step': 1, 'action': 'b'}], [{'step': 1, 'action': 'a', 'tool': 'not_registered'}]])
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
pytest.raises
plan.parse_plan_payload
json.dumps
pytest.mark.parametrize
```

<a id="fn-dfef1440af354660"></a>

## test_dynamic_tools_execute_and_readonly_steps_exclude_writes

源码：[L105](D:/Project/learnLittle/tests/test_agent_alignment.py:105)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

临时注册 echo，验证 LangChain 可调用动态实现、只读集合不含三个写工具、无参工具 Schema 空，计划也能引用动态名。finally 注销防污染。

**输入与签名**

```python
async def test_dynamic_tools_execute_and_readonly_steps_exclude_writes()
```

装饰器/挂载：

```python
@pytest.mark.asyncio
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert await tools[name].ainvoke({'value': 'actual-value'}) == 'actual-value'
assert 'update_note_tool' not in tools
assert 'create_note_tool' not in tools
assert 'mark_reviewed_tool' not in tools
assert tools['what_time_is_now'].args == {}
assert parsed.steps[0].tool == name
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
registry.register
ToolSpec
build_langchain_tools
tools[name].ainvoke
plan.parse_plan_payload
json.dumps
registry.unregister
```

<a id="fn-a14dfc4638e78af8"></a>

## test_dynamic_tools_execute_and_readonly_steps_exclude_writes.<lambda@111:11>

源码：[L111](D:/Project/learnLittle/tests/test_agent_alignment.py:111)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

动态 echo 工具的真实同步实现，原样返回 value。用于确认注册表 fn 能被 StructuredTool 调用。

**输入与签名**

```python
lambda value: value
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 value
```

<a id="fn-518f774d4dc7cdcc"></a>

## test_plan_step_passes_real_dependency_ids_to_agent

源码：[L129](D:/Project/learnLittle/tests/test_agent_alignment.py:129)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

注入两步搜索/更新计划，检查真实 note/review ID 传入后一步，且读写步骤权限不同。防止步骤执行器自己猜 ID 或只硬调一次工具。

**输入与签名**

```python
async def test_plan_step_passes_real_dependency_ids_to_agent()
```

装饰器/挂载：

```python
@pytest.mark.asyncio
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert events[-1]['type'] == 'stream_done'
assert captured[0][1]['read_only'] is True
assert captured[1][1]['read_only'] is False
assert {'note_write', 'note_read'} <= set(captured[1][1]['tool_groups'])
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
plan.ExecutionPlan
plan.PlanStep
plan.set_plan_fn
react.set_react_streamer
plan.run_plan
settings
set
```

<a id="fn-d4a0e38df4d1686b"></a>

## test_plan_step_passes_real_dependency_ids_to_agent.fake_react

源码：[L132](D:/Project/learnLittle/tests/test_agent_alignment.py:132)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

第一步返回真实样例 ID，后一步断言问题内包含它们，输出 stream_done。记录 kwargs 用于检查 read_only 和工具分组。

**输入与签名**

```python
async def fake_react(question, *args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert 'note_id=real-123' in question
assert 'review_id=42' in question
yield {'type': 'stream_done', 'full_response': result}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
captured.append
```

<a id="fn-60aeae814fb394bd"></a>

## test_plan_step_passes_real_dependency_ids_to_agent.make_plan

源码：[L147](D:/Project/learnLittle/tests/test_agent_alignment.py:147)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

返回预先构造的 ExecutionPlan，省去真实规划模型。让测试集中验证依赖结果传递。

**输入与签名**

```python
async def make_plan(_)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return execution
```

<a id="fn-dbc45ed059f68083"></a>

## test_plan_step_passes_real_dependency_ids_to_agent.by_step

源码：[L150](D:/Project/learnLittle/tests/test_agent_alignment.py:150)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

给第一步追加识别标记，再转发 fake_react 事件。用于区分步骤，不改变生产 Plan 路由。

**输入与签名**

```python
async def by_step(question, *args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield event
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
fake_react
```

<a id="fn-5f9c8aa3ed6354e0"></a>

## test_plan_parallel_reads_serial_writes_and_cancellation

源码：[L166](D:/Project/learnLittle/tests/test_agent_alignment.py:166)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

替换步骤执行器记录活跃集合，断言两读并发、写时无其他活跃任务，关闭流后集合清空。验证并发策略和取消回收。

**输入与签名**

```python
async def test_plan_parallel_reads_serial_writes_and_cancellation(monkeypatch)
```

装饰器/挂载：

```python
@pytest.mark.asyncio
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert events[-1]['type'] == 'stream_done'
assert max_reads == 2
assert not active
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
set
plan.ExecutionPlan
plan.PlanStep
monkeypatch.setattr
plan.set_plan_fn
plan.run_plan
settings
aclosing
```

<a id="fn-01d29b8931a8abf3"></a>

## test_plan_parallel_reads_serial_writes_and_cancellation.step_stream

源码：[L170](D:/Project/learnLittle/tests/test_agent_alignment.py:170)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

只读/写工具开始时维护 active，写工具先断言无其他任务，短等待模拟并发，finally 清 active。这样取消也能被测试观察到。

**输入与签名**

```python
async def step_stream(step, *args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert not active
yield {'type': 'tool_start', 'name': step.tool}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
registry.get
active.add
max
len
asyncio.sleep
active.remove
```

<a id="fn-ac48debf4718378f"></a>

## test_plan_parallel_reads_serial_writes_and_cancellation.make_plan

源码：[L190](D:/Project/learnLittle/tests/test_agent_alignment.py:190)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

返回两读两写的固定无依赖计划。专门检验 safe_batches，不检验 LLM 会如何规划。

**输入与签名**

```python
async def make_plan(_)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return execution
```

<a id="fn-c3b5ad250dc8fa31"></a>

## test_plan_does_not_replay_after_write

源码：[L211](D:/Project/learnLittle/tests/test_agent_alignment.py:211)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

参数化读工具/写工具开始后失败，分别要求 fallback/error，写失败不能出现 fallback。保护可能已提交的副作用不被整轮重放。

**输入与签名**

```python
async def test_plan_does_not_replay_after_write(monkeypatch, tool, expected)
```

装饰器/挂载：

```python
@pytest.mark.asyncio
@pytest.mark.parametrize('tool,expected', [('search_notes_tool', 'plan_fallback'), ('create_note_tool', 'error')])
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert events[-1]['type'] == expected
assert not (expected == 'error' and any((e['type'] == 'plan_fallback' for e in events)))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
plan.set_plan_fn
monkeypatch.setattr
plan.run_plan
settings
any
pytest.mark.parametrize
```

<a id="fn-3905ad19d9aff420"></a>

## test_plan_does_not_replay_after_write.make_plan

源码：[L212](D:/Project/learnLittle/tests/test_agent_alignment.py:212)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

根据参数化 tool 创建单步骤计划。固定规划形状便于只比较工具副作用分类。

**输入与签名**

```python
async def make_plan(_)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return plan.ExecutionPlan('goal', [plan.PlanStep(1, 'action', tool)])
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
plan.ExecutionPlan
plan.PlanStep
```

<a id="fn-f13ddc4cf1fa890b"></a>

## test_plan_does_not_replay_after_write.failing_step

源码：[L215](D:/Project/learnLittle/tests/test_agent_alignment.py:215)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

先 yield tool_start 再 error，模拟开始后未获成功结果。用于证明不能等 tool_end 才认为可能已写。

**输入与签名**

```python
async def failing_step(step, *args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'tool_start', 'name': tool}
yield {'type': 'error', 'content': 'failure'}
```

<a id="fn-b8e7073db754fb6f"></a>

## test_react_repairs_read_failure_only

源码：[L230](D:/Project/learnLittle/tests/test_agent_alignment.py:230)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

参数化读、写、未知工具失败，断言只有只读允许第二次执行并清旧稿；修复提示只暴露异常类型。覆盖 ReAct L2 护栏。

**输入与签名**

```python
async def test_react_repairs_read_failure_only(monkeypatch, tool, retry)
```

装饰器/挂载：

```python
@pytest.mark.asyncio
@pytest.mark.parametrize('tool,retry', [('search_notes_tool', True), ('update_note_tool', False), ('unknown_custom_write', False)])
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert len(calls) == (2 if retry else 1)
assert events[-1]['type'] == ('stream_done' if retry else 'error')
assert any((event['type'] == 'response_replace' for event in events))
assert 'first attempt failed' not in calls[1]['messages'][-1].content
assert 'RuntimeError' in calls[1]['messages'][-1].content
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
monkeypatch.setattr
react.run_langchain_react
settings
len
any
pytest.mark.parametrize
```

<a id="fn-0ba93bdacfa7f319"></a>

## test_react_repairs_read_failure_only.FakeAgent.astream_events

源码：[L234](D:/Project/learnLittle/tests/test_agent_alignment.py:234)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

第一次发工具开始后抛 RuntimeError，第二次发 fixed 正文，保存 payload。重试次数由真实执行器决定，不由 fake 自己循环。

**输入与签名**

```python
async def astream_events(self, payload, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'event': 'on_tool_start', 'name': tool}
yield {'event': 'on_chat_model_stream', 'data': {'chunk': AIMessageChunk(content='fixed')}}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
calls.append
len
RuntimeError
AIMessageChunk
```

<a id="fn-9b4888afc53c22d5"></a>

## test_react_repairs_read_failure_only.<lambda@241:53>

源码：[L241](D:/Project/learnLittle/tests/test_agent_alignment.py:241)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

替换模型构造为普通占位 object，避免连接模型。此测试的模型事件由另外的 FakeAgent 提供。

**输入与签名**

```python
lambda *args, **kwargs: object()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 object()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
object
```

<a id="fn-5b996c4b275b58cc"></a>

## test_react_repairs_read_failure_only.<lambda@242:48>

源码：[L242](D:/Project/learnLittle/tests/test_agent_alignment.py:242)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

替换 Agent 构造为测试 FakeAgent，使第一次工具失败/第二次恢复可控。生产重试判断仍由真实执行器运行。

**输入与签名**

```python
lambda *args: FakeAgent()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 FakeAgent()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
FakeAgent
```

<a id="fn-2e6e0865c007f7b6"></a>

## test_reflection_status_is_live_and_replaces_draft

源码：[L255](D:/Project/learnLittle/tests/test_agent_alignment.py:255)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

逐次 anext 验证 checking 先于 critique 真执行，再用假 Agent 验证修订触发 response_replace 和最终 corrected。测试事件时序而非仅最后文字。

**输入与签名**

```python
async def test_reflection_status_is_live_and_replaces_draft(monkeypatch)
```

装饰器/挂载：

```python
@pytest.mark.asyncio
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert (await anext(stream))['stage'] == 'checking'
assert not checked
assert (await anext(stream))['stage'] == 'refining'
assert checked
assert {'type': 'response_replace', 'content': 'corrected'} in events
assert events[-1]['full_response'] == 'corrected'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
reflection.set_critique_fn
monkeypatch.setattr
settings
reflection.stream_l1_refine
anext
stream.aclose
react.run_langchain_react
```

<a id="fn-50e78cdd613c2851"></a>

## test_reflection_status_is_live_and_replaces_draft.critique

源码：[L260](D:/Project/learnLittle/tests/test_agent_alignment.py:260)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

记录自己已经被调用，并返回不通过及 fix 指令。配合 checked 列表判断状态是否及时送出。

**输入与签名**

```python
async def critique(*args)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return reflection.ReflectionVerdict(False, 'fix')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
checked.append
reflection.ReflectionVerdict
```

<a id="fn-25b62c173398d740"></a>

## test_reflection_status_is_live_and_replaces_draft.refine

源码：[L264](D:/Project/learnLittle/tests/test_agent_alignment.py:264)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

返回 corrected 固定修订稿。避免用真实模型让替换断言不确定。

**输入与签名**

```python
async def refine(*args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 'corrected'
```

<a id="fn-3408d920c13c2554"></a>

## test_reflection_status_is_live_and_replaces_draft.FakeAgent.astream_events

源码：[L278](D:/Project/learnLittle/tests/test_agent_alignment.py:278)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

产出一块 draft 模型正文事件。反思由真实 run_langchain_react 继续执行。

**输入与签名**

```python
async def astream_events(self, *args, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'event': 'on_chat_model_stream', 'data': {'chunk': AIMessageChunk(content='draft')}}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
AIMessageChunk
```

<a id="fn-36180ba9129eccbc"></a>

## test_reflection_status_is_live_and_replaces_draft.<lambda@281:53>

源码：[L281](D:/Project/learnLittle/tests/test_agent_alignment.py:281)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

反思测试用普通 object 代替真实模型构造。避免模型网络影响 checking/refining 时序断言。

**输入与签名**

```python
lambda *args, **kwargs: object()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 object()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
object
```

<a id="fn-3fbc0ff28399f36f"></a>

## test_reflection_status_is_live_and_replaces_draft.<lambda@282:48>

源码：[L282](D:/Project/learnLittle/tests/test_agent_alignment.py:282)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

反思测试返回只生成 draft 的 FakeAgent。后续替换必须由真实反思逻辑完成。

**输入与签名**

```python
lambda *args: FakeAgent()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 FakeAgent()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
FakeAgent
```

<a id="fn-00c92f5af88654b9"></a>

## ToolCallingModel.bind_tools

源码：[L289](D:/Project/learnLittle/tests/test_agent_alignment.py:289)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

假模型接受工具绑定但直接返回 self。使真实 LangChain create_agent 能使用预设工具调用消息，不访问网络。

**输入与签名**

```python
def bind_tools(self, tools, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return self
```

<a id="fn-3d1e9280b081effb"></a>

## ToolCallingModel._stream

源码：[L292](D:/Project/learnLittle/tests/test_agent_alignment.py:292)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

从预设 _generate 消息构建 ChatGenerationChunk，保留正文、tool_calls 和 usage_metadata。不是跳过 LangChain 的整段假 ReAct。

**输入与签名**

```python
def _stream(self, messages, stop=None, run_manager=None, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield ChatGenerationChunk(message=AIMessageChunk(content=message.content, tool_calls=message.tool_calls, usage_metadata=message.usage_metadata))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._generate
ChatGenerationChunk
AIMessageChunk
```

<a id="fn-f5c5aea51d30b35e"></a>

## test_real_langchain_tool_loop_records_each_model_call

源码：[L301](D:/Project/learnLittle/tests/test_agent_alignment.py:301)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

用真实 LangChain 循环配预设模型先调工具再回答，断言真实参数、两次用量、历史和工具结果进入对应输入。证明 callback 按每次模型调用计量。

**输入与签名**

```python
async def test_real_langchain_tool_loop_records_each_model_call(monkeypatch)
```

装饰器/挂载：

```python
@pytest.mark.asyncio
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert calls == ['real-id']
assert events[-1] == {'type': 'stream_done', 'full_response': 'final'}
assert len(records) == 2
assert records[0]['usage_payload']['usage']['prompt_tokens'] == 17
assert records[1]['usage_payload']['usage']['completion_tokens'] == 3
assert 'history' in records[0]['prompt']
assert 'tool-result' in records[1]['prompt']
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
registry.register
ToolSpec
ToolCallingModel
AIMessage
usage_callback.ModelUsageCallback
monkeypatch.setattr
react.run_langchain_react
settings
len
registry.unregister
```

<a id="fn-bdd513a107456ced"></a>

## test_real_langchain_tool_loop_records_each_model_call.execute

源码：[L308](D:/Project/learnLittle/tests/test_agent_alignment.py:308)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

记录传入 value 并返回 tool-result。验证 StructuredTool 实际收到 real-id，不只输出装饰事件。

**输入与签名**

```python
async def execute(value)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 'tool-result'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
calls.append
```

<a id="fn-34ef48af8237c5ce"></a>

## test_real_langchain_tool_loop_records_each_model_call.record

源码：[L312](D:/Project/learnLittle/tests/test_agent_alignment.py:312)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

用列表捕获 record_text_call 的 kwargs，替代实际 SQL 用量写入。用于检查 usage 和 prompt，无数据库副作用。

**输入与签名**

```python
async def record(**kwargs)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
records.append
```

<a id="fn-ae9315f1bb05f0bb"></a>

## test_real_langchain_tool_loop_records_each_model_call.<lambda@327:53>

源码：[L327](D:/Project/learnLittle/tests/test_agent_alignment.py:327)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

将模型工厂替换为预设 ToolCallingModel 实例。真实 LangChain 工具循环和 usage callback 仍参与执行。

**输入与签名**

```python
lambda *args, **kwargs: model
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 model
```

<a id="fn-33619f79787e28bb"></a>

## test_classifier_uses_role_model_and_thinking

源码：[L345](D:/Project/learnLittle/tests/test_agent_alignment.py:345)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

替换补全并配置 small-model/角色 thinking，断言分类选择计划且传入正确 model、开关和超时。与主模型设置解耦。

**输入与签名**

```python
async def test_classifier_uses_role_model_and_thinking(monkeypatch)
```

装饰器/挂载：

```python
@pytest.mark.asyncio
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert result.route == 'plan_execute'
assert captured == {'model': 'small-model', 'enable_thinking': True, 'timeout': 15.0}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
monkeypatch.setattr
_llm_classify
settings
```

<a id="fn-fa319b1bd0a89f1c"></a>

## test_classifier_uses_role_model_and_thinking.complete

源码：[L351](D:/Project/learnLittle/tests/test_agent_alignment.py:351)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

捕获 config.llm_model 与关键字参数，返回固定 complex JSON。用于验证配置传递而非模型理解能力。

**输入与签名**

```python
async def complete(prompt, config, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '{"complexity":"complex","reason":"multi-step"}'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
captured.update
```

<a id="fn-881ee18bb499ca04"></a>

## test_usage_stages_do_not_leak_between_parallel_steps

源码：[L364](D:/Project/learnLittle/tests/test_agent_alignment.py:364)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

两个 gather 分支分别切阶段，断言各保留自己的值且父仍 chat。防止 ContextVar 中共享字典被原地修改。

**输入与签名**

```python
async def test_usage_stages_do_not_leak_between_parallel_steps()
```

装饰器/挂载：

```python
@pytest.mark.asyncio
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert await asyncio.gather(branch('a'), branch('b')) == ['a', 'b']
assert usage_service.get_trace_context()['stage'] == 'chat'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
usage_service.set_trace_context
asyncio.gather
branch
usage_service.get_trace_context
usage_service.clear_trace_context
```

<a id="fn-382be845dac0d78d"></a>

## test_usage_stages_do_not_leak_between_parallel_steps.branch

源码：[L369](D:/Project/learnLittle/tests/test_agent_alignment.py:369)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

设置分支 stage，主动让出事件循环后读回。让并行交错足以暴露共享状态污染。

**输入与签名**

```python
async def branch(stage)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return usage_service.get_trace_context()['stage']
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
usage_service.set_trace_stage
asyncio.sleep
usage_service.get_trace_context
```
