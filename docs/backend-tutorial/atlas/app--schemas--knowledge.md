# app/schemas/knowledge.py

[源码](D:/Project/learnLittle/app/schemas/knowledge.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

文档响应不暴露本地路径，搜索 hit 限定公开字段。

## 本文件导航

本文件没有显式函数；请看下方结构声明，不计作遗漏。

## 类与字段

### KnowledgeDocumentResponse

Pydantic 数据契约，声明 id、filename、file_size、file_type、md5_hash、chunk_count、created_at、updated_at。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L8](D:/Project/learnLittle/app/schemas/knowledge.py:8)。父类：`BaseModel`。

```python
id: int

filename: str

file_size: int

file_type: str

md5_hash: str

chunk_count: int

created_at: datetime

updated_at: datetime

model_config = {'from_attributes': True}
```

### KnowledgeDocumentListResponse

Pydantic 数据契约，声明 documents、total。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L23](D:/Project/learnLittle/app/schemas/knowledge.py:23)。父类：`BaseModel`。

```python
documents: list[KnowledgeDocumentResponse]

total: int
```

### KnowledgeSearchHit

Pydantic 数据契约，声明 content、score、document_id、filename、section_title、chunk_index。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L28](D:/Project/learnLittle/app/schemas/knowledge.py:28)。父类：`BaseModel`。

```python
content: str

score: float

document_id: int

filename: str

section_title: str = ''

chunk_index: int = 0
```

### KnowledgeSearchResponse

Pydantic 数据契约，声明 items、total。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L37](D:/Project/learnLittle/app/schemas/knowledge.py:37)。父类：`BaseModel`。

```python
items: list[KnowledgeSearchHit]

total: int
```
