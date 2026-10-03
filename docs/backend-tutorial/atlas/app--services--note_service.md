# app/services/note_service.py

[源码](D:/Project/learnLittle/app/services/note_service.py) | [任务流程 03](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

笔记业务权限、SQL 生命周期、关键词检索和提交后向量同步。

## 本文件导航

- [_not_found](#fn-b303fd1c3575735e)
- [_escape_like](#fn-751b0896841c0997)
- [index_note](#fn-2acac9bb358bcca4)
- [drop_note_vectors](#fn-511977c3e9fd5739)
- [_try_index](#fn-d575e28aa57c2be7)
- [defer_note_index](#fn-243fb2ca37dc3b1a)
- [defer_note_index.sync_latest](#fn-16b3986482df277a)
- [ensure_category](#fn-a4406d42a888115e)
- [create_note](#fn-5ef02ba740c59d16)
- [get_active_note](#fn-1e870eb8c96b0efb)
- [list_notes](#fn-b3781105bae8033e)
- [_note_hit](#fn-8585d2d92f003b09)
- [_like_search](#fn-559e3559eb39d93a)
- [keyword_search](#fn-e675069055f6c9dd)
- [update_note](#fn-46baf290d95ab305)
- [soft_delete_note](#fn-930a27db3fa2ac3e)
- [list_recycle_bin](#fn-223b51d995a88e92)
- [move_note](#fn-225b6ec26df7f255)
- [batch_notes](#fn-0b94f552036ce65a)
- [cleanup_expired_notes](#fn-5ef6f5272f1e53b9)
- [restore_note](#fn-15d9e900bf07083b)
- [permanent_delete_note](#fn-d57ce306ae56196d)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)
```

<a id="fn-b303fd1c3575735e"></a>

## _not_found

源码：[L29](D:/Project/learnLittle/app/services/note_service.py:29)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

生成统一笔记不存在业务错误，供权限/删除状态过滤失败时使用。避免通过不同响应泄露别人的笔记是否存在。

**输入与签名**

```python
def _not_found() -> BusinessError
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return BusinessError(code=ErrorCode.NOTE_NOT_FOUND, http_status=404)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
BusinessError
```

<a id="fn-751b0896841c0997"></a>

## _escape_like

源码：[L33](D:/Project/learnLittle/app/services/note_service.py:33)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

转义 LIKE 特殊符号，使关键词中的百分号和下划线按字面匹配。它不是 SQL 拼接安全的唯一措施，查询仍使用参数绑定。

**输入与签名**

```python
def _escape_like(keyword: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return keyword.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
keyword.replace('\\', '\\\\').replace('%', '\\%').replace
keyword.replace('\\', '\\\\').replace
keyword.replace
```

<a id="fn-2acac9bb358bcca4"></a>

## index_note

源码：[L38](D:/Project/learnLittle/app/services/note_service.py:38)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

先删旧 note 向量，把标题与正文拼接后检查是否为空，非空则切片写 notes collection 和归属 metadata。有标题而正文为空仍可索引；删除与 upsert 非原子，出错可能暂时缺索引。

**输入与签名**

```python
async def index_note(note: Note) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_vector_store
store.delete_note
f'{note.title}\n\n{note.content}'.strip
get_settings
TextSplitter(settings.chunk_size, settings.chunk_overlap).split
TextSplitter
store.upsert_chunks
```

<a id="fn-511977c3e9fd5739"></a>

## drop_note_vectors

源码：[L68](D:/Project/learnLittle/app/services/note_service.py:68)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

按 note_id 从 notes collection 删除相关切片。只改变向量库，不物理删除 SQL 笔记。

**输入与签名**

```python
def drop_note_vectors(note_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_vector_store().delete_note
get_vector_store
logger.warning
```

<a id="fn-d575e28aa57c2be7"></a>

## _try_index

源码：[L76](D:/Project/learnLittle/app/services/note_service.py:76)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

在索引调用外捕获并记录异常，使派生搜索故障不反向破坏笔记业务提交。失败不等于已经安排持久化重试。

**输入与签名**

```python
async def _try_index(note: Note) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
index_note
logger.warning
```

<a id="fn-243fb2ca37dc3b1a"></a>

## defer_note_index

源码：[L83](D:/Project/learnLittle/app/services/note_service.py:83)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

取会话绑定工厂和笔记身份，向 after_commit 登记同笔记工作。现在不读写 Chroma，避免事务回滚仍留下向量。

**输入与签名**

```python
def defer_note_index(db: AsyncSession, note_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
async_sessionmaker
defer_after_commit
```

<a id="fn-16b3986482df277a"></a>

## defer_note_index.sync_latest

源码：[L87](D:/Project/learnLittle/app/services/note_service.py:87)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

提交后用新 session 重读当前 SQL 笔记；缺失/删除就清向量，否则索引最新内容。同 key 串行配合重读，减少旧任务覆盖新内容，但仅限本进程。

**输入与签名**

```python
async def sync_latest()
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
factory
fresh.get
drop_note_vectors
_try_index
```

<a id="fn-a4406d42a888115e"></a>

## ensure_category

源码：[L98](D:/Project/learnLittle/app/services/note_service.py:98)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

按 ID、当前用户和未删除状态确认分类可挂载，失败抛业务错误。无分类时由调用者跳过此检查，本函数不会把空 ID 当成有效分类。

**输入与签名**

```python
async def ensure_category(db: AsyncSession, user_id: str, category_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(NoteCategory).where(NoteCategory.id == category_id, NoteCategory.user_id == user_id, NoteCategory.deleted_at.is_(None)))).scalar_one_or_none
db.execute
select(NoteCategory).where
select
NoteCategory.deleted_at.is_
BusinessError
```

<a id="fn-5ef02ba740c59d16"></a>

## create_note

源码：[L113](D:/Project/learnLittle/app/services/note_service.py:113)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

验证分类、创建 Note、flush/refresh，再确保回顾记录并登记提交后索引。返回实体，普通路由的 commit 在外层。

**输入与签名**

```python
async def create_note(db: AsyncSession, user_id: str, data: NoteCreate) -> Note
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return note
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
ensure_category
Note
db.add
db.flush
db.refresh
ensure_review_record
defer_note_index
```

<a id="fn-1e870eb8c96b0efb"></a>

## get_active_note

源码：[L137](D:/Project/learnLittle/app/services/note_service.py:137)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

按 note_id/user_id/deleted_at 查询当前用户活跃笔记，缺失抛统一错误。是读取、修改、邮件导出和工具复用的权限关口。

**输入与签名**

```python
async def get_active_note(db: AsyncSession, user_id: str, note_id: str) -> Note
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return note
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(Note).where(Note.id == note_id, Note.user_id == user_id, Note.deleted_at.is_(None)))).scalar_one_or_none
db.execute
select(Note).where
select
Note.deleted_at.is_
_not_found
```

<a id="fn-b3781105bae8033e"></a>

## list_notes

源码：[L152](D:/Project/learnLittle/app/services/note_service.py:152)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

组合分类/未分类/关键词过滤与分页，置顶优先，再按时间等规则排序，返回列表和总数。使用 SQL 元数据，不是语义向量搜索。

**输入与签名**

```python
async def list_notes(db: AsyncSession, user_id: str, *, category_id: str | None=None, uncategorized: bool=False, keyword: str | None=None, page: int=1, page_size: int=20) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'items': [NoteSummary.model_validate(n).model_dump(mode='json') for n in notes], 'total': total, 'page': page, 'page_size': page_size}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
select(Note).where
select
Note.deleted_at.is_
stmt.where
Note.category_id.is_
_escape_like
or_
Note.title.like
Note.content.like
(await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one
db.execute
select(func.count()).select_from
func.count
stmt.subquery
stmt.order_by
Note.is_pinned.desc
Note.updated_at.desc
(await db.execute(stmt.offset((page - 1) * page_size).limit(page_size))).scalars().all
(await db.execute(stmt.offset((page - 1) * page_size).limit(page_size))).scalars
stmt.offset((page - 1) * page_size).limit
stmt.offset
NoteSummary.model_validate(n).model_dump
NoteSummary.model_validate
```

<a id="fn-8585d2d92f003b09"></a>

## _note_hit

源码：[L193](D:/Project/learnLittle/app/services/note_service.py:193)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

把 Note 包装成关键词搜索结果中的 note 摘要与 score。score 是展示排序值，不是统一语义相关概率。

**输入与签名**

```python
def _note_hit(note: Note, score: float) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'note': NoteSummary.model_validate(note).model_dump(mode='json'), 'score': score}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
NoteSummary.model_validate(note).model_dump
NoteSummary.model_validate
```

<a id="fn-559e3559eb39d93a"></a>

## _like_search

源码：[L200](D:/Project/learnLittle/app/services/note_service.py:200)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

分别优先匹配标题再补正文，转义关键词并去重、限 top_k。标题和正文采用不同固定分值用于排序。

**输入与签名**

```python
async def _like_search(db: AsyncSession, user_id: str, keyword: str, top_k: int) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return results
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_escape_like
Note.deleted_at.is_
list
(await db.execute(select(Note).where(*base, Note.title.like(pattern, escape='\\')).order_by(Note.updated_at.desc()).limit(top_k))).scalars().all
(await db.execute(select(Note).where(*base, Note.title.like(pattern, escape='\\')).order_by(Note.updated_at.desc()).limit(top_k))).scalars
db.execute
select(Note).where(*base, Note.title.like(pattern, escape='\\')).order_by(Note.updated_at.desc()).limit
select(Note).where(*base, Note.title.like(pattern, escape='\\')).order_by
select(Note).where
select
Note.title.like
Note.updated_at.desc
_note_hit
len
Note.content.like
conds.append
Note.id.not_in
(await db.execute(select(Note).where(*conds).order_by(Note.updated_at.desc()).limit(remaining))).scalars().all
(await db.execute(select(Note).where(*conds).order_by(Note.updated_at.desc()).limit(remaining))).scalars
select(Note).where(*conds).order_by(Note.updated_at.desc()).limit
select(Note).where(*conds).order_by
results.extend
```

<a id="fn-e675069055f6c9dd"></a>

## keyword_search

源码：[L243](D:/Project/learnLittle/app/services/note_service.py:243)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

整理 query，适用时尝试 MySQL FULLTEXT ngram，异常或不可用退回 LIKE。返回搜索响应字典；迁移 HEAD 不一定保有 FULLTEXT 索引。

**输入与签名**

```python
async def keyword_search(db: AsyncSession, user_id: str, query: str, top_k: int=20) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'query': query, 'results': []}
return {'query': keyword, 'results': [_note_hit(note, 0.9) for note in notes]}
return {'query': keyword, 'results': await _like_search(db, user_id, keyword, top_k)}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(query or '').strip
len
text
list
(await db.execute(select(Note).where(and_(Note.user_id == user_id, Note.deleted_at.is_(None), match_where)).order_by(match_order, Note.updated_at.desc()).limit(top_k), {'kw': keyword})).scalars().all
(await db.execute(select(Note).where(and_(Note.user_id == user_id, Note.deleted_at.is_(None), match_where)).order_by(match_order, Note.updated_at.desc()).limit(top_k), {'kw': keyword})).scalars
db.execute
select(Note).where(and_(Note.user_id == user_id, Note.deleted_at.is_(None), match_where)).order_by(match_order, Note.updated_at.desc()).limit
select(Note).where(and_(Note.user_id == user_id, Note.deleted_at.is_(None), match_where)).order_by
select(Note).where
select
and_
Note.deleted_at.is_
Note.updated_at.desc
_note_hit
logger.warning
type
_like_search
```

<a id="fn-46baf290d95ab305"></a>

## update_note

源码：[L299](D:/Project/learnLittle/app/services/note_service.py:299)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

移除 format，处理显式字段并检查分类，flush/refresh；传入 title/content 字段就登记索引，并不比较新旧值是否相等。category_id 的 null 表示解绑。

**输入与签名**

```python
async def update_note(db: AsyncSession, user_id: str, note_id: str, fields: dict) -> Note
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return note
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_active_note
fields.pop
ensure_category
fields.items
setattr
db.flush
db.refresh
{'title', 'content'}.intersection
defer_note_index
```

<a id="fn-930a27db3fa2ac3e"></a>

## soft_delete_note

源码：[L320](D:/Project/learnLittle/app/services/note_service.py:320)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

加载活跃笔记并设置 deleted_at，安排提交后移除向量。SQL 正文仍保留供回收站恢复。

**输入与签名**

```python
async def soft_delete_note(db: AsyncSession, user_id: str, note_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_active_note
datetime.now
db.flush
defer_note_index
```

<a id="fn-223b51d995a88e92"></a>

## list_recycle_bin

源码：[L328](D:/Project/learnLittle/app/services/note_service.py:328)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

列出当前用户软删笔记和剩余保留天数。不会自动执行物理清理，过期删除另有任务。

**输入与签名**

```python
async def list_recycle_bin(db: AsyncSession, user_id: str) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return items
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(Note).where(Note.user_id == user_id, Note.deleted_at.isnot(None)).order_by(Note.deleted_at.desc()))).scalars().all
(await db.execute(select(Note).where(Note.user_id == user_id, Note.deleted_at.isnot(None)).order_by(Note.deleted_at.desc()))).scalars
db.execute
select(Note).where(Note.user_id == user_id, Note.deleted_at.isnot(None)).order_by
select(Note).where
select
Note.deleted_at.isnot
Note.deleted_at.desc
get_settings
datetime.now
NoteSummary.model_validate(note).model_dump
NoteSummary.model_validate
max
items.append
```

<a id="fn-225b6ec26df7f255"></a>

## move_note

源码：[L351](D:/Project/learnLittle/app/services/note_service.py:351)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

复用更新流程把 category_id 改为目标或 None。分类元数据改变不重新嵌入正文。

**输入与签名**

```python
async def move_note(db: AsyncSession, user_id: str, note_id: str, category_id: str | None) -> Note
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await update_note(db, user_id, note_id, {'category_id': category_id})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
update_note
```

<a id="fn-0b94f552036ce65a"></a>

## batch_notes

源码：[L358](D:/Project/learnLittle/app/services/note_service.py:358)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

按 operation 对每个 ID 执行软删、恢复、永久删、移动或置顶，捕获 BusinessError 记录逐项结果。没有单项 savepoint，不应宣称所有数据库异常都可局部隔离。

**输入与签名**

```python
async def batch_notes(db: AsyncSession, user_id: str, data: NoteBatchRequest) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'operation': data.operation, 'total': len(data.note_ids), 'success_count': len(success_ids), 'error_count': len(errors), 'errors': errors or None}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
soft_delete_note
update_note
move_note
permanent_delete_note
restore_note
success_ids.append
errors.append
len
```

<a id="fn-5ef6f5272f1e53b9"></a>

## cleanup_expired_notes

源码：[L388](D:/Project/learnLittle/app/services/note_service.py:388)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

筛选早于阈值的已删除笔记，物理移除并安排向量清理，返回数量。调用者负责提交；阈值基于 deleted_at 而不是 created_at。

**输入与签名**

```python
async def cleanup_expired_notes(db: AsyncSession, days: int | None=None) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return len(expired)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
datetime.now
timedelta
get_settings
list
(await db.execute(select(Note).where(Note.deleted_at.isnot(None), Note.deleted_at <= cutoff))).scalars().all
(await db.execute(select(Note).where(Note.deleted_at.isnot(None), Note.deleted_at <= cutoff))).scalars
db.execute
select(Note).where
select
Note.deleted_at.isnot
defer_note_index
db.delete
db.flush
len
```

<a id="fn-15d9e900bf07083b"></a>

## restore_note

源码：[L412](D:/Project/learnLittle/app/services/note_service.py:412)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

只加载当前用户已删除笔记，清 deleted_at 并安排重新索引。活跃笔记调用恢复会按不存在处理。

**输入与签名**

```python
async def restore_note(db: AsyncSession, user_id: str, note_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(Note).where(Note.id == note_id, Note.user_id == user_id, Note.deleted_at.isnot(None)))).scalar_one_or_none
db.execute
select(Note).where
select
Note.deleted_at.isnot
_not_found
db.flush
defer_note_index
```

<a id="fn-d57ce306ae56196d"></a>

## permanent_delete_note

源码：[L430](D:/Project/learnLittle/app/services/note_service.py:430)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

按用户定位笔记后物理删除并安排清向量。当前并不要求先在回收站，删除后不能靠 restore 找回。

**输入与签名**

```python
async def permanent_delete_note(db: AsyncSession, user_id: str, note_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(Note).where(Note.id == note_id, Note.user_id == user_id))).scalar_one_or_none
db.execute
select(Note).where
select
_not_found
defer_note_index
db.delete
db.flush
```
