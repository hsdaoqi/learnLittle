# app/ai_service/plan_execute.py

[源码](D:/Project/learnLittle/app/ai_service/plan_execute.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

依赖计划、限量并行读/串行写、步骤 ReAct、综合与安全降级。

## 本文件导航

- [set_plan_streamer](#fn-dcc37072079bad49)
- [get_plan_streamer](#fn-ca9d120f88335b93)
- [set_plan_fn](#fn-3db1d5a82e6b3a65)
- [get_plan_fn](#fn-744d28c0f8b74de9)
- [plan_available](#fn-b250d7dd751c37b2)
- [build_plan_tool_list](#fn-44c77bea7ec5a8a4)
- [build_plan_prompt](#fn-6a480f292c726a7d)
- [parse_plan_payload](#fn-dc6e752aeb2819d5)
- [topological_batches](#fn-58d39dc1d6a68016)
- [_complete](#fn-c957a9e32e24150e)
- [generate_plan](#fn-eb38e1fe0b36e9de)
- [_execute_step](#fn-e7392c211fa754e0)
- [_execute_batch](#fn-df14e4ce292bbe73)
- [_execute_batch.consume](#fn-5826bd5c2c72f710)
- [_safe_batches](#fn-ebca9f483c9d8877)
- [build_synthesize_prompt](#fn-7d65aee7cd907eb4)
- [run_plan_execute](#fn-1b5f9b5c7cac9b7c)
- [run_plan](#fn-2b3c06214bf72e88)

## 类与字段

### PlanStep

步骤号、action、建议工具、依赖号和执行结果；结果供后续真实 ID 上下文。

声明位置：[L30](D:/Project/learnLittle/app/ai_service/plan_execute.py:30)。父类：`无显式父类`。

```python
step: int

action: str

tool: str = 'none'

depends_on: list[int] = field(default_factory=list)

result: str = ''
```

### ExecutionPlan

目标与有序步骤集合，依赖执行还要经过拓扑校验。

声明位置：[L39](D:/Project/learnLittle/app/ai_service/plan_execute.py:39)。父类：`无显式父类`。

```python
goal: str

steps: list[PlanStep]
```


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

PlanStreamer = Callable[..., AsyncIterator[dict[str, Any]]]

PlanFn = Callable[[str], Awaitable['ExecutionPlan']]

_injected_streamer: PlanStreamer | None = None

_injected_plan: PlanFn | None = None
```

<a id="fn-dcc37072079bad49"></a>

## set_plan_streamer

源码：[L44](D:/Project/learnLittle/app/ai_service/plan_execute.py:44)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

替换计划流或计划生成的模块级注入槽 `_injected_streamer`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_plan_streamer(fn: PlanStreamer | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-ca9d120f88335b93"></a>

## get_plan_streamer

源码：[L49](D:/Project/learnLittle/app/ai_service/plan_execute.py:49)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

返回计划流或计划生成当前的注入函数 `_injected_streamer` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_plan_streamer() -> PlanStreamer | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected_streamer
```

<a id="fn-3db1d5a82e6b3a65"></a>

## set_plan_fn

源码：[L53](D:/Project/learnLittle/app/ai_service/plan_execute.py:53)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

替换计划流或计划生成的模块级注入槽 `_injected_plan`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_plan_fn(fn: PlanFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-744d28c0f8b74de9"></a>

## get_plan_fn

源码：[L58](D:/Project/learnLittle/app/ai_service/plan_execute.py:58)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

返回计划流或计划生成当前的注入函数 `_injected_plan` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_plan_fn() -> PlanFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected_plan
```

<a id="fn-b250d7dd751c37b2"></a>

## plan_available

源码：[L62](D:/Project/learnLittle/app/ai_service/plan_execute.py:62)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

综合 plan_execute_enabled 与注入流/注入计划/真实 key 判断是否能规划。返回 bool，分类器据此决定复杂问题能否真走 Plan。

**输入与签名**

```python
def plan_available(settings: Settings) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return settings.plan_execute_enabled and bool(_injected_streamer or _injected_plan or settings.llm_api_key)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
bool
```

<a id="fn-44c77bea7ec5a8a4"></a>

## build_plan_tool_list

源码：[L68](D:/Project/learnLittle/app/ai_service/plan_execute.py:68)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

把注册表当前工具名称/描述转规划提示清单，并加 none 分析步骤。动态工具能进入计划，不靠另一份写死白名单。

**输入与签名**

```python
def build_plan_tool_list() -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '\n'.join((f'- {spec.name}: {spec.description}' for spec in registry.resolve())) + '\n- none: 根据已有结果分析、总结，不调用工具'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
'\n'.join
registry.resolve
```

<a id="fn-6a480f292c726a7d"></a>

## build_plan_prompt

源码：[L74](D:/Project/learnLittle/app/ai_service/plan_execute.py:74)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

给问题、当前时间和工具清单，要求带 depends_on 的 JSON 步骤和真实 ID 依赖。提示不是验证，返回后仍需解析检查。

**输入与签名**

```python
def build_plan_prompt(message: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'你是任务规划器。拆成 2-5 个步骤，显式声明依赖；不要编造工具。\n当前时间：{datetime.now():%Y-%m-%d %H:%M:%S}\n可用工具：\n{build_plan_tool_list()}\n用户请求：{message[:4000]}\n读全文、更新或回顾完成步骤必须依赖提供资源 ID 的步骤。\n最后由系统统一综合回答，不必重复安排综合步骤。只输出 JSON：\n{{"goal":"目标","steps":[{{"step" ... [截短，完整见源码]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
datetime.now
build_plan_tool_list
```

<a id="fn-dc6e752aeb2819d5"></a>

## parse_plan_payload

源码：[L87](D:/Project/learnLittle/app/ai_service/plan_execute.py:87)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

清代码围栏并解析 JSON，构造 PlanStep，拒绝未知工具/空 action，再检查依赖图。返回 ExecutionPlan；解析失败触发运行层安全降级。

**输入与签名**

```python
def parse_plan_payload(raw: str, fallback_goal: str='') -> ExecutionPlan
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ExecutionPlan(str(data.get('goal') or fallback_goal)[:200], steps)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
re.sub('```(?:json)?\\s*', '', (raw or '').strip()).strip
re.sub
(raw or '').strip
json.loads
re.search
ValueError
match.group
isinstance
data.get
enumerate
str
item.get
registry.get
steps.append
PlanStep
int
str(item.get('action') or '').strip
any
topological_batches
ExecutionPlan
```

<a id="fn-58d39dc1d6a68016"></a>

## topological_batches

源码：[L115](D:/Project/learnLittle/app/ai_service/plan_execute.py:115)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

验证正数唯一 step ID、依赖存在，然后不断取依赖已完成的节点批次。没有可执行节点时识别环，返回拓扑层而非实际同时运行安排。

**输入与签名**

```python
def topological_batches(steps: list[PlanStep]) -> list[list[PlanStep]]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return batches
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
len
any
ValueError
set
list
batches.append
completed.update
```

<a id="fn-c957a9e32e24150e"></a>

## _complete

源码：[L134](D:/Project/learnLittle/app/ai_service/plan_execute.py:134)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

临时切换用量 stage 和角色模型，在指定 deadline 内非流式补全，finally 恢复上个 stage。避免计划补全计到别的阶段。

**输入与签名**

```python
async def _complete(prompt, settings, role, timeout, enable_thinking=False)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await complete_openai_compatible(prompt, settings_for_role(settings, role), timeout=timeout, enable_thinking=enable_thinking)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(usage_service.get_trace_context() or {}).get
usage_service.get_trace_context
usage_service.set_trace_stage
asyncio.timeout
complete_openai_compatible
settings_for_role
```

<a id="fn-eb38e1fe0b36e9de"></a>

## generate_plan

源码：[L150](D:/Project/learnLittle/app/ai_service/plan_execute.py:150)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

给规划总调用套 plan_timeout，优先注入 PlanFn，否则模型生成并解析。只产生计划，不调用笔记写工具。

**输入与签名**

```python
async def generate_plan(message: str, settings: Settings) -> ExecutionPlan
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await _injected_plan(message)
return parse_plan_payload(raw, visible_question(message))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.timeout
_injected_plan
_complete
build_plan_prompt
complete_thinking_for
parse_plan_payload
visible_question
```

<a id="fn-e7392c211fa754e0"></a>

## _execute_step

源码：[L163](D:/Project/learnLittle/app/ai_service/plan_execute.py:163)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

先发步骤开始，拼入 depends_on 的真实结果，工具步骤交步骤 ReAct；none 做分析，最后发结束摘要。出错发 error，不编造成功；step.result 保存较完整结果用于后续依赖。

**输入与签名**

```python
async def _execute_step(step, question, previous, user_id, session_factory, settings, *, history, summary, rag_context, enable_thinking)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'plan_step_start', 'step': step.step, 'action': step.action}
yield event
return None
yield {'type': 'error', 'content': f'步骤 {step.step} 执行失败，请稍后重试'}
yield {'type': 'plan_step_end', 'step': step.step, 'action': step.action, 'result': step.result[:200]}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
'\n\n'.join
asyncio.timeout
usage_service.set_trace_stage
run_react
registry.groups_for
bool
registry.get
aclosing
event.get
parts.append
''.join
''.join(parts).strip
(await _complete(task + f'\n历史摘要：{summary}\n参考资料：{rag_context}', settings, 'plan_step', step_timeout, enable_thinking)).strip
_complete
logger.warning
```

<a id="fn-df14e4ce292bbe73"></a>

## _execute_batch

源码：[L229](D:/Project/learnLittle/app/ai_service/plan_execute.py:229)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

为一小批创建并发步骤消费任务，通过队列转发事件，sentinel 计完成数。退出时取消未完项并 gather，防止断流留下步骤后台执行。

**输入与签名**

```python
async def _execute_batch(batch, *args, **kwargs)
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
asyncio.create_task
consume
len
queue.get
asyncio.gather
task.done
task.cancel
```

<a id="fn-5826bd5c2c72f710"></a>

## _execute_batch.consume

源码：[L233](D:/Project/learnLittle/app/ai_service/plan_execute.py:233)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

消费单个步骤的事件写队列，在 finally 放该任务的结束 sentinel。消费者由此能知道所有并发步骤是否结束。

**输入与签名**

```python
async def consume(step)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_execute_step
queue.put
```

<a id="fn-ebca9f483c9d8877"></a>

## _safe_batches

源码：[L257](D:/Project/learnLittle/app/ai_service/plan_execute.py:257)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按并行上限把 readonly/none 步骤分组，非 parallel_safe 写步骤各自一批。这是拓扑层之上的执行安全划分，不是单纯所有无依赖步骤全并发。

**输入与签名**

```python
def _safe_batches(batch, limit)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield reads
yield [step]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
registry.get
reads.append
len
```

<a id="fn-7d65aee7cd907eb4"></a>

## build_synthesize_prompt

源码：[L275](D:/Project/learnLittle/app/ai_service/plan_execute.py:275)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按原计划次序收集各 step.result，结合用户问题/目标要求最终答案，保留笔记 ID。失败结果不能被提示为已经成功的事实。

**输入与签名**

```python
def build_synthesize_prompt(plan: ExecutionPlan, message: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'用户请求：{message}\n目标：{plan.goal}\n各步骤结果：\n{results}\n\n根据结果给出最终回答，不重复过程，不编造失败步骤的结果。笔记搜索结果的编号、标题、(ID: ...) 必须保留。'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
'\n\n'.join
```

<a id="fn-1b5f9b5c7cac9b7c"></a>

## run_plan_execute

源码：[L287](D:/Project/learnLittle/app/ai_service/plan_execute.py:287)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

规划、依赖批次、步骤执行、综合、自检的总流，设置整轮 deadline。tool_start 时记可能副作用，未写失败可 fallback，写后失败只报核查错误避免重放。

**输入与签名**

```python
async def run_plan_execute(question, user_id, session_factory, settings, *, history='', summary='', rag_context='', enable_thinking=False)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'plan_start', 'goal': plan.goal, 'steps': [{'step': step.step, 'action': step.action, 'tool': step.tool} for step in plan.steps]}
yield event
yield {'type': 'error', 'content': '部分操作可能已执行，请核对记录；不会自动重放写入'}
yield {'type': 'plan_fallback', 'reason': 'step_failed'}
return None
yield {'type': 'plan_synthesize', 'goal': plan.goal}
yield {'type': 'response', 'content': answer}
yield {'type': 'plan_complete', 'goal': plan.goal}
```

另有 3 个出口/断言，完整条件见源码。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.timeout
generate_plan
len
ValueError
topological_batches
_safe_batches
max
_execute_batch
event.get
registry.get
no_retry_tools
stream.aclose
previous.update
build_react_system_prompt
isinstance
json.dumps
build_synthesize_prompt
(await _complete(prompt, settings, 'plan_synthesize', settings.plan_synthesize_timeout * (2 if enable_thinking else 1), enable_thinking)).strip
_complete
'\n'.join
stream_l1_refine
previous.values
logger.warning
```

<a id="fn-2b3c06214bf72e88"></a>

## run_plan

源码：[L368](D:/Project/learnLittle/app/ai_service/plan_execute.py:368)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

选择注入 PlanStreamer 或真实总流程，并用 aclosing 转发。注入改变执行来源，不改变调用者消费事件的接口。

**输入与签名**

```python
async def run_plan(question, user_id, session_factory, settings, **kwargs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield event
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
aclosing
fn
```
