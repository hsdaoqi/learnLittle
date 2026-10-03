# app/rag/session_title.py

[源码](D:/Project/learnLittle/app/rag/session_title.py) | [任务流程 08](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

标题文本生成/清洗/失败兜底，写库竞争保护在 query_service。

## 本文件导航

- [set_title_fn](#fn-943b78e0925026d2)
- [get_title_fn](#fn-3a7eadcc0eace41c)
- [build_title_prompt](#fn-024f90cda70e1ac9)
- [fallback_title](#fn-c970a57261e42106)
- [sanitize_title](#fn-a0575ce17a8b9a9b)
- [generate_session_title](#fn-9eb6c9e6dbc901a2)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

DEFAULT_TITLE = '新对话'

TitleFn = Callable[[str], Awaitable[str]]

_injected: TitleFn | None = None

_QUOTE_RE = re.compile('^[\\\'"「」『』《》]+|[\\\'"「」『』《》]+$')
```

<a id="fn-943b78e0925026d2"></a>

## set_title_fn

源码：[L26](D:/Project/learnLittle/app/rag/session_title.py:26)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

替换会话标题生成的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_title_fn(fn: TitleFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-3a7eadcc0eace41c"></a>

## get_title_fn

源码：[L31](D:/Project/learnLittle/app/rag/session_title.py:31)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

返回会话标题生成当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_title_fn() -> TitleFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-024f90cda70e1ac9"></a>

## build_title_prompt

源码：[L35](D:/Project/learnLittle/app/rag/session_title.py:35)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

要求模型依据问题生成短标题且不加说明。提示里的二十字目标不等于严格程序约束，后面还要 sanitize。

**输入与签名**

```python
def build_title_prompt(question: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'请根据以下用户问题，生成一个不超过20字的会话标题。\n\n问题：{question}\n\n要求：\n- 不超过20个字\n- 用用户的语言\n- 不加引号\n- 概括问题主题\n- 不要解释你在做什么，只输出标题本身\n\n标题：'
```

<a id="fn-c970a57261e42106"></a>

## fallback_title

源码：[L49](D:/Project/learnLittle/app/rag/session_title.py:49)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

压平问句空白并按长度取短标题，空问题返回默认新对话。没有模型也能得到可用占位。

**输入与签名**

```python
def fallback_title(question: str, max_chars: int=40) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return DEFAULT_TITLE
return text[:max(1, max_chars)]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
' '.join
(question or '').strip().split
(question or '').strip
max
```

<a id="fn-a0575ce17a8b9a9b"></a>

## sanitize_title

源码：[L56](D:/Project/learnLittle/app/rag/session_title.py:56)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

清外层引号与空白并按 max_chars 截断，清空后回 fallback。只清标题文本，不判断是否允许覆盖数据库标题。

**输入与签名**

```python
def sanitize_title(raw: str, *, max_chars: int, fallback: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return fallback
return text[:max_chars]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
' '.join
(raw or '').strip().split
(raw or '').strip
_QUOTE_RE.sub('', text).strip
_QUOTE_RE.sub
```

<a id="fn-9eb6c9e6dbc901a2"></a>

## generate_session_title

源码：[L64](D:/Project/learnLittle/app/rag/session_title.py:64)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

优先注入，否则用 title 角色模型；开关关、无 key、异常都回短问句。返回文字，更新资格和竞争保护在 query_service。

**输入与签名**

```python
async def generate_session_title(question: str, settings: Settings) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return DEFAULT_TITLE
return fallback
return cleaned
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
fallback_title
(question or '').strip
set_trace_stage
UsageTimer
_injected
timer.finish
str
complete_openai_compatible
build_title_prompt
settings_for_role
sanitize_title
logger.warning
```
