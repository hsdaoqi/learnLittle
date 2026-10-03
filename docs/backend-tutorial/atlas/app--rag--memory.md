# app/rag/memory.py

[源码](D:/Project/learnLittle/app/rag/memory.py) | [任务流程 08](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

按消息检查点增量压缩旧历史，保留近期原文。

## 本文件导航

- [set_summary_fn](#fn-2f79098250682822)
- [get_summary_fn](#fn-e39aca7c0c98e3fa)
- [truncate_summary](#fn-8ba132eaa8523377)
- [format_messages_for_summary](#fn-dda7f3e0dadd30fd)
- [build_summary_prompt](#fn-f511160a7d45f03b)
- [get_summary](#fn-03c3400bfc005142)
- [update_summary](#fn-bef655189d83802c)
- [_complete_summary](#fn-872790baaf53f4bb)
- [check_and_summarize](#fn-c241bb7697d197dd)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

SUMMARY_PROMPT = '你是一个对话摘要助手。请阅读以下信息，生成一段简洁的结构化摘要。\n\n## 已有的历史摘要\n{existing_summary}\n\n## 新增的对话片段（需要融合到摘要中）\n{new_messages}\n\n## 要求\n1. 融合已有摘要和新对话，生成新的完整摘要\n2. 重点保留以下类型的信息：\n   - **关键决策**：用户做了什么技术/业务决策\n   - **用户偏好**：用户表达过的喜好、习惯、要求\n   - **未完成任务**：对话中提到但尚未完成的事项\n   - **重要事实**：用户提供的关键信息\n   - **上下文延续**：可能需要跨轮次引用的信息\n3. 摘要长度控制在 500 字以内\n4. 使用中文\n5. 仅输出摘要文本，不要加任何前缀或解释'

SummaryFn = Callable[[str], Awaitable[str]]

_injected: SummaryFn | None = None
```

<a id="fn-2f79098250682822"></a>

## set_summary_fn

源码：[L52](D:/Project/learnLittle/app/rag/memory.py:52)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

替换历史摘要生成的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_summary_fn(fn: SummaryFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-e39aca7c0c98e3fa"></a>

## get_summary_fn

源码：[L57](D:/Project/learnLittle/app/rag/memory.py:57)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

返回历史摘要生成当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_summary_fn() -> SummaryFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-8ba132eaa8523377"></a>

## truncate_summary

源码：[L61](D:/Project/learnLittle/app/rag/memory.py:61)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

估 Token，超额按比例截字符并尝试在较后句号处结束。近似限制，不是反复精确 tokenizer 截到绝对上限。

**输入与签名**

```python
def truncate_summary(summary: str, max_tokens: int) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ''
return text
return truncated.strip()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(summary or '').strip
TokenCounter.count
max
int
len
truncated.rfind
truncated.strip
```

<a id="fn-dda7f3e0dadd30fd"></a>

## format_messages_for_summary

源码：[L79](D:/Project/learnLittle/app/rag/memory.py:79)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

兼容消息字典/对象，带角色标签并截每条正文后拼接。摘要模型看到的是这些裁剪后的材料，不是完整原数据库。

**输入与签名**

```python
def format_messages_for_summary(messages: list[Any], max_chars: int=300) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '\n\n'.join(lines)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
isinstance
msg.get
getattr
lines.append
'\n\n'.join
```

<a id="fn-f511160a7d45f03b"></a>

## build_summary_prompt

源码：[L99](D:/Project/learnLittle/app/rag/memory.py:99)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

把已有摘要和新的较早消息装入增量融合提示，要求保留事实/偏好/待办。返回提示，不写 ChatSummary。

**输入与签名**

```python
def build_summary_prompt(existing_summary: str, new_messages: list[Any]) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return SUMMARY_PROMPT.format(existing_summary=existing_summary.strip() or '（暂无历史摘要）', new_messages=format_messages_for_summary(new_messages))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
SUMMARY_PROMPT.format
existing_summary.strip
format_messages_for_summary
```

<a id="fn-03c3400bfc005142"></a>

## get_summary

源码：[L106](D:/Project/learnLittle/app/rag/memory.py:106)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

按 session_id 读取至多一条里程碑摘要实体。调用方已确保会话归属，不在这里重新解析 Token。

**输入与签名**

```python
async def get_summary(db: AsyncSession, session_id: str) -> ChatSummary | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return (await db.execute(select(ChatSummary).where(ChatSummary.session_id == session_id))).scalar_one_or_none()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(ChatSummary).where(ChatSummary.session_id == session_id))).scalar_one_or_none
db.execute
select(ChatSummary).where
select
```

<a id="fn-bef655189d83802c"></a>

## update_summary

源码：[L114](D:/Project/learnLittle/app/rag/memory.py:114)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

存在就更新摘要、覆盖 ID、token_count 并加 version，否则新增；flush/refresh 返回实体。commit 由后台包装或旧调用方负责。

**输入与签名**

```python
async def update_summary(db: AsyncSession, session_id: str, summary_text: str, last_message_id: int) -> ChatSummary
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return existing
return row
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_summary
TokenCounter.count
db.flush
db.refresh
ChatSummary
db.add
```

<a id="fn-872790baaf53f4bb"></a>

## _complete_summary

源码：[L140](D:/Project/learnLittle/app/rag/memory.py:140)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

给调用设置 summary 阶段，优先注入并计量，否则调用兼容模型，无 key 空结果。异常交给外层容错保留旧摘要。

**输入与签名**

```python
async def _complete_summary(prompt: str, settings: Settings) -> str
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
(await _injected(prompt)).strip
_injected
timer.finish
str
(await complete_openai_compatible(prompt, settings)).strip
complete_openai_compatible
```

<a id="fn-c241bb7697d197dd"></a>

## check_and_summarize

源码：[L160](D:/Project/learnLittle/app/rag/memory.py:160)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

检查总量/新增间隔，保留最近若干条，只压缩未摘要较早消息并更新覆盖 ID。失败返回已有摘要或 None，不应吞掉已完成问答。

**输入与签名**

```python
async def check_and_summarize(db: AsyncSession, session_id: str, settings: Settings) -> ChatSummary | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await get_summary(db, session_id)
return existing
return await update_summary(db, session_id, new_summary, to_compress[-1].id)
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_summary
(await db.execute(select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session_id))).scalar
db.execute
select(func.count(ChatMessage.id)).where
select
func.count
(await db.execute(select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session_id, ChatMessage.id > last_id))).scalar
list
(await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id, ChatMessage.id > last_id).order_by(ChatMessage.id.asc()))).scalars().all
(await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id, ChatMessage.id > last_id).order_by(ChatMessage.id.asc()))).scalars
select(ChatMessage).where(ChatMessage.session_id == session_id, ChatMessage.id > last_id).order_by
select(ChatMessage).where
ChatMessage.id.asc
max
len
build_summary_prompt
_complete_summary
truncate_summary
update_summary
logger.warning
```
