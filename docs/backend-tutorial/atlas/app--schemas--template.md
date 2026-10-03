# app/schemas/template.py

[源码](D:/Project/learnLittle/app/schemas/template.py) | [任务流程 04](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

模板创建、部分更新、应用和响应契约。

## 本文件导航

本文件没有显式函数；请看下方结构声明，不计作遗漏。

## 类与字段

### NoteTemplateCreate

Pydantic 数据契约，声明 name、content_structure、category、sort_order。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L8](D:/Project/learnLittle/app/schemas/template.py:8)。父类：`BaseModel`。

```python
name: str = Field(min_length=1, max_length=200)

content_structure: dict | None = None

category: str | None = Field(default=None, max_length=100)

sort_order: int = Field(default=0, ge=0)
```

### NoteTemplateUpdate

Pydantic 数据契约，声明 name、content_structure、category、sort_order。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L15](D:/Project/learnLittle/app/schemas/template.py:15)。父类：`BaseModel`。

```python
name: str | None = Field(default=None, min_length=1, max_length=200)

content_structure: dict | None = None

category: str | None = Field(default=None, max_length=100)

sort_order: int | None = Field(default=None, ge=0)
```

### NoteTemplateApply

Pydantic 数据契约，声明 title、category_id、format。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L22](D:/Project/learnLittle/app/schemas/template.py:22)。父类：`BaseModel`。

```python
title: str | None = Field(default=None, min_length=1, max_length=500)

category_id: str | None = Field(default=None, max_length=36)

format: str = Field(default='md', pattern='^(md|txt)$')
```

### NoteTemplateResponse

Pydantic 数据契约，声明 id、name、content_structure、category、sort_order、created_at、updated_at。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L30](D:/Project/learnLittle/app/schemas/template.py:30)。父类：`BaseModel`。

```python
id: int

name: str

content_structure: dict | None = None

category: str | None = None

sort_order: int

created_at: datetime

updated_at: datetime

model_config = {'from_attributes': True}
```
