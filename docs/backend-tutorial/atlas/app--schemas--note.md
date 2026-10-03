# app/schemas/note.py

[源码](D:/Project/learnLittle/app/schemas/note.py) | [任务流程 03](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

笔记创建/部分更新/搜索/批量/写作建议的字段限制和响应形状。

## 本文件导航

- [NoteBatchRequest.validate_batch](#fn-40a7ac81366a1ab7)

## 类与字段

### NoteCreate

Pydantic 数据契约，声明 title、content、category_id、tags、format。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L9](D:/Project/learnLittle/app/schemas/note.py:9)。父类：`BaseModel`。

```python
title: str = Field(min_length=1, max_length=500, description='标题')

content: str = Field(description='内容（Markdown 或纯文本）')

category_id: str | None = Field(default=None, max_length=36, description='分类 ID')

tags: list[str] | None = Field(default=None, description='标签数组')

format: str = Field(default='md', pattern='^(md|txt)$', description='文档类型，创建后不可改')
```

### NoteUpdate

Pydantic 数据契约，声明 title、content、category_id、tags、is_pinned。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L19](D:/Project/learnLittle/app/schemas/note.py:19)。父类：`BaseModel`。

```python
title: str | None = Field(default=None, min_length=1, max_length=500)

content: str | None = None

category_id: str | None = Field(default=None, max_length=36, description='移动分类；传 null 移出分类')

tags: list[str] | None = None

is_pinned: bool | None = None
```

### NoteResponse

Pydantic 数据契约，声明 id、title、content、format、tags、category_id、is_pinned、created_at、updated_at。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L29](D:/Project/learnLittle/app/schemas/note.py:29)。父类：`BaseModel`。

```python
id: str

title: str

content: str

format: str

tags: list[str] | None = None

category_id: str | None = None

is_pinned: bool

created_at: datetime

updated_at: datetime

model_config = {'from_attributes': True}
```

### NoteSummary

Pydantic 数据契约，声明 id、title、format、tags、category_id、is_pinned、created_at、updated_at、days_remaining。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L45](D:/Project/learnLittle/app/schemas/note.py:45)。父类：`BaseModel`。

```python
id: str

title: str

format: str

tags: list[str] | None = None

category_id: str | None = None

is_pinned: bool

created_at: datetime

updated_at: datetime

days_remaining: int | None = None

model_config = {'from_attributes': True}
```

### NoteMoveRequest

Pydantic 数据契约，声明 category_id。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L61](D:/Project/learnLittle/app/schemas/note.py:61)。父类：`BaseModel`。

```python
category_id: str | None = Field(default=None, max_length=36)
```

### NoteBatchRequest

Pydantic 数据契约，声明 note_ids、operation、target_category_id。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L67](D:/Project/learnLittle/app/schemas/note.py:67)。父类：`BaseModel`。

```python
note_ids: list[str] = Field(min_length=1)

operation: Literal['delete', 'pin', 'unpin', 'move', 'permanent_delete', 'restore']

target_category_id: str | None = Field(default=None, max_length=36)
```

### NoteSearchRequest

Pydantic 数据契约，声明 query、top_k。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L84](D:/Project/learnLittle/app/schemas/note.py:84)。父类：`BaseModel`。

```python
query: str = Field(min_length=1, max_length=200, description='搜索关键词')

top_k: int = Field(default=20, ge=1, le=50, description='返回条数')
```

### NoteSearchHit

Pydantic 数据契约，声明 note、score。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L89](D:/Project/learnLittle/app/schemas/note.py:89)。父类：`BaseModel`。

```python
note: NoteSummary

score: float
```

### AutocompleteRequest

Pydantic 数据契约，声明 content、cursor_position。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L94](D:/Project/learnLittle/app/schemas/note.py:94)。父类：`BaseModel`。

```python
content: str = Field(default='', description='当前笔记内容')

cursor_position: int = Field(default=0, ge=0)
```

### WriteAssistantRequest

Pydantic 数据契约，声明 content、mode。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L99](D:/Project/learnLittle/app/schemas/note.py:99)。父类：`BaseModel`。

```python
content: str = Field(default='', description='笔记内容')

mode: str = Field(default='continue', pattern='^(continue|expand|summary)$')
```

### AutoTagRequest

Pydantic 数据契约，声明 title、content。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L104](D:/Project/learnLittle/app/schemas/note.py:104)。父类：`BaseModel`。

```python
title: str = Field(default='', max_length=500)

content: str = Field(default='')
```

<a id="fn-40a7ac81366a1ab7"></a>

## NoteBatchRequest.validate_batch

源码：[L73](D:/Project/learnLittle/app/schemas/note.py:73)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

限制一次 permanent_delete 最多 50 项、restore 最多 100 项；move 分支允许 None 且不做额外检查。不能假设它强制显式提供目标分类。

**输入与签名**

```python
def validate_batch(self)
```

装饰器/挂载：

```python
@model_validator(mode='after')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return self
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
len
ValueError
model_validator
```
