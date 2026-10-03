# app/ai_service/thinking.py

[源码](D:/Project/learnLittle/app/ai_service/thinking.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

协议兼容、附件互斥、角色独立 thinking 和超时放宽。

## 本文件导航

- [ThinkingDecision.sse_notice](#fn-eaea71090ed2ca6a)
- [thinking_protocol](#fn-ee4cb0b90081ee01)
- [extra_body](#fn-20af143260a09f29)
- [payload_thinking_fields](#fn-b78376eda697d9ea)
- [resolve_agent_thinking](#fn-98949ec9a107c67c)
- [complete_thinking_for](#fn-005d33b41c9835e8)
- [agent_timeout](#fn-db5d2664c9086df9)

## 类与字段

### ThinkingDecision

保留请求值与实际应用值及原因，便于解释附件/协议导致的降级。

声明位置：[L26](D:/Project/learnLittle/app/ai_service/thinking.py:26)。父类：`无显式父类`。

```python
requested: bool

applied: bool

reason: ThinkingReason
```


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
ThinkingReason = Literal['off', 'agent', 'attachment', 'unsupported']

ThinkingProtocol = Literal['dashscope', 'none']

CompleteRole = Literal['classifier', 'plan', 'reflection', 'agent']

ATTACHMENT_THINKING_NOTICE = '深度思考对附件场景自动关闭（视觉模型理解附件）'

UNSUPPORTED_THINKING_NOTICE = '当前模型接口不支持深度思考，已按普通模式继续'
```

<a id="fn-eaea71090ed2ca6a"></a>

## ThinkingDecision.sse_notice

源码：[L31](D:/Project/learnLittle/app/ai_service/thinking.py:31)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

只有用户要求思考但被附件/协议关闭时生成解释事件，否则 None。文案不证明视觉模型已经实现。

**输入与签名**

```python
def sse_notice(self) -> dict[str, str] | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'type': 'thinking', 'stage': 'attachment', 'content': ATTACHMENT_THINKING_NOTICE}
return {'type': 'thinking', 'stage': 'unsupported', 'content': UNSUPPORTED_THINKING_NOTICE}
return None
```

<a id="fn-ee4cb0b90081ee01"></a>

## thinking_protocol

源码：[L47](D:/Project/learnLittle/app/ai_service/thinking.py:47)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按显式 none/dashscope 或 auto 的 URL 字串判断协议。auto 只识别项目支持的 DashScope 形式，不对任意网关做远端能力探测。

**输入与签名**

```python
def thinking_protocol(settings: Settings) -> ThinkingProtocol
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 'none'
return 'dashscope'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(settings.llm_thinking_protocol or 'auto').strip().lower
(settings.llm_thinking_protocol or 'auto').strip
(settings.llm_base_url or '').lower
```

<a id="fn-20af143260a09f29"></a>

## extra_body

源码：[L60](D:/Project/learnLittle/app/ai_service/thinking.py:60)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

协议支持才返回 enable_thinking 字典，否则 None。避免向不支持扩展的网关发送非法参数。

**输入与签名**

```python
def extra_body(enable_thinking: bool, settings: Settings) -> dict[str, bool] | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
return {'enable_thinking': bool(enable_thinking)}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
thinking_protocol
bool
```

<a id="fn-b78376eda697d9ea"></a>

## payload_thinking_fields

源码：[L67](D:/Project/learnLittle/app/ai_service/thinking.py:67)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

把 extra_body 转普通请求体可合并字典，不支持时空字典。直接 httpx 调用和 ChatOpenAI 的字段位置不同。

**输入与签名**

```python
def payload_thinking_fields(enable_thinking: bool, settings: Settings) -> dict[str, bool]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return dict(body) if body is not None else {}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
extra_body
dict
```

<a id="fn-98949ec9a107c67c"></a>

## resolve_agent_thinking

源码：[L73](D:/Project/learnLittle/app/ai_service/thinking.py:73)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按附件互斥、用户开关和协议支持生成 requested/applied/reason。attachment_ids 只触发关闭，不读取实际图片。

**输入与签名**

```python
def resolve_agent_thinking(requested: bool, *, has_attachments: bool=False, settings: Settings | None=None) -> ThinkingDecision
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ThinkingDecision(bool(requested), False, 'attachment')
return ThinkingDecision(False, False, 'off')
return ThinkingDecision(True, False, 'unsupported')
return ThinkingDecision(True, True, 'agent')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
ThinkingDecision
bool
thinking_protocol
```

<a id="fn-005d33b41c9835e8"></a>

## complete_thinking_for

源码：[L88](D:/Project/learnLittle/app/ai_service/thinking.py:88)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

分类、计划、批判分别读角色配置；不支持协议或其他角色默认 False。主模型请求开关不直接传播到所有辅助角色。

**输入与签名**

```python
def complete_thinking_for(role: CompleteRole, settings: Settings) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return False
return bool(settings.classifier_enable_thinking)
return bool(settings.plan_enable_thinking)
return bool(settings.reflection_enable_thinking)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
thinking_protocol
bool
```

<a id="fn-db5d2664c9086df9"></a>

## agent_timeout

源码：[L100](D:/Project/learnLittle/app/ai_service/thinking.py:100)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

选择显式或默认超时，主 thinking 开时乘二。只返回秒数，真正 deadline 在执行器。

**输入与签名**

```python
def agent_timeout(settings: Settings, enable_thinking: bool, *, timeout: int | None=None) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return base * 2 if enable_thinking else base
```
