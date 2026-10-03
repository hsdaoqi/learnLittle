# app/rag/note_cards.py

[源码](D:/Project/learnLittle/app/rag/note_cards.py) | [任务流程 08](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

带真实 note_id 的搜索文本和用户引用块解析。

## 本文件导航

- [one_line](#fn-839d65a0f6f6ad67)
- [format_note_search_cards](#fn-cbdc8198667bd0ef)
- [visible_question](#fn-e4261370438b3302)
- [referenced_notes_prompt](#fn-d06af0275d85df30)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
CONTEXT_MARKER = '以下是用户引用的笔记'

REF_BLOCK_RE = re.compile('<referenced_notes>\\s*.*?\\s*</referenced_notes>', re.DOTALL)
```

<a id="fn-839d65a0f6f6ad67"></a>

## one_line

源码：[L15](D:/Project/learnLittle/app/rag/note_cards.py:15)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

把摘要空白压成一行并限制长度。保证工具卡片文本不会被正文换行打乱。

**输入与签名**

```python
def one_line(text: str, max_chars: int=30) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return collapsed
return collapsed[:max_chars].rstrip() + '…'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
' '.join
(text or '').split
len
collapsed[:max_chars].rstrip
```

<a id="fn-cbdc8198667bd0ef"></a>

## format_note_search_cards

源码：[L22](D:/Project/learnLittle/app/rag/note_cards.py:22)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

把搜索结果变成包含序号、标题、note_id、摘要的固定文本，空列表给未找到说明。保留 ID 使后续读取全文能定位真实笔记。

**输入与签名**

```python
def format_note_search_cards(query: str, items: list[dict]) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '未找到相关笔记'
return '\n'.join(lines)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(query or '').strip
len
enumerate
(item.get('title') or '未命名').strip
item.get
(item.get('note_id') or '').strip
one_line
lines.append
'\n'.join
```

<a id="fn-e4261370438b3302"></a>

## visible_question

源码：[L41](D:/Project/learnLittle/app/rag/note_cards.py:41)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

移除附带的笔记引用块，得到本轮真正问题，用于标题、分类和检索。原 raw 仍可保存，不是在 SQL 中删内容。

**输入与签名**

```python
def visible_question(message: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return text.strip()
return prefix or text.strip()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
text.find
text.strip
re.sub('\\s*[-—–]+\\s*$', '', prefix).strip
re.sub
```

<a id="fn-d06af0275d85df30"></a>

## referenced_notes_prompt

源码：[L52](D:/Project/learnLittle/app/rag/note_cards.py:52)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

识别用户附带引用并提取适合 Agent 提示的上下文，无引用返回空。引用是上下文材料，不能代替工具所有权检查。

**输入与签名**

```python
def referenced_notes_prompt(message: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ''
return text.strip()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
REF_BLOCK_RE.search
text.strip
```
