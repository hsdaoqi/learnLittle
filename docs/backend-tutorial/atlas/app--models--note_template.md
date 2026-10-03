# app/models/note_template.py

[源码](D:/Project/learnLittle/app/models/note_template.py) | [任务流程 04](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

note_templates 保存用户自定义 JSON 骨架和文字 category。

## 本文件导航

- [NoteTemplate.__repr__](#fn-98b3de7e81b190a6)

## 类与字段

### NoteTemplate

JSON 正文骨架；category 是标签式文字，不是分类树外键。

声明位置：[L15](D:/Project/learnLittle/app/models/note_template.py:15)。父类：`Base`。

```python
__tablename__ = 'note_templates'

id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False, index=True)

name: Mapped[str] = mapped_column(String(200), nullable=False)

content_structure: Mapped[dict | None] = mapped_column(JSON, nullable=True)

category: Mapped[str | None] = mapped_column(String(100), nullable=True)

sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```

<a id="fn-98b3de7e81b190a6"></a>

## NoteTemplate.__repr__

源码：[L31](D:/Project/learnLittle/app/models/note_template.py:31)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

NoteTemplate 的调试字符串表示，返回 `f'<NoteTemplate(id={self.id}, name={self.name})>'`。用于日志/交互查看，不是 API Schema 序列化，也不查询或提交数据库。

**输入与签名**

```python
def __repr__(self) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'<NoteTemplate(id={self.id}, name={self.name})>'
```
