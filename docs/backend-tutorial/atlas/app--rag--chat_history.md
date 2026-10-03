# app/rag/chat_history.py

[源码](D:/Project/learnLittle/app/rag/chat_history.py) | [任务流程 08](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

SQL 未摘要历史的实际 Token 预算选择，保持消息角色。

## 本文件导航

- [_role_and_content](#fn-673c1ad28e562f3e)
- [rag_context_text](#fn-97019bc2efcfd297)
- [build_agent_history](#fn-f96c66db1a3ef29e)
<a id="fn-673c1ad28e562f3e"></a>

## _role_and_content

源码：[L11](D:/Project/learnLittle/app/rag/chat_history.py:11)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

从字典或对象统一取得 role/content，缺字段用空。当前历史选择据此保留用户/助手角色，而不是先格式化为一段历史字符串。

**输入与签名**

```python
def _role_and_content(item: Any) -> tuple[str, str]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return (item.get('role') or '', item.get('content') or '')
return (getattr(item, 'role', '') or '', getattr(item, 'content', '') or '')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
isinstance
item.get
getattr
```

<a id="fn-97019bc2efcfd297"></a>

## rag_context_text

源码：[L17](D:/Project/learnLittle/app/rag/chat_history.py:17)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

抽出非空 hit.content 并换行连接，生成预算和提示用的参考文本。不是把全部 metadata 都送模型。

**输入与签名**

```python
def rag_context_text(hits: list[dict]) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '\n'.join(parts)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(hit.get('content') or '').strip
hit.get
parts.append
'\n'.join
```

<a id="fn-f96c66db1a3ef29e"></a>

## build_agent_history

源码：[L26](D:/Project/learnLittle/app/rag/chat_history.py:26)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

新主链排除已摘要 ID，保留 user/assistant 原角色，扣问题/摘要/RAG/工具预留后从新往旧取历史。单条超大时逐步缩短，legacy scratchpad<=0 自动预留 4000，不受旧热窗口限制。

**输入与签名**

```python
def build_agent_history(messages: list[Any], settings: Settings, *, rag_text: str='', question: str='', summary: str='', summarized_through: int=0) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return list(reversed(selected))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
max
TokenCounter.count
isinstance
item.get
getattr
_role_and_content
pending.append
reversed
count_message
len
selected.append
list
```
