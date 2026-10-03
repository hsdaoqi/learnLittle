# app/models/review.py

[源码](D:/Project/learnLittle/app/models/review.py) | [任务流程 04](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

review_records 每笔记唯一，保留当前进度/下次时间和最近完成时间。

## 本文件导航

- [ReviewRecord.__repr__](#fn-68d4f94e5aae13fa)

## 类与字段

### ReviewRecord

note_id 唯一，表示每笔记当前复习状态；reviewed_at 仅最后一次，不是事件日志。

声明位置：[L15](D:/Project/learnLittle/app/models/review.py:15)。父类：`Base`。

```python
__tablename__ = 'review_records'

__table_args__ = (UniqueConstraint('note_id', name='uq_review_records_note_id'),)

id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

note_id: Mapped[str] = mapped_column(String(36), ForeignKey('notes.id', ondelete='CASCADE'), nullable=False, index=True)

user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False, index=True)

review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

interval_days: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

quality: Mapped[int | None] = mapped_column(Integer, nullable=True)

next_review_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```

<a id="fn-68d4f94e5aae13fa"></a>

## ReviewRecord.__repr__

源码：[L46](D:/Project/learnLittle/app/models/review.py:46)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

ReviewRecord 的调试字符串表示，返回 `f'<ReviewRecord(id={self.id}, note_id={self.note_id})>'`。用于日志/交互查看，不是 API Schema 序列化，也不查询或提交数据库。

**输入与签名**

```python
def __repr__(self) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'<ReviewRecord(id={self.id}, note_id={self.note_id})>'
```
