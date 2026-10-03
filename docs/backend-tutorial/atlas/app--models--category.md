# app/models/category.py

[源码](D:/Project/learnLittle/app/models/category.py) | [任务流程 03](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

note_categories 自引用树，软删除与同级名称规则由 service 维护。

## 本文件导航

- [NoteCategory.<lambda@22:74>](#fn-36f15e2a61278cf8)
- [NoteCategory.__repr__](#fn-05dcc7e4903bb7eb)

## 类与字段

### NoteCategory

自引用 parent_id 表示树，user_id 表示归属，deleted_at 表示软删；三层限制在 service。

声明位置：[L19](D:/Project/learnLittle/app/models/category.py:19)。父类：`Base`。

```python
__tablename__ = 'note_categories'

id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False, index=True)

parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('note_categories.id', ondelete='CASCADE'), nullable=True, index=True)

name: Mapped[str] = mapped_column(String(100), nullable=False)

sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

icon: Mapped[str | None] = mapped_column(String(50), nullable=True)

color: Mapped[str | None] = mapped_column(String(20), nullable=True)

deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```

<a id="fn-36f15e2a61278cf8"></a>

## NoteCategory.<lambda@22:74>

源码：[L22](D:/Project/learnLittle/app/models/category.py:22)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

分类 ID 的延迟默认工厂，每次实际需要默认值时生成 uuid4 字符串。不能改成模块导入时只求值一次。

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

<a id="fn-05dcc7e4903bb7eb"></a>

## NoteCategory.__repr__

源码：[L39](D:/Project/learnLittle/app/models/category.py:39)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

NoteCategory 的调试字符串表示，返回 `f'<NoteCategory(id={self.id}, name={self.name})>'`。用于日志/交互查看，不是 API Schema 序列化，也不查询或提交数据库。

**输入与签名**

```python
def __repr__(self) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'<NoteCategory(id={self.id}, name={self.name})>'
```
