# app/rag/text_splitter.py

[源码](D:/Project/learnLittle/app/rag/text_splitter.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

标题/段落/字符滑窗切片与 TextChunk 结构。

## 本文件导航

- [TextSplitter.__init__](#fn-e263beb5291bf644)
- [TextSplitter.split](#fn-c442ed6a555b5f1f)
- [TextSplitter._split_markdown](#fn-e90dfa57cdc285ce)
- [TextSplitter._parse_sections](#fn-6367f7672fb19d53)
- [TextSplitter._split_generic](#fn-4eed756c66d5b9b3)
- [TextSplitter._window](#fn-db6e8d42a5949bb5)

## 类与字段

### TextChunk

切片纯数据，保存正文、章节名、序号；dataclass 生成的方法不计为手写函数。

声明位置：[L13](D:/Project/learnLittle/app/rag/text_splitter.py:13)。父类：`无显式父类`。

```python
content: str

section_title: str = ''

chunk_index: int = 0
```

### TextSplitter

持有字符 size/overlap 的切分器，显式方法在函数详解内。

声明位置：[L22](D:/Project/learnLittle/app/rag/text_splitter.py:22)。父类：`无显式父类`。


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
_HEADING_RE = re.compile('^(#{1,4})\\s+(.+)$', re.MULTILINE)
```

<a id="fn-e263beb5291bf644"></a>

## TextSplitter.__init__

源码：[L23](D:/Project/learnLittle/app/rag/text_splitter.py:23)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

保存并规范 chunk_size/overlap，使窗口参数可用。数值单位是字符，不是模型 Token。

**输入与签名**

```python
def __init__(self, chunk_size: int=400, chunk_overlap: int=80)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
ValueError
```

<a id="fn-c442ed6a555b5f1f"></a>

## TextSplitter.split

源码：[L31](D:/Project/learnLittle/app/rag/text_splitter.py:31)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

根据文本和文档类型选择 Markdown 标题分段或普通段落分段，过滤空项并统一编号，返回 TextChunk 列表。空白资料不会凭空造切片。

**输入与签名**

```python
def split(self, text: str, doc_type: str='txt') -> list[TextChunk]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return []
return chunks
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(text or '').strip
doc_type.lower().replace
doc_type.lower
self._split_markdown
TextChunk
self._split_generic
c.content.strip
enumerate
```

<a id="fn-e90dfa57cdc285ce"></a>

## TextSplitter._split_markdown

源码：[L47](D:/Project/learnLittle/app/rag/text_splitter.py:47)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

先解析标题章节，再将章节正文按通用规则切片并携带 section_title。保留章节来源而不是只按固定偏移硬切整文。

**输入与签名**

```python
def _split_markdown(self, text: str) -> list[TextChunk]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [TextChunk(content=c) for c in self._split_generic(text)]
return result
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._parse_sections
TextChunk
self._split_generic
text[section['start']:section['end']].strip
result.append
```

<a id="fn-6367f7672fb19d53"></a>

## TextSplitter._parse_sections

源码：[L61](D:/Project/learnLittle/app/rag/text_splitter.py:61)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

识别一至四级 Markdown 标题，收集对应正文，返回章节序列。不是完整 Markdown AST 解析器。

**输入与签名**

```python
def _parse_sections(self, text: str) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return []
return sections
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
m.start
len
m.group
m.group(2).strip
_HEADING_RE.finditer
text[:headings[0][0]].strip
sections.append
enumerate
```

<a id="fn-4eed756c66d5b9b3"></a>

## TextSplitter._split_generic

源码：[L82](D:/Project/learnLittle/app/rag/text_splitter.py:82)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按空行分段，合并可容纳短段，长段交滑窗，产出文字块。相邻短段拼成的块不保证都有 overlap。

**输入与签名**

```python
def _split_generic(self, text: str) -> list[str]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return self._window(text)
return pieces
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
p.strip
re.split
self._window
len
pieces.append
pieces.extend
f'{buf}\n\n{para}'.strip
```

<a id="fn-db6e8d42a5949bb5"></a>

## TextSplitter._window

源码：[L106](D:/Project/learnLittle/app/rag/text_splitter.py:106)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

对长字符串按 size 与 size-overlap 步长取窗口，直到尾部。重叠主要在这里产生，不能推断全部切片有相同重叠。

**输入与签名**

```python
def _window(self, text: str) -> list[str]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [text] if text.strip() else []
return chunks
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
len
text.strip
min
text[start:end].strip
chunks.append
```
