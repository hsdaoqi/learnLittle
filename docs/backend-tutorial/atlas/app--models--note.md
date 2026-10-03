# app/models/note.py

[源码](D:/Project/learnLittle/app/models/note.py) | [任务流程 03](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

notes 表，正文/格式/标签/分类/置顶和删除时间；向量存在 Chroma 而非这一行。

## 本文件导航

- [Note.<lambda@22:74>](#fn-0b9175ca7a1a2eac)
- [Note.__repr__](#fn-bca5f8de4ad98bd3)

## 类与字段

### Note

笔记事实。category_id 可空、物理分类删除 SET NULL，tags 是 JSON，format 不由更新 Schema 修改。

声明位置：[L19](D:/Project/learnLittle/app/models/note.py:19)。父类：`Base`。

```python
__tablename__ = 'notes'

id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False, index=True)

title: Mapped[str] = mapped_column(String(500), nullable=False)

content: Mapped[str] = mapped_column(Text, nullable=False)

format: Mapped[str] = mapped_column(String(10), nullable=False, server_default='md')

tags: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

category_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('note_categories.id', ondelete='SET NULL'), nullable=True, index=True)

is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```

<a id="fn-0b9175ca7a1a2eac"></a>

## Note.<lambda@22:74>

源码：[L22](D:/Project/learnLittle/app/models/note.py:22)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

笔记 ID 的延迟默认工厂，每条新 Note 独立 UUID。没有用户权限含义，查询仍需 user_id。

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

<a id="fn-bca5f8de4ad98bd3"></a>

## Note.__repr__

源码：[L40](D:/Project/learnLittle/app/models/note.py:40)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

Note 的调试字符串表示，返回 `f'<Note(id={self.id}, title={self.title[:20]})>'`。用于日志/交互查看，不是 API Schema 序列化，也不查询或提交数据库。

**输入与签名**

```python
def __repr__(self) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'<Note(id={self.id}, title={self.title[:20]})>'
```
