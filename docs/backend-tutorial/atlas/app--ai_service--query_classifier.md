# app/ai_service/query_classifier.py

[源码](D:/Project/learnLittle/app/ai_service/query_classifier.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

L1 规则、L2 补全和安全默认简单路线。

## 本文件导航

- [ClassificationResult.thinking_text](#fn-2df8faae7a7515cf)
- [set_classifier_fn](#fn-bfaa398a9ea4e50c)
- [get_classifier_fn](#fn-e9b5aab26bf35da9)
- [decide_route](#fn-abce886919e256bb)
- [_count_tool_keywords](#fn-0cc6c7d300f74c31)
- [rule_classify](#fn-5470a2b4e64f144d)
- [_final](#fn-66767a6771de44a4)
- [build_classify_prompt](#fn-e49998c50ba722a8)
- [parse_classifier_payload](#fn-524c068ca8a1d408)
- [_llm_classify](#fn-07591be957e7783b)
- [classify_query](#fn-13f478f262a46ffc)

## 类与字段

### ClassificationResult

复杂度、来源、理由、置信值和路线；置信值是程序给定，不是校准概率。

声明位置：[L81](D:/Project/learnLittle/app/ai_service/query_classifier.py:81)。父类：`无显式父类`。

```python
complexity: Complexity

source: ClassifierSource

reason: str

confidence: float = 1.0

route: RouteName = 'react'
```


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

Complexity = Literal['simple', 'complex']

ClassifierSource = Literal['rule', 'llm', 'inject', 'fallback']

RouteName = Literal['react', 'plan_pending', 'plan_execute']

ClassifierFn = Callable[[str], Awaitable['ClassificationResult']]

_injected: ClassifierFn | None = None

COMPLEX_PATTERNS = ('分析.*总结', '对比.*整理', '研究.*归纳', '先.*然后.*再', '计划', '规划', '步骤', '方案', '策略', '综合分析', '系统梳理')

SIMPLE_PATTERNS = ('^你好', '^谢谢', '^再见', '^现在.*时间')

CONDITION_PATTERNS = ('如果.*否则', '要么.*要么', '根据.*决定')

TOOL_KEYWORDS = ('搜索笔记', '搜索', '统计', '回顾', '创建', '更新', '推荐', '标记')

TOOL_INTENT_KEYWORDS = ('搜索', '统计', '回顾', '创建', '更新', '推荐', '标记', '时间')

_COMPLEX_RES = [re.compile(pattern) for pattern in COMPLEX_PATTERNS]

_SIMPLE_RES = [re.compile(pattern) for pattern in SIMPLE_PATTERNS]

_CONDITION_RES = [re.compile(pattern) for pattern in CONDITION_PATTERNS]
```

<a id="fn-2df8faae7a7515cf"></a>

## ClassificationResult.thinking_text

源码：[L88](D:/Project/learnLittle/app/ai_service/query_classifier.py:88)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

根据 complexity 与实际 route 生成可读分类说明，包括复杂但 Plan 不可用。不是模型隐藏推理，只是状态文案。

**输入与签名**

```python
def thinking_text(self) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'判定为复杂查询（{self.source}），走 Plan-Execute'
return f'判定为复杂查询（{self.source}），Plan-Execute 不可用，本轮降级 ReAct'
return f'判定为简单查询（{self.source}），走 ReAct'
```

<a id="fn-bfaa398a9ea4e50c"></a>

## set_classifier_fn

源码：[L98](D:/Project/learnLittle/app/ai_service/query_classifier.py:98)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

替换查询分类的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_classifier_fn(fn: ClassifierFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-e9b5aab26bf35da9"></a>

## get_classifier_fn

源码：[L103](D:/Project/learnLittle/app/ai_service/query_classifier.py:103)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

返回查询分类当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_classifier_fn() -> ClassifierFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-abce886919e256bb"></a>

## decide_route

源码：[L107](D:/Project/learnLittle/app/ai_service/query_classifier.py:107)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

complex 且可用返回 plan_execute，complex 不可用返回 plan_pending，其余 react。图把非 plan_execute 走 react，pending 不是排队实现。

**输入与签名**

```python
def decide_route(complexity: str, *, plan_available: bool=False) -> RouteName
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 'plan_execute' if plan_available else 'plan_pending'
return 'react'
```

<a id="fn-0cc6c7d300f74c31"></a>

## _count_tool_keywords

源码：[L113](D:/Project/learnLittle/app/ai_service/query_classifier.py:113)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按关键词长度优先匹配，避免搜索笔记和搜索等包含关系重复计数。返回意图种数，供多目标规则用。

**输入与签名**

```python
def _count_tool_keywords(message: str) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return len(matched)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
sorted
any
matched.append
len
```

<a id="fn-5470a2b4e64f144d"></a>

## rule_classify

源码：[L124](D:/Project/learnLittle/app/ai_service/query_classifier.py:124)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

依次检查复杂模式、长多问句、多工具、条件分支和简单模式；无法确定返回 uncertain。只做 L1，不调用模型。

**输入与签名**

```python
def rule_classify(message: str, settings: Settings, *, plan_available: bool=False) -> ClassificationResult
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ClassificationResult('simple', 'rule', 'empty', 1.0, 'react')
return _final('complex', 'rule', f'匹配复杂模式: {pattern.pattern}', plan_available=plan_available)
return _final('complex', 'rule', f'长文本({len(text)}字符)+{question_marks}个问号', plan_available=plan_available)
return _final('complex', 'rule', f'多目标并列: 匹配{matched_tools}个工具意图', plan_available=plan_available)
return _final('complex', 'rule', f'条件分支: 匹配 {pattern.pattern}', plan_available=plan_available)
return _final('simple', 'rule', f'匹配简单模式: {pattern.pattern}', plan_available=plan_available)
return _final('simple', 'rule', f'短消息({len(text)}字符)无工具意图', plan_available=plan_available)
return _final('simple', 'rule', '单步工具操作', plan_available=plan_available)
```

另有 1 个出口/断言，完整条件见源码。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(message or '').strip
ClassificationResult
pattern.search
_final
text.count
len
_count_tool_keywords
any
```

<a id="fn-66767a6771de44a4"></a>

## _final

源码：[L193](D:/Project/learnLittle/app/ai_service/query_classifier.py:193)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

统一构造 ClassificationResult 并通过 decide_route 计算路线。调用者提供来源/理由，避免不同分支漏填字段。

**输入与签名**

```python
def _final(complexity: Complexity, source: ClassifierSource, reason: str, confidence: float=1.0, *, plan_available: bool=False) -> ClassificationResult
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ClassificationResult(complexity, source, reason, confidence, decide_route(complexity, plan_available=plan_available))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
ClassificationResult
decide_route
```

<a id="fn-e49998c50ba722a8"></a>

## build_classify_prompt

源码：[L210](D:/Project/learnLittle/app/ai_service/query_classifier.py:210)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

截问题前 500 字，给简单/复杂例子并要求 JSON。限制输入成本，但长问题尾部可能未进入 L2。

**输入与签名**

```python
def build_classify_prompt(message: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'你是一个查询复杂度分析器。判断以下用户消息属于"简单"还是"复杂"。\n\n简单消息的特征：\n- 可以在一步内完成（单一工具调用或直接回答）\n- 不涉及多个子任务\n- 不需要先收集信息再综合处理\n- 示例："现在几点了？"、"帮我搜索Python笔记"、"什么是Docker？"\n\n复杂消息的特征：\n- 需要多步骤完成（先搜索、再分析、最后汇总等）\n- 包含多个子任务或目标\n- 需要制定计划分步执行\n- 示例："分析我最近的笔记，总结 ... [截短，完整见源码]
```

<a id="fn-524c068ca8a1d408"></a>

## parse_classifier_payload

源码：[L230](D:/Project/learnLittle/app/ai_service/query_classifier.py:230)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

容错去围栏/抽 JSON，规范 complexity 和理由，非法输出回 simple。返回的是模型来源结果，不自动证明判断正确。

**输入与签名**

```python
def parse_classifier_payload(raw: str, *, plan_available: bool=False) -> ClassificationResult
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _final('simple', 'llm', 'parse_error', 0.5, plan_available=plan_available)
return _final(complexity, 'llm', reason, 0.8, plan_available=plan_available)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(raw or '').strip
re.sub
re.sub('```\\s*', '', content).strip
json.loads
re.search
_final
match.group
isinstance
data.get
str
```

<a id="fn-07591be957e7783b"></a>

## _llm_classify

源码：[L261](D:/Project/learnLittle/app/ai_service/query_classifier.py:261)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

切 classify stage，选择 classifier 角色模型与其 thinking 开关调用补全，解析结果，finally 恢复 stage。与主对话思考开关独立。

**输入与签名**

```python
async def _llm_classify(message: str, settings: Settings, *, plan_available: bool=False) -> ClassificationResult
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return parse_classifier_payload(raw, plan_available=plan_available)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(usage_service.get_trace_context() or {}).get
usage_service.get_trace_context
usage_service.set_trace_stage
settings_for_role
complete_openai_compatible
build_classify_prompt
complete_thinking_for
parse_classifier_payload
```

<a id="fn-13f478f262a46ffc"></a>

## classify_query

源码：[L284](D:/Project/learnLittle/app/ai_service/query_classifier.py:284)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

总分类入口：关闭则简单，注入优先，L1 确定即返回，不确定且 L2/key 可用才限时模型判断。异常回 simple，注入分支用于确定性测试。

**输入与签名**

```python
async def classify_query(message: str, settings: Settings, *, plan_available: bool=False) -> ClassificationResult
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _final('simple', 'fallback', 'disabled', 1.0, plan_available=plan_available)
return ClassificationResult(result.complexity, 'inject', result.reason, result.confidence, route)
return l1
return _final('simple', 'fallback', 'no_llm_default', 0.5, plan_available=plan_available)
return await _llm_classify(text, settings, plan_available=plan_available)
return _final('simple', 'fallback', 'llm_fallback', 0.5, plan_available=plan_available)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(message or '').strip
_final
_injected
decide_route
ClassificationResult
rule_classify
asyncio.timeout
_llm_classify
logger.warning
```
