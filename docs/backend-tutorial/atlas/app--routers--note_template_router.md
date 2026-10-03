# app/routers/note_template_router.py

[源码](D:/Project/learnLittle/app/routers/note_template_router.py) | [任务流程 04](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

模板 HTTP CRUD 和套用创建入口。

## 本文件导航

- [_dump](#fn-4966975abf247f59)
- [create_template](#fn-70ac9490eea8547b)
- [list_templates](#fn-b972dd81f31ff437)
- [get_template](#fn-8ce45f62c20d2908)
- [update_template](#fn-b9d2cf20a858b1dc)
- [delete_template](#fn-72e5f97aaf4795d8)
- [apply_template](#fn-c84ddb681e94153d)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
router = APIRouter()
```

<a id="fn-4966975abf247f59"></a>

## _dump

源码：[L28](D:/Project/learnLittle/app/routers/note_template_router.py:28)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

把模板 ORM 转为 NoteTemplateResponse 的 JSON 形状。避免把 SQLAlchemy 内部属性直接塞响应。

**输入与签名**

```python
def _dump(template) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return NoteTemplateResponse.model_validate(template).model_dump(mode='json')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
NoteTemplateResponse.model_validate(template).model_dump
NoteTemplateResponse.model_validate
```

<a id="fn-70ac9490eea8547b"></a>

## create_template

源码：[L33](D:/Project/learnLittle/app/routers/note_template_router.py:33)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

校验请求并创建用户模板，序列化返回。只保存模板，不创建笔记。

**输入与签名**

```python
async def create_template(data: NoteTemplateCreate, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/note-template', summary='创建模板')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=_dump(template))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_template_service.create_template
success_response
_dump
router.post
```

<a id="fn-b972dd81f31ff437"></a>

## list_templates

源码：[L43](D:/Project/learnLittle/app/routers/note_template_router.py:43)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

传当前用户和筛选给 service，逐项 _dump 返回。模板查询与笔记分类树无直接外键绑定。

**输入与签名**

```python
async def list_templates(user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/note-template', summary='模板列表')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'templates': [_dump(item) for item in templates]})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_template_service.list_templates
success_response
_dump
router.get
```

<a id="fn-8ce45f62c20d2908"></a>

## get_template

源码：[L52](D:/Project/learnLittle/app/routers/note_template_router.py:52)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

通过有权限单项查询取得模板并返回。模板 ID 不是跨用户通行证。

**输入与签名**

```python
async def get_template(template_id: int, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/note-template/{template_id}', summary='模板详情')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=_dump(template))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_template_service.get_template
success_response
_dump
router.get
```

<a id="fn-b9d2cf20a858b1dc"></a>

## update_template

源码：[L62](D:/Project/learnLittle/app/routers/note_template_router.py:62)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

提取显式更新字段，委托模板 service 并返回新状态。不影响已套用模板生成的笔记。

**输入与签名**

```python
async def update_template(template_id: int, data: NoteTemplateUpdate, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.put('/note-template/{template_id}', summary='更新模板')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=_dump(template))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_template_service.update_template
success_response
_dump
router.put
```

<a id="fn-72e5f97aaf4795d8"></a>

## delete_template

源码：[L73](D:/Project/learnLittle/app/routers/note_template_router.py:73)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

委托删除当前用户模板，返回完成说明。不是删除模板曾产生的全部内容。

**输入与签名**

```python
async def delete_template(template_id: int, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.delete('/note-template/{template_id}', summary='删除模板')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='模板已删除')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_template_service.delete_template
success_response
router.delete
```

<a id="fn-c84ddb681e94153d"></a>

## apply_template

源码：[L83](D:/Project/learnLittle/app/routers/note_template_router.py:83)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

读模板并委托创建笔记，返回新笔记标识与信息。回顾/向量生命周期由普通笔记创建继承。

**输入与签名**

```python
async def apply_template(template_id: int, data: NoteTemplateApply, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/note-template/{template_id}/apply', summary='套用模板新建笔记')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'id': note.id, 'title': note.title, 'format': note.format, 'created_at': note.created_at})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_template_service.apply_template
success_response
router.post
```
