# app/routers/note_router.py

[源码](D:/Project/learnLittle/app/routers/note_router.py) | [任务流程 03](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

笔记 CRUD、批量、搜索及写作/邮件入口；静态路径在动态 note_id 路由前注册。

## 本文件导航

- [create_note](#fn-13346af089d570b0)
- [list_notes](#fn-b2aaf13668f61855)
- [recycle_bin](#fn-2017a8ce25ed2a53)
- [batch_operation](#fn-68b3a0e22bc897d9)
- [search_notes](#fn-e52ce42ef01af1df)
- [autocomplete](#fn-ee9663de4604292f)
- [write_assistant](#fn-729c2c50ab2340f0)
- [auto_tag](#fn-d0e28c46fd784e64)
- [get_note](#fn-8764bfa398eb271a)
- [update_note](#fn-a90694e48c50868f)
- [move_note_to_category](#fn-d1d4ebb316246e30)
- [delete_note](#fn-ae2e2267c13cb11f)
- [restore_note](#fn-f446077766fb84c1)
- [export_note_email](#fn-c6cb2130d7922a64)
- [permanent_delete_note](#fn-25b4d373a001698b)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
router = APIRouter()
```

<a id="fn-13346af089d570b0"></a>

## create_note

源码：[L49](D:/Project/learnLittle/app/routers/note_router.py:49)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

接 NoteCreate 和已鉴权用户，调用 service，返回新笔记 ID/标题/格式/时间。路由不手写切片/embedding，commit 由依赖完成。

**输入与签名**

```python
async def create_note(data: NoteCreate, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/note', summary='创建笔记')
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
note_service.create_note
success_response
router.post
```

<a id="fn-b2aaf13668f61855"></a>

## list_notes

源码：[L66](D:/Project/learnLittle/app/routers/note_router.py:66)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

接分类、未分类、关键词与有界分页参数，委托 SQL 列表服务。它不是知识库向量搜索接口。

**输入与签名**

```python
async def list_notes(category_id: str | None=Query(default=None, description='按分类过滤'), uncategorized: bool=Query(default=False, description='只看未分类'), keyword: str | None=Query(default=None, max_length=100, description='标题/内容关键词'), page: int=Query(default=1, ge=1), page_size: int=Query(default=20, ge=1, le=100), user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/note', summary='笔记列表')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=result)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Query
Depends
note_service.list_notes
success_response
router.get
```

<a id="fn-2017a8ce25ed2a53"></a>

## recycle_bin

源码：[L90](D:/Project/learnLittle/app/routers/note_router.py:90)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

调用笔记 service 返回当前用户软删笔记列表及保留天数，包装成功响应。仅展示，不在读取时清掉过期项。

**输入与签名**

```python
async def recycle_bin(user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/note/recycle-bin', summary='回收站列表')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=await note_service.list_recycle_bin(db, user_id))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
success_response
note_service.list_recycle_bin
router.get
```

<a id="fn-68b3a0e22bc897d9"></a>

## batch_operation

源码：[L98](D:/Project/learnLittle/app/routers/note_router.py:98)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

接操作与 ID 集合，委托 batch_notes，包装成功/失败数量和逐项结果。不是每条独立数据库事务。

**输入与签名**

```python
async def batch_operation(data: NoteBatchRequest, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/note/batch', summary='批量操作笔记')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=result, message=f'批量操作完成：成功 {result['success_count']} 篇，失败 {result['error_count']} 篇')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_service.batch_notes
success_response
router.post
```

<a id="fn-e52ce42ef01af1df"></a>

## search_notes

源码：[L111](D:/Project/learnLittle/app/routers/note_router.py:111)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

把 query/top_k 交关键词搜索，返回结果信封。此路由走 FULLTEXT/LIKE，不调用聊天 Agent。

**输入与签名**

```python
async def search_notes(data: NoteSearchRequest, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/note/search', summary='关键词搜索笔记')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=await note_service.keyword_search(db, user_id, data.query, data.top_k))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
success_response
note_service.keyword_search
router.post
```

<a id="fn-ee9663de4604292f"></a>

## autocomplete

源码：[L122](D:/Project/learnLittle/app/routers/note_router.py:122)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

为当前用户设置 note_ai 计量上下文，调用补全并 finally 清除，返回 completion。不会自动保存正文。

**输入与签名**

```python
async def autocomplete(data: AutocompleteRequest, user_id: str=Depends(get_current_user_id))
```

装饰器/挂载：

```python
@router.post('/note/autocomplete', summary='AI 内联补全')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'completion': text})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
usage_service.set_trace_context
note_ai_service.autocomplete
usage_service.clear_trace_context
success_response
router.post
```

<a id="fn-729c2c50ab2340f0"></a>

## write_assistant

源码：[L135](D:/Project/learnLittle/app/routers/note_router.py:135)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

设置/清理计量上下文，按 mode 获取写作结果。返回建议，不把 result 直接写进笔记。

**输入与签名**

```python
async def write_assistant(data: WriteAssistantRequest, user_id: str=Depends(get_current_user_id))
```

装饰器/挂载：

```python
@router.post('/note/write-assistant', summary='AI 写作辅助')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'result': text})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
usage_service.set_trace_context
note_ai_service.write_assist
usage_service.clear_trace_context
success_response
router.post
```

<a id="fn-d0e28c46fd784e64"></a>

## auto_tag

源码：[L148](D:/Project/learnLittle/app/routers/note_router.py:148)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

在 note_ai 计量范围调用标签建议，返回 tags。没有更新 Note.tags 的数据库副作用。

**输入与签名**

```python
async def auto_tag(data: AutoTagRequest, user_id: str=Depends(get_current_user_id))
```

装饰器/挂载：

```python
@router.post('/note/auto-tag', summary='AI 自动打标签')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'tags': tags})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
usage_service.set_trace_context
note_ai_service.suggest_tags
usage_service.clear_trace_context
success_response
router.post
```

<a id="fn-8764bfa398eb271a"></a>

## get_note

源码：[L161](D:/Project/learnLittle/app/routers/note_router.py:161)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

读当前用户活跃笔记并用 NoteResponse 序列化。被软删或不属于用户都不能作为正常详情访问。

**输入与签名**

```python
async def get_note(note_id: str, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/note/{note_id}', summary='笔记详情')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=NoteResponse.model_validate(note).model_dump(mode='json'))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_service.get_active_note
success_response
NoteResponse.model_validate(note).model_dump
NoteResponse.model_validate
router.get
```

<a id="fn-a90694e48c50868f"></a>

## update_note

源码：[L173](D:/Project/learnLittle/app/routers/note_router.py:173)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

用 exclude_unset=True 提取显式字段，交 service 更新，再响应序列化。省略 category_id 与显式 null 语义不同。

**输入与签名**

```python
async def update_note(note_id: str, data: NoteUpdate, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.put('/note/{note_id}', summary='更新笔记')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=NoteResponse.model_validate(note).model_dump(mode='json'))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_service.update_note
data.model_dump
success_response
NoteResponse.model_validate(note).model_dump
NoteResponse.model_validate
router.put
```

<a id="fn-d1d4ebb316246e30"></a>

## move_note_to_category

源码：[L188](D:/Project/learnLittle/app/routers/note_router.py:188)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

把 note_id 与可空分类 ID 交 move_note，再返回更新后的 NoteResponse。只修改分类，不手动重建正文向量。

**输入与签名**

```python
async def move_note_to_category(note_id: str, data: NoteMoveRequest, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.put('/note/{note_id}/category', summary='移动笔记到分类')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=NoteResponse.model_validate(note).model_dump(mode='json'))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_service.move_note
success_response
NoteResponse.model_validate(note).model_dump
NoteResponse.model_validate
router.put
```

<a id="fn-ae2e2267c13cb11f"></a>

## delete_note

源码：[L201](D:/Project/learnLittle/app/routers/note_router.py:201)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

把当前用户与 note_id 交给软删除服务，完成后返回已移入回收站说明。不是物理删除正文，仍可在保留期内恢复。

**输入与签名**

```python
async def delete_note(note_id: str, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.delete('/note/{note_id}', summary='删除笔记（移入回收站）')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='已移入回收站')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_service.soft_delete_note
success_response
router.delete
```

<a id="fn-f446077766fb84c1"></a>

## restore_note

源码：[L211](D:/Project/learnLittle/app/routers/note_router.py:211)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

委托恢复当前用户已删笔记并返回成功。索引恢复在事务提交后进行。

**输入与签名**

```python
async def restore_note(note_id: str, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/note/{note_id}/restore', summary='从回收站恢复')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='已恢复')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_service.restore_note
success_response
router.post
```

<a id="fn-c6cb2130d7922a64"></a>

## export_note_email

源码：[L221](D:/Project/learnLittle/app/routers/note_router.py:221)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

校验笔记归属，优先请求收件人否则用户邮箱，生成附件并发信，发送错误转业务错误。普通邮件导出已存在，不等于 Agent 发邮件工具存在。

**输入与签名**

```python
async def export_note_email(note_id: str, data: NoteExportEmailRequest, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/note/{note_id}/export-email', summary='把笔记发到邮箱')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='已发送', data={'to': to, 'filename': attachment['filename']})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
note_service.get_active_note
(await db.execute(select(User).where(User.uuid == user_id))).scalar_one_or_none
db.execute
select(User).where
select
BusinessError
email_service.note_attachment
email_service.send_email
success_response
router.post
```

<a id="fn-25b4d373a001698b"></a>

## permanent_delete_note

源码：[L257](D:/Project/learnLittle/app/routers/note_router.py:257)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

按配置增加专属删除额度检查，再委托物理删笔记。不可恢复，且 service 当前允许直接永久删活跃笔记。

**输入与签名**

```python
async def permanent_delete_note(note_id: str, request: Request, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.delete('/note/{note_id}/permanent', summary='彻底删除笔记')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='已彻底删除')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
check_named_limit
note_service.permanent_delete_note
success_response
router.delete
```
