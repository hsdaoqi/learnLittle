# app/rag/rag_summarize.py

[源码](D:/Project/learnLittle/app/rag/rag_summarize.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

命中副本压缩/截断，原命中留作来源展示。

## 本文件导航

- [set_summarize_fn](#fn-d3f3db8b347a4518)
- [get_summarize_fn](#fn-c6676e6d9eccd4cb)
- [build_summarize_prompt](#fn-4eb52a08d2a53cd8)
- [truncate_text](#fn-1007ec241d37bd1e)
- [_copy_hit](#fn-731976d20fe7ebae)
- [_complete_summary](#fn-47e9f5f6c0eb3f04)
- [_summarize_one](#fn-9a1f9063810e676b)
- [summarize_hits](#fn-ef5730d7ff5815aa)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

SUMMARIZE_PROMPT = '请根据问题，从下面的文档片段中提取能回答问题的信息，写成一段简短参考。\n只保留相关事实，不要编造。如果片段与问题无关，只输出「与问题无关」。\n不要解释你在做什么，只输出短参考本身。\n\n问题：{query}\n\n文档片段：\n{document}\n\n短参考：'

SummarizeFn = Callable[[str, str], Awaitable[str]]

_injected: SummarizeFn | None = None
```

<a id="fn-d3f3db8b347a4518"></a>

## set_summarize_fn

源码：[L37](D:/Project/learnLittle/app/rag/rag_summarize.py:37)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

替换命中片段摘要的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_summarize_fn(fn: SummarizeFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-c6676e6d9eccd4cb"></a>

## get_summarize_fn

源码：[L42](D:/Project/learnLittle/app/rag/rag_summarize.py:42)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

返回命中片段摘要当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_summarize_fn() -> SummarizeFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-4eb52a08d2a53cd8"></a>

## build_summarize_prompt

源码：[L46](D:/Project/learnLittle/app/rag/rag_summarize.py:46)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

组合问题与切片，要求提取能回答问题的短参考。模型可答无关，不保证结果一定有用。

**输入与签名**

```python
def build_summarize_prompt(query: str, document: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return SUMMARIZE_PROMPT.format(query=query, document=document)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
SUMMARIZE_PROMPT.format
```

<a id="fn-1007ec241d37bd1e"></a>

## truncate_text

源码：[L50](D:/Project/learnLittle/app/rag/rag_summarize.py:50)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按字符上限截取，非正上限不截。作为摘要关闭/失败的本地兜底，不是 Token 截断器。

**输入与签名**

```python
def truncate_text(text: str, max_chars: int) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return raw
return raw[:max_chars]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
len
```

<a id="fn-731976d20fe7ebae"></a>

## _copy_hit

源码：[L57](D:/Project/learnLittle/app/rag/rag_summarize.py:57)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

复制命中字典并只替换 content，让原始命中可供 sources。浅拷贝不递归复制嵌套对象。

**输入与签名**

```python
def _copy_hit(hit: dict, content: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return copied
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
dict
```

<a id="fn-47e9f5f6c0eb3f04"></a>

## _complete_summary

源码：[L63](D:/Project/learnLittle/app/rag/rag_summarize.py:63)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

给调用设置 rag_summary 阶段，使用注入或兼容补全，并限制真实 API 输入切片长度。无 key 返回空，外层决定截断。

**输入与签名**

```python
async def _complete_summary(query: str, document: str, settings: Settings) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return text
return ''
return (await complete_openai_compatible(prompt, settings)).strip()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
set_trace_stage
UsageTimer
(await _injected(query, document)).strip
_injected
timer.finish
str
build_summarize_prompt
truncate_text
(await complete_openai_compatible(prompt, settings)).strip
complete_openai_compatible
```

<a id="fn-9a1f9063810e676b"></a>

## _summarize_one

源码：[L86](D:/Project/learnLittle/app/rag/rag_summarize.py:86)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

处理单个 hit：空内容直接副本，关开关/空返回/异常用截断，否则用摘要。当前非空且开关开就尝试，没有先判断切片足够长。

**输入与签名**

```python
async def _summarize_one(query: str, hit: dict, settings: Settings) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _copy_hit(hit, '')
return _copy_hit(hit, truncate_text(content, max_chars))
return _copy_hit(hit, text)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(hit.get('content') or '').strip
hit.get
_copy_hit
truncate_text
_complete_summary
logger.warning
```

<a id="fn-ef5730d7ff5815aa"></a>

## summarize_hits

源码：[L104](D:/Project/learnLittle/app/rag/rag_summarize.py:104)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

对每个 hit gather 并发摘要并按输入顺序收集副本。原始 hits 不变，便于来源展示与提示内容分开。

**输入与签名**

```python
async def summarize_hits(query: str, hits: list[dict], settings: Settings) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return []
return list(results)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.gather
_summarize_one
list
```
