# app/rag/llm.py

[源码](D:/Project/learnLittle/app/rag/llm.py) | [任务流程 08](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

httpx 非流式辅助补全，复用于分类、计划、摘要、标题和反思；不是工具执行器。

## 本文件导航

- [complete_openai_compatible](#fn-9d19b1a45ca5ebcf)
<a id="fn-9d19b1a45ca5ebcf"></a>

## complete_openai_compatible

源码：[L6](D:/Project/learnLittle/app/rag/llm.py:6)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

发非流式补全请求，按协议加入 thinking 字段，提取正文并记用量，HTTP 失败抛异常。分类、计划、摘要等短任务复用，由调用方决定降级。

**输入与签名**

```python
async def complete_openai_compatible(prompt: str, settings: Settings, *, enable_thinking: bool=False, timeout: float=30.0) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return text
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_trace_context
UsageTimer
ctx.get
settings.llm_base_url.rstrip
payload_thinking_fields
httpx.AsyncClient
client.post
RuntimeError
resp.json
(data.get('choices') or [{}])[0].get
data.get
(message.get('content') or '').strip
message.get
timer.finish
str
```
