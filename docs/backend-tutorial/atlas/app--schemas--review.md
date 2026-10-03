# app/schemas/review.py

[源码](D:/Project/learnLittle/app/schemas/review.py) | [任务流程 04](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

待复习项目、完成响应、统计与 0..5 的质量字段。

## 本文件导航

本文件没有显式函数；请看下方结构声明，不计作遗漏。

## 类与字段

### ReviewItem

Pydantic 数据契约，声明 review_id、note_id、note_title、note_content、review_count、interval_days、next_review_at。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L8](D:/Project/learnLittle/app/schemas/review.py:8)。父类：`BaseModel`。

```python
review_id: int

note_id: str

note_title: str

note_content: str

review_count: int

interval_days: int

next_review_at: datetime
```

### ReviewCompleteResponse

Pydantic 数据契约，声明 review_id、next_review_at、interval_days、review_count。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L18](D:/Project/learnLittle/app/schemas/review.py:18)。父类：`BaseModel`。

```python
review_id: int

next_review_at: datetime

interval_days: int

review_count: int
```

### ReviewStats

Pydantic 数据契约，声明 pending_today、total_reviews、completed_today、streak_days。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L25](D:/Project/learnLittle/app/schemas/review.py:25)。父类：`BaseModel`。

```python
pending_today: int

total_reviews: int

completed_today: int

streak_days: int
```

### ReviewCompleteQuery

Pydantic 数据契约，声明 quality。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L32](D:/Project/learnLittle/app/schemas/review.py:32)。父类：`BaseModel`。

```python
quality: int = Field(default=3, ge=0, le=5)
```
