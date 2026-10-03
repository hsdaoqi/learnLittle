# app/services/note_template_service.py

[源码](D:/Project/learnLittle/app/services/note_template_service.py) | [任务流程 04](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

模板 CRUD 与应用为普通笔记，复用笔记生命周期。

## 本文件导航

- [_not_found](#fn-09a2a597a3bd0edc)
- [body_from_structure](#fn-a3e73287f641648e)
- [create_template](#fn-aeab6fe2f810f2df)
- [list_templates](#fn-9a2baeae7738a430)
- [get_template](#fn-4e639f675007c896)
- [update_template](#fn-09fb937b132fda71)
- [delete_template](#fn-e29d720d1a7503de)
- [apply_template](#fn-05ffb53ba35f27ec)
<a id="fn-09a2a597a3bd0edc"></a>

## _not_found

源码：[L13](D:/Project/learnLittle/app/services/note_template_service.py:13)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

统一模板不存在/无权访问的业务错误。避免根据 ID 读到其他用户模板。

**输入与签名**

```python
def _not_found() -> BusinessError
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return BusinessError(code=ErrorCode.TEMPLATE_NOT_FOUND, http_status=404)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
BusinessError
```

<a id="fn-a3e73287f641648e"></a>

## body_from_structure

源码：[L17](D:/Project/learnLittle/app/services/note_template_service.py:17)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

按 markdown/content/body 顺序找可用字符串正文，否则返回空。模板结构是 JSON，不自动执行其中代码或完整模板语言。

**输入与签名**

```python
def body_from_structure(structure: dict | None) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ''
return value
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
structure.get
isinstance
```

<a id="fn-aeab6fe2f810f2df"></a>

## create_template

源码：[L28](D:/Project/learnLittle/app/services/note_template_service.py:28)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

按 Schema 数据创建当前用户模板，flush/refresh 后返回实体。模板 category 是文字分类，不是 NoteCategory 外键。

**输入与签名**

```python
async def create_template(db: AsyncSession, user_id: str, data: NoteTemplateCreate) -> NoteTemplate
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return template
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
NoteTemplate
db.add
db.flush
db.refresh
```

<a id="fn-9a2baeae7738a430"></a>

## list_templates

源码：[L42](D:/Project/learnLittle/app/services/note_template_service.py:42)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

查询当前用户全部模板，按 sort_order 升序、创建时间倒序返回实体列表，当前没有分类筛选参数。只读骨架，不创建笔记或修改已应用的正文。

**输入与签名**

```python
async def list_templates(db: AsyncSession, user_id: str) -> list[NoteTemplate]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return list(result.scalars().all())
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
db.execute
select(NoteTemplate).where(NoteTemplate.user_id == user_id).order_by
select(NoteTemplate).where
select
NoteTemplate.sort_order.asc
NoteTemplate.created_at.desc
list
result.scalars().all
result.scalars
```

<a id="fn-4e639f675007c896"></a>

## get_template

源码：[L51](D:/Project/learnLittle/app/services/note_template_service.py:51)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

按模板 ID 与用户定位单项，缺失抛业务异常。应用模板与更新删除都复用这个权限入口。

**输入与签名**

```python
async def get_template(db: AsyncSession, user_id: str, template_id: int) -> NoteTemplate
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return template
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(NoteTemplate).where(NoteTemplate.id == template_id, NoteTemplate.user_id == user_id))).scalar_one_or_none
db.execute
select(NoteTemplate).where
select
_not_found
```

<a id="fn-09fb937b132fda71"></a>

## update_template

源码：[L65](D:/Project/learnLittle/app/services/note_template_service.py:65)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

加载有权限模板后仅更新给定字段并刷新。修改模板不会反向修改已生成笔记。

**输入与签名**

```python
async def update_template(db: AsyncSession, user_id: str, template_id: int, data: NoteTemplateUpdate) -> NoteTemplate
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return template
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_template
data.model_dump(exclude_unset=True).items
data.model_dump
setattr
db.flush
db.refresh
```

<a id="fn-e29d720d1a7503de"></a>

## delete_template

源码：[L76](D:/Project/learnLittle/app/services/note_template_service.py:76)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

加载当前用户模板并删除 SQL 实体。已用模板创建的笔记独立存在。

**输入与签名**

```python
async def delete_template(db: AsyncSession, user_id: str, template_id: int) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_template
db.delete
db.flush
```

<a id="fn-05ffb53ba35f27ec"></a>

## apply_template

源码：[L82](D:/Project/learnLittle/app/services/note_template_service.py:82)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

取模板正文与默认/覆盖标题，组 NoteCreate 并委托普通笔记创建。复用回顾记录和提交后向量索引，而非直接绕过 service 写表。

**输入与签名**

```python
async def apply_template(db: AsyncSession, user_id: str, template_id: int, data: NoteTemplateApply)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return note
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_template
note_service.create_note
NoteCreate
body_from_structure
```
