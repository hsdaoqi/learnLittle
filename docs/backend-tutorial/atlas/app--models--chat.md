# app/models/chat.py

[源码](D:/Project/learnLittle/app/models/chat.py) | [任务流程 06](D:/Project/learnLittle/docs/backend-tutorial/06-query.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

会话、消息、里程碑摘要三表；手动标题和用户角色哈希幂等键保护生命周期。

## 本文件导航

- [ChatSession.<lambda@19:46>](#fn-e99af520f2ad7d75)
- [ChatSession.__repr__](#fn-97ad337d52f025bd)
- [ChatMessage.__repr__](#fn-5c46cb061e7e4924)
- [ChatSummary.__repr__](#fn-5c4bde1fc71fa00d)

## 类与字段

### ChatSession

会话归属、标题与更新时间，title_manual 防后台覆盖人工标题。

声明位置：[L15](D:/Project/learnLittle/app/models/chat.py:15)。父类：`Base`。

```python
__tablename__ = 'chat_sessions'

id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False, index=True)

title: Mapped[str] = mapped_column(String(200), nullable=False, server_default='新对话')

title_manual: Mapped[bool] = mapped_column(Boolean, default=False, server_default='0')

created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```

### ChatMessage

消息事实，角色/正文/会话外键和可空唯一防重键；idempotency_key 由用户+角色+客户端 key 哈希。

声明位置：[L42](D:/Project/learnLittle/app/models/chat.py:42)。父类：`Base`。

```python
__tablename__ = 'chat_messages'

id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

session_id: Mapped[str] = mapped_column(String(36), ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False, index=True)

role: Mapped[str] = mapped_column(String(20), nullable=False)

content: Mapped[str] = mapped_column(Text, nullable=False)

idempotency_key: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)

created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
```

### ChatSummary

每会话唯一摘要；last_message_id 是覆盖到的消息 ID，不是消息数量。

声明位置：[L63](D:/Project/learnLittle/app/models/chat.py:63)。父类：`Base`。

```python
__tablename__ = 'chat_summaries'

id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

session_id: Mapped[str] = mapped_column(String(36), ForeignKey('chat_sessions.id', ondelete='CASCADE'), nullable=False, unique=True)

summary_text: Mapped[str] = mapped_column(Text, nullable=False)

last_message_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

token_count: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)

created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```

<a id="fn-e99af520f2ad7d75"></a>

## ChatSession.<lambda@19:46>

源码：[L19](D:/Project/learnLittle/app/models/chat.py:19)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

ChatSession ID 的延迟默认工厂，每个新会话产生独立 UUID。消息 ID 则由数据库自增，不用此函数。

**输入与签名**

```python
lambda: str(uuid.uuid4())
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 str(uuid.uuid4())
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
str
uuid.uuid4
```

<a id="fn-97ad337d52f025bd"></a>

## ChatSession.__repr__

源码：[L38](D:/Project/learnLittle/app/models/chat.py:38)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

ChatSession 的调试字符串表示，返回 `f'<ChatSession(id={self.id}, title={self.title[:20]})>'`。用于日志/交互查看，不是 API Schema 序列化，也不查询或提交数据库。

**输入与签名**

```python
def __repr__(self) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'<ChatSession(id={self.id}, title={self.title[:20]})>'
```

<a id="fn-5c46cb061e7e4924"></a>

## ChatMessage.__repr__

源码：[L59](D:/Project/learnLittle/app/models/chat.py:59)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

ChatMessage 的调试字符串表示，返回 `f'<ChatMessage(id={self.id}, role={self.role})>'`。用于日志/交互查看，不是 API Schema 序列化，也不查询或提交数据库。

**输入与签名**

```python
def __repr__(self) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'<ChatMessage(id={self.id}, role={self.role})>'
```

<a id="fn-5c4bde1fc71fa00d"></a>

## ChatSummary.__repr__

源码：[L86](D:/Project/learnLittle/app/models/chat.py:86)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

ChatSummary 的调试字符串表示，返回 `f'<ChatSummary(session_id={self.session_id}, version={self.version})>'`。用于日志/交互查看，不是 API Schema 序列化，也不查询或提交数据库。

**输入与签名**

```python
def __repr__(self) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'<ChatSummary(session_id={self.session_id}, version={self.version})>'
```
