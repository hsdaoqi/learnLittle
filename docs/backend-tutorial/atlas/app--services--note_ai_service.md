# app/services/note_ai_service.py

[源码](D:/Project/learnLittle/app/services/note_ai_service.py) | [任务流程 04](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

补全/写作/标签建议，输出建议而不自动保存笔记。

## 本文件导航

- [set_note_ai_fn](#fn-36c83f2a954762f8)
- [get_note_ai_fn](#fn-eb10568f0e9d546a)
- [_clip](#fn-dbbb5570ae4acdc8)
- [build_autocomplete_prompt](#fn-31b21e3ef5030f11)
- [build_write_prompt](#fn-39fd44d0e74d868f)
- [build_tag_prompt](#fn-2c80d63812eb2014)
- [parse_tags](#fn-a4570f2d517ec4e4)
- [_complete](#fn-21b55c04ebdc5208)
- [autocomplete](#fn-4915a183da039ba6)
- [write_assist](#fn-bc00c904d254bec1)
- [suggest_tags](#fn-2c2f5bd01a1f0b37)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

CompleteFn = Callable[[str], Awaitable[str]]

_injected: CompleteFn | None = None

WRITE_MODES = ('continue', 'expand', 'summary')
```

<a id="fn-36c83f2a954762f8"></a>

## set_note_ai_fn

源码：[L25](D:/Project/learnLittle/app/services/note_ai_service.py:25)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

替换笔记写作补全的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_note_ai_fn(fn: CompleteFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-eb10568f0e9d546a"></a>

## get_note_ai_fn

源码：[L30](D:/Project/learnLittle/app/services/note_ai_service.py:30)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

返回笔记写作补全当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_note_ai_fn() -> CompleteFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-dbbb5570ae4acdc8"></a>

## _clip

源码：[L34](D:/Project/learnLittle/app/services/note_ai_service.py:34)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

按上限截取输入文本，为模型提示控制长度。只截字符串，不按 Token 精确预算。

**输入与签名**

```python
def _clip(text: str, limit: int) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return text
return text[:limit]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
len
```

<a id="fn-31b21e3ef5030f11"></a>

## build_autocomplete_prompt

源码：[L41](D:/Project/learnLittle/app/services/note_ai_service.py:41)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

用光标位置分割正文，截前文/后文并约束只续写。当前前文取切片前 1200 字，不一定是离光标最近的末尾 1200。

**输入与签名**

```python
def build_autocomplete_prompt(content: str, cursor_position: int) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'你在给一篇笔记做内联补全。只输出光标处接下来要写的一小段，不要重复已有正文，不要解释，不要加引号。\n\n光标前：\n{prefix}\n\n光标后：\n{suffix}\n\n补全：'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
max
min
len
_clip
```

<a id="fn-39fd44d0e74d868f"></a>

## build_write_prompt

源码：[L54](D:/Project/learnLittle/app/services/note_ai_service.py:54)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

按 continue/expand/summary 模式生成写作要求，并限制输入正文长度。返回 prompt，不调用模型。

**输入与签名**

```python
def build_write_prompt(content: str, mode: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'{instruction}\n\n原文：\n{body}\n\n结果：'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_clip
```

<a id="fn-2c80d63812eb2014"></a>

## build_tag_prompt

源码：[L65](D:/Project/learnLittle/app/services/note_ai_service.py:65)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

把标题和正文放入标签建议提示，要求有限数量短标签。最终格式仍需 parse_tags 校验。

**输入与签名**

```python
def build_tag_prompt(title: str, content: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'根据笔记标题和正文生成 1 到 5 个短标签。只输出逗号分隔的标签，不要编号，不要解释。\n\n标题：{_clip(title, 200)}\n\n正文：{_clip(content, 2000)}\n\n标签：'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_clip
```

<a id="fn-a4570f2d517ec4e4"></a>

## parse_tags

源码：[L75](D:/Project/learnLittle/app/services/note_ai_service.py:75)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

解析模型返回的 JSON/分隔文本，去空、大小写去重并限制数量和长度。返回建议数组，不写 Note.tags。

**输入与签名**

```python
def parse_tags(raw: str) -> list[str]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return tags
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
re.split
set
part.strip().lstrip('#').strip
part.strip().lstrip
part.strip
tag.lower
seen.add
tags.append
len
```

<a id="fn-21b55c04ebdc5208"></a>

## _complete

源码：[L90](D:/Project/learnLittle/app/services/note_ai_service.py:90)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

优先注入写作模型，再用配置 API，记录耗时/用量；缺 key 或失败返回空。容错是建议为空，不是自动离线生成。

**输入与签名**

```python
async def _complete(prompt: str, settings: Settings) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return text
return (await complete_openai_compatible(prompt, settings)).strip()
return ''
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

<a id="fn-4915a183da039ba6"></a>

## autocomplete

源码：[L108](D:/Project/learnLittle/app/services/note_ai_service.py:108)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

构造光标补全提示并调用 _complete，返回续写文字。不会修改数据库正文。

**输入与签名**

```python
async def autocomplete(content: str, cursor_position: int=0, settings: Settings | None=None) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await _complete(build_autocomplete_prompt(content, cursor_position), settings)
return ''
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
_complete
build_autocomplete_prompt
logger.warning
```

<a id="fn-bc00c904d254bec1"></a>

## write_assist

源码：[L117](D:/Project/learnLittle/app/services/note_ai_service.py:117)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

根据模式构造提示并返回写作结果。接受结果需要调用普通笔记更新。

**输入与签名**

```python
async def write_assist(content: str, mode: str='continue', settings: Settings | None=None) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return text
return ''
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
_complete
build_write_prompt
logger.warning
```

<a id="fn-2c2f5bd01a1f0b37"></a>

## suggest_tags

源码：[L129](D:/Project/learnLittle/app/services/note_ai_service.py:129)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

发标签提示后调用 parse_tags 得到干净标签列表。建议与保存分离，失败可为空列表。

**输入与签名**

```python
async def suggest_tags(title: str, content: str, settings: Settings | None=None) -> list[str]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return parse_tags(raw)
return []
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
_complete
build_tag_prompt
parse_tags
logger.warning
```
