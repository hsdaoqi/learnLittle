# app/ai_service/reflection.py

[源码](D:/Project/learnLittle/app/ai_service/reflection.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

L1 批判/修订实时状态与 L2 修复提示，失败不阻断已有草稿。

## 本文件导航

- [set_critique_fn](#fn-3ca489ab7e6a7c07)
- [get_critique_fn](#fn-e1959186f3cf4d67)
- [parse_critique_response](#fn-f36e8843e2e37e1c)
- [build_critique_prompt](#fn-a3497a62e34f6eff)
- [build_repair_note](#fn-4061245960041999)
- [build_refine_prompt](#fn-57b6bd8383bee04c)
- [no_retry_tools](#fn-713ab34e17e54a6f)
- [critique_answer](#fn-c28c52684a57227b)
- [refine_answer](#fn-dea73b03114fb405)
- [stream_l1_refine](#fn-945dd769a44b0d80)

## 类与字段

### ReflectionVerdict

批判结果 passed/issues；无法可信解析的批判会被按通过处理。

声明位置：[L26](D:/Project/learnLittle/app/ai_service/reflection.py:26)。父类：`无显式父类`。

```python
passed: bool

issues: str = ''
```


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

CritiqueFn = Callable[[str, str, str], Awaitable['ReflectionVerdict']]

_injected: CritiqueFn | None = None
```

<a id="fn-3ca489ab7e6a7c07"></a>

## set_critique_fn

源码：[L31](D:/Project/learnLittle/app/ai_service/reflection.py:31)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

替换答案批判的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_critique_fn(fn: CritiqueFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-e1959186f3cf4d67"></a>

## get_critique_fn

源码：[L36](D:/Project/learnLittle/app/ai_service/reflection.py:36)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

返回答案批判当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_critique_fn() -> CritiqueFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-f36e8843e2e37e1c"></a>

## parse_critique_response

源码：[L40](D:/Project/learnLittle/app/ai_service/reflection.py:40)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

清围栏、解析 pass/issues，无法解析或不通过却无修改理由都视为通过。反思是增强，不因评审格式差毁掉已有答案。

**输入与签名**

```python
def parse_critique_response(raw: str) -> ReflectionVerdict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ReflectionVerdict(True)
return ReflectionVerdict(passed, issues)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
re.sub
re.sub('```\\s*', '', text).strip
json.loads
re.search
logger.warning
ReflectionVerdict
match.group
isinstance
bool
data.get
str(data.get('issues') or '').strip
str
```

<a id="fn-a3497a62e34f6eff"></a>

## build_critique_prompt

源码：[L65](D:/Project/learnLittle/app/ai_service/reflection.py:65)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

把问题、计划目标、步骤结果与草稿放入质量评审提示，要求实质问题的 JSON。截部分输入以控制长度。

**输入与签名**

```python
def build_critique_prompt(user_message: str, plan_summary: str, step_results: str, draft: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'你是一个回答质量评审员。评审以下回答是否合格，输出严格 JSON。\n\n原始用户问题：{(user_message or '')[:1000]}\n\n执行计划目标：{plan_summary or '（无计划，直接回答）'}\n\n各步骤结果（内部参考）：\n{step_results or '（无分步结果）'}\n\n待评审回答：\n{(draft or '')[:4000]}\n\n评判维度（任一不满足 → pass: false）：\n1.  ... [截短，完整见源码]
```

<a id="fn-4061245960041999"></a>

## build_repair_note

源码：[L87](D:/Project/learnLittle/app/ai_service/reflection.py:87)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

生成上次工具/执行失败的短附加提示，提醒修参数或换策略而非反复试。真正能否重试仍由执行器副作用判断决定。

**输入与签名**

```python
def build_repair_note(failed_tool: str | None, error_content: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'\n\n[系统提示：{tool_part}（原因：{str(error_content)[:150]}）。请分析失败原因，修正参数或更换策略，最多再尝试 1 次工具调用；若无法确定修复方式，请直接基于已有信息回答，不要反复重试。]'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
str
```

<a id="fn-57b6bd8383bee04c"></a>

## build_refine_prompt

源码：[L96](D:/Project/learnLittle/app/ai_service/reflection.py:96)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

给旧稿与 issues，要求输出完整修订正文。返回提示，不做局部字符串补丁。

**输入与签名**

```python
def build_refine_prompt(user_message: str, draft: str, issues: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'你之前对用户问题「{(user_message or '')[:500]}」的回答未通过质量评审。\n\n上一版回答：\n{(draft or '')[:4000]}\n\n评审意见（必须修正的问题）：\n{issues}\n\n请输出修正后的完整回答（只输出回答正文，不要解释修改过程）。'
```

<a id="fn-713ab34e17e54a6f"></a>

## no_retry_tools

源码：[L105](D:/Project/learnLittle/app/ai_service/reflection.py:105)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

把配置逗号分隔名称转集合，空配置使用 send_email 默认。注册表 non-parallel_safe 和未知工具也会参与执行器禁止重试。

**输入与签名**

```python
def no_retry_tools(settings: Settings) -> set[str]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {part.strip() for part in raw.split(',') if part.strip()}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
part.strip
raw.split
```

<a id="fn-c28c52684a57227b"></a>

## critique_answer

源码：[L110](D:/Project/learnLittle/app/ai_service/reflection.py:110)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

优先注入，否则 reflection 角色补全并解析；没 key/异常视为通过，临时 stage 最后恢复。外层 stream 还加批判 deadline。

**输入与签名**

```python
async def critique_answer(user_message: str, draft: str, settings: Settings, *, plan_summary: str='', step_results: str='') -> ReflectionVerdict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await _injected(user_message, draft, plan_summary)
return ReflectionVerdict(True)
return parse_critique_response(raw)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_injected
ReflectionVerdict
(usage_service.get_trace_context() or {}).get
usage_service.get_trace_context
usage_service.set_trace_stage
settings_for_role
complete_openai_compatible
build_critique_prompt
complete_thinking_for
parse_critique_response
logger.warning
```

<a id="fn-dea73b03114fb405"></a>

## refine_answer

源码：[L147](D:/Project/learnLittle/app/ai_service/reflection.py:147)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

把上下文与修订提示送主配置模型，thinking 跟当前主开关，临时记 reflection 阶段。异常交外层保留草稿。

**输入与签名**

```python
async def refine_answer(user_message: str, draft: str, issues: str, settings: Settings, *, enable_thinking: bool=False, context: str='') -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return (text or '').strip()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(usage_service.get_trace_context() or {}).get
usage_service.get_trace_context
usage_service.set_trace_stage
complete_openai_compatible
build_refine_prompt
(text or '').strip
```

<a id="fn-945dd769a44b0d80"></a>

## stream_l1_refine

源码：[L173](D:/Project/learnLittle/app/ai_service/reflection.py:173)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按开关、长度与模型可用性决定是否自检，等待之前先 yield checking/refining，修订失败留原稿，最后 stream_done。它输出最终值，由上层决定 response_replace。

**输入与签名**

```python
async def stream_l1_refine(user_message: str, draft: str, settings: Settings, *, plan_summary: str='', step_results: str='', enable_thinking: bool=False, context: str='')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield {'type': 'reflection', 'stage': 'checking', 'round': 0}
yield {'type': 'reflection', 'stage': 'refining', 'round': 1}
yield {'type': 'reflection', 'stage': '', 'round': 0}
yield {'type': 'stream_done', 'full_response': text}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(draft or '').strip
len
asyncio.timeout
critique_answer
ReflectionVerdict
refine_answer
logger.warning
```
