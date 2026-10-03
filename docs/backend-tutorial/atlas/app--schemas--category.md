# app/schemas/category.py

[源码](D:/Project/learnLittle/app/schemas/category.py) | [任务流程 03](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

分类创建/改名/移动/排序/批量参数；Schema 不能代替数据库所有权检查。

## 本文件导航

- [CategoryBatchRequest.validate_merge](#fn-c3ba61f77ca907bd)

## 类与字段

### CategoryCreate

Pydantic 数据契约，声明 name、parent_id、icon、color。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L9](D:/Project/learnLittle/app/schemas/category.py:9)。父类：`BaseModel`。

```python
name: str = Field(min_length=1, max_length=100, description='分类名')

parent_id: str | None = Field(default=None, max_length=36, description='父分类 ID，空为顶级')

icon: str | None = Field(default=None, max_length=50, description='图标（emoji 或图标名）')

color: str | None = Field(default=None, max_length=20, description='颜色（十六进制）')
```

### CategoryUpdate

Pydantic 数据契约，声明 name、icon、color。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L18](D:/Project/learnLittle/app/schemas/category.py:18)。父类：`BaseModel`。

```python
name: str = Field(min_length=1, max_length=100, description='分类名')

icon: str | None = Field(default=None, max_length=50)

color: str | None = Field(default=None, max_length=20)
```

### CategoryMoveRequest

Pydantic 数据契约，声明 parent_id。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L26](D:/Project/learnLittle/app/schemas/category.py:26)。父类：`BaseModel`。

```python
parent_id: str | None = Field(default=None, max_length=36, description='新父分类 ID，空为顶级')
```

### CategoryReorderRequest

Pydantic 数据契约，声明 parent_id、ordered_ids。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L32](D:/Project/learnLittle/app/schemas/category.py:32)。父类：`BaseModel`。

```python
parent_id: str | None = Field(default=None, max_length=36, description='父分类 ID，空为顶级')

ordered_ids: list[str] = Field(min_length=1, description='该父级下全部分类 ID，按新顺序')
```

### CategoryBatchRequest

Pydantic 数据契约，声明 category_ids、operation、merge_target_id。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L39](D:/Project/learnLittle/app/schemas/category.py:39)。父类：`BaseModel`。

```python
category_ids: list[str] = Field(min_length=1)

operation: Literal['delete', 'merge', 'permanent_delete', 'restore']

merge_target_id: str | None = Field(default=None, max_length=36)
```

### DeletedCategoryResponse

Pydantic 数据契约，声明 id、name、icon、color、parent_id、deleted_at、days_remaining、descendant_count。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L53](D:/Project/learnLittle/app/schemas/category.py:53)。父类：`BaseModel`。

```python
id: str

name: str

icon: str | None = None

color: str | None = None

parent_id: str | None = None

deleted_at: datetime

days_remaining: int

descendant_count: int = 0
```

<a id="fn-c3ba61f77ca907bd"></a>

## CategoryBatchRequest.validate_merge

源码：[L45](D:/Project/learnLittle/app/schemas/category.py:45)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

在 merge 操作时要求目标分类并约束来源列表等字段关系。树环、归属和深度仍由 service 校验，不由 Schema 推断数据库状态。

**输入与签名**

```python
def validate_merge(self)
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
ValueError
model_validator
```
