# app/models/knowledge.py

[源码](D:/Project/learnLittle/app/models/knowledge.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

knowledge_documents 文件路径、MD5、类型和切片数；旧头注释的 chunk_count=0 已过时。

## 本文件导航

- [KnowledgeDocument.__repr__](#fn-c39ac8f2bb04ae6e)

## 类与字段

### KnowledgeDocument

原文件元数据和存储路径，chunk_count 为实际切片数，正文切片另存 Chroma。

声明位置：[L15](D:/Project/learnLittle/app/models/knowledge.py:15)。父类：`Base`。

```python
__tablename__ = 'knowledge_documents'

id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False, index=True)

filename: Mapped[str] = mapped_column(String(500), nullable=False)

file_path: Mapped[str] = mapped_column(String(1000), nullable=False)

file_size: Mapped[int] = mapped_column(Integer, nullable=False)

file_type: Mapped[str] = mapped_column(String(100), nullable=False)

md5_hash: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default='0')

created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```

<a id="fn-c39ac8f2bb04ae6e"></a>

## KnowledgeDocument.__repr__

源码：[L33](D:/Project/learnLittle/app/models/knowledge.py:33)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

KnowledgeDocument 的调试字符串表示，返回 `f'<KnowledgeDocument(id={self.id}, filename={self.filename})>'`。用于日志/交互查看，不是 API Schema 序列化，也不查询或提交数据库。

**输入与签名**

```python
def __repr__(self) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'<KnowledgeDocument(id={self.id}, filename={self.filename})>'
```
