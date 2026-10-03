# app/schemas/chat.py

[源码](D:/Project/learnLittle/app/schemas/chat.py) | [任务流程 06](D:/Project/learnLittle/docs/backend-tutorial/06-query.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

QueryRequest 与公开会话/消息响应；附件 ID 当前只用于 thinking 互斥。

## 本文件导航

本文件没有显式函数；请看下方结构声明，不计作遗漏。

## 类与字段

### QueryRequest

Pydantic 数据契约，声明 idempotency_key、session_id、message、top_k、enable_thinking、attachment_ids。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L8](D:/Project/learnLittle/app/schemas/chat.py:8)。父类：`BaseModel`。

```python
idempotency_key: str | None = Field(default=None, min_length=1, max_length=128)

session_id: str | None = Field(default=None, description='为空则创建新会话')

message: str = Field(min_length=1, max_length=20000)

top_k: int = Field(default=5, ge=1, le=10)

enable_thinking: bool = Field(default=False, description='深度思考；只作用于主问答模型。分类器 / 计划由环境变量独立控制')

attachment_ids: list[str] = Field(default_factory=list, max_length=8, description='附件 ID。本阶段不解析多模态，非空时自动关闭主模型深度思考')
```

### ChatSessionResponse

Pydantic 数据契约，声明 id、title、created_at、updated_at。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L24](D:/Project/learnLittle/app/schemas/chat.py:24)。父类：`BaseModel`。

```python
id: str

title: str

created_at: datetime

updated_at: datetime

model_config = {'from_attributes': True}
```

### ChatMessageResponse

Pydantic 数据契约，声明 id、session_id、role、content、created_at。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L33](D:/Project/learnLittle/app/schemas/chat.py:33)。父类：`BaseModel`。

```python
id: int

session_id: str

role: str

content: str

created_at: datetime

model_config = {'from_attributes': True}
```

### ChatSessionTitleUpdate

Pydantic 数据契约，声明 title。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L43](D:/Project/learnLittle/app/schemas/chat.py:43)。父类：`BaseModel`。

```python
title: str = Field(min_length=1, max_length=200)
```
