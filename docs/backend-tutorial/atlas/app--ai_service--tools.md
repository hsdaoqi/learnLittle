# app/ai_service/tools.py

[源码](D:/Project/learnLittle/app/ai_service/tools.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

绑定认证用户的内置笔记/回顾工具，写工具自管事务。

## 本文件导航

- [_clip](#fn-142a4800ecdedafb)
- [_resolve_category_id](#fn-f3151cb85f265f93)
- [bind_user_tools](#fn-9d641e4da081318b)
- [bind_user_tools.what_time_is_now](#fn-1af83f3ddc9b4c5d)
- [bind_user_tools.get_user_info_tools](#fn-686b08d172f29020)
- [bind_user_tools.search_notes_tool](#fn-11740a34d047aa33)
- [bind_user_tools.get_note_content_tool](#fn-f2877fb2a17edcab)
- [bind_user_tools.get_note_stats_tool](#fn-f8b8f369e46fee7b)
- [bind_user_tools.get_note_stats_tool.<lambda@159:35>](#fn-3dc8c7b861e87cf6)
- [bind_user_tools.today_reviews](#fn-d85abfe794ec260b)
- [bind_user_tools.mark_reviewed](#fn-9627ce0391abd56a)
- [bind_user_tools.create_note_tool](#fn-7ec78e8d823fab54)
- [bind_user_tools.update_note_tool](#fn-c7d0970828fad2ee)
- [bind_user_tools.get_related_notes_tool](#fn-efa7cd60c1617ca9)
- [_empty_params](#fn-429a64951a45ce8a)
- [register_builtin_tools](#fn-50a554cf65d7b856)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

MAX_NOTE_CHARS = 20000
```

<a id="fn-142a4800ecdedafb"></a>

## _clip

源码：[L31](D:/Project/learnLittle/app/ai_service/tools.py:31)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

为工具输出按字符截长正文并加省略号。限制工具结果尺寸，不是完整上下文 Token 预算。

**输入与签名**

```python
def _clip(text: str, limit: int) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return text
return text[:limit] + '…'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
len
```

<a id="fn-f3151cb85f265f93"></a>

## _resolve_category_id

源码：[L38](D:/Project/learnLittle/app/ai_service/tools.py:38)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按用户、活跃状态和名称找分类，空名/未找到返回 None。不同父级可同名，scalar_one_or_none 在多项命中时存在歧义边界。

**输入与签名**

```python
async def _resolve_category_id(db: AsyncSession, user_id: str, name: str | None) -> str | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
return cat.id if cat else None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
name.strip
(await db.execute(select(NoteCategory).where(NoteCategory.user_id == user_id, NoteCategory.name == name.strip(), NoteCategory.deleted_at.is_(None)))).scalar_one_or_none
db.execute
select(NoteCategory).where
select
NoteCategory.deleted_at.is_
```

<a id="fn-9d641e4da081318b"></a>

## bind_user_tools

源码：[L55](D:/Project/learnLittle/app/ai_service/tools.py:55)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

为当前 user_id/session_factory 建一组闭包并返回名称映射。模型参数不会决定当前用户，每个工具自行管理需要的 session。

**输入与签名**

```python
def bind_user_tools(user_id: str, session_factory) -> dict[str, Callable[..., Any]]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'what_time_is_now': what_time_is_now, 'get_user_info_tools': get_user_info_tools, 'search_notes_tool': search_notes_tool, 'get_note_content_tool': get_note_content_tool, 'get_note_stats_tool': get_note_stats_tool, 'get_today_revi ... [截短，完整见源码]
```

<a id="fn-1af83f3ddc9b4c5d"></a>

## bind_user_tools.what_time_is_now

源码：[L58](D:/Project/learnLittle/app/ai_service/tools.py:58)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

返回服务器本地格式化日期时间。不是从模型记忆推测时间，也不使用用户时区字段。

**输入与签名**

```python
async def what_time_is_now() -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
datetime.now().strftime
datetime.now
```

<a id="fn-686b08d172f29020"></a>

## bind_user_tools.get_user_info_tools

源码：[L61](D:/Project/learnLittle/app/ai_service/tools.py:61)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

独立 session 查当前用户，输出用户名、邮箱和 ID，缺失给兜底文字。不输出密码哈希。

**输入与签名**

```python
async def get_user_info_tools() -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'当前用户 ID: {user_id}（用户信息获取失败）'
return f'用户名: {user.username}\n邮箱: {email}\n用户ID: {user_id}'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
session_factory
(await db.execute(select(User).where(User.uuid == user_id))).scalar_one_or_none
db.execute
select(User).where
select
```

<a id="fn-11740a34d047aa33"></a>

## bind_user_tools.search_notes_tool

源码：[L71](D:/Project/learnLittle/app/ai_service/tools.py:71)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

向量查多片段，回 SQL 校验活跃/归属并按 note_id 去重；无卡片才关键词兜底。返回保留真实 ID 的搜索文本，不把向量残留直接当可访问笔记。

**输入与签名**

```python
async def search_notes_tool(query: str, top_k: int=5) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return format_note_search_cards(query, cards)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
max
min
int
get_vector_store().search
get_vector_store
logger.warning
session_factory
set
item.get
note_service.get_active_note
seen.add
cards.append
len
format_note_search_cards
note_service.keyword_search
data.get
summary.get
```

<a id="fn-f2877fb2a17edcab"></a>

## bind_user_tools.get_note_content_tool

源码：[L117](D:/Project/learnLittle/app/ai_service/tools.py:117)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按真实 note_id 读有权限正文，输出标题/标签/日期和有限长正文，业务不存在转文字。不能仅凭猜到 UUID 越权。

**输入与签名**

```python
async def get_note_content_tool(note_id: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '未找到笔记或无权访问'
return f'# {note.title}\n\n> 标签：{tags} | 更新日期：{updated}\n\n---\n\n{body}'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
session_factory
note_service.get_active_note
','.join
note.updated_at.strftime
_clip
```

<a id="fn-f8b8f369e46fee7b"></a>

## bind_user_tools.get_note_stats_tool

源码：[L130](D:/Project/learnLittle/app/ai_service/tools.py:130)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

SQL 外连接分类统计当前用户活跃笔记，把未分类排末并输出文字。不会把已删除笔记计入活跃总览。

**输入与签名**

```python
async def get_note_stats_tool() -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '暂无笔记'
return '笔记分类统计:\n' + '\n'.join(lines)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
session_factory
func.coalesce(NoteCategory.name, '未分类').label
func.coalesce
list
(await db.execute(select(category_name, func.count().label('note_count')).select_from(Note).outerjoin(NoteCategory, and_(Note.category_id == NoteCategory.id, NoteCategory.deleted_at.is_(None))).where(Note.user_id == user_id, Note.deleted_at.is_(None), Note.category_id.is_(None) | NoteCategory.id.is_not(None)).group_by(NoteCategory.id, NoteCategory.name))).all
db.execute
select(category_name, func.count().label('note_count')).select_from(Note).outerjoin(NoteCategory, and_(Note.category_id == NoteCategory.id, NoteCategory.deleted_at.is_(None))).where(Note.user_id == user_id, Note.deleted_at.is_(None), Note.category_id.is_(None) | NoteCategory.id.is_not(None)).group_by
select(category_name, func.count().label('note_count')).select_from(Note).outerjoin(NoteCategory, and_(Note.category_id == NoteCategory.id, NoteCategory.deleted_at.is_(None))).where
select(category_name, func.count().label('note_count')).select_from(Note).outerjoin
select(category_name, func.count().label('note_count')).select_from
select
func.count().label
func.count
and_
NoteCategory.deleted_at.is_
Note.deleted_at.is_
Note.category_id.is_
NoteCategory.id.is_not
sorted
'\n'.join
```

<a id="fn-3dc8c7b861e87cf6"></a>

## bind_user_tools.get_note_stats_tool.<lambda@159:35>

源码：[L159](D:/Project/learnLittle/app/ai_service/tools.py:159)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

统计排序 key：未分类返回 True、其他 False，升序时未分类靠后。只改变输出顺序，不修改分类。

**输入与签名**

```python
lambda r: r[0] == "未分类"
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 r[0] == '未分类'
```

<a id="fn-d85abfe794ec260b"></a>

## bind_user_tools.today_reviews

源码：[L163](D:/Project/learnLittle/app/ai_service/tools.py:163)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

开独立 session 调只读回顾工具并返回文本。无写入所以不 commit 业务状态。

**输入与签名**

```python
async def today_reviews() -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await get_today_reviews_tool(db, user_id)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
session_factory
get_today_reviews_tool
```

<a id="fn-9627ce0391abd56a"></a>

## bind_user_tools.mark_reviewed

源码：[L167](D:/Project/learnLittle/app/ai_service/tools.py:167)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

调用完成回顾适配器并 commit，业务或其他异常 rollback 后返回可读失败。是有副作用工具，外层不能盲目重放。

**输入与签名**

```python
async def mark_reviewed(review_id: int) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return text
return '未找到回顾记录或无权操作'
return '标记回顾失败，请稍后重试'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
session_factory
mark_reviewed_tool
int
db.commit
db.rollback
logger.warning
```

<a id="fn-7ec78e8d823fab54"></a>

## bind_user_tools.create_note_tool

源码：[L181](D:/Project/learnLittle/app/ai_service/tools.py:181)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

解析逗号标签与分类名，组 NoteCreate，复用笔记 service 并自己 commit，返回新 ID/标题。继承提交后索引与回顾记录。

**输入与签名**

```python
async def create_note_tool(title: str, content: str, tags: str='', category: str='') -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'笔记创建成功！ID: {note.id}, 标题: {note.title}'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
part.strip
(tags or '').split
session_factory
_resolve_category_id
note_service.create_note
NoteCreate
db.commit
```

<a id="fn-c7d0970828fad2ee"></a>

## bind_user_tools.update_note_tool

源码：[L197](D:/Project/learnLittle/app/ai_service/tools.py:197)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

仅构建模型实际提供的字段，解析标签/分类后调用笔记更新并 commit，异常 rollback。分类空/找不到可变未分类，不能误以为省略参数等于清空。

**输入与签名**

```python
async def update_note_tool(note_id: str, title: str | None=None, content: str | None=None, tags: str | None=None, category: str | None=None) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '未提供任何要更新的字段'
return f'笔记更新成功！ID: {note.id}, 标题: {note.title}'
return '未找到笔记或无权访问'
return '笔记更新失败，请稍后重试'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
part.strip
tags.split
session_factory
_resolve_category_id
note_service.update_note
db.commit
db.rollback
logger.warning
```

<a id="fn-efa7cd60c1617ca9"></a>

## bind_user_tools.get_related_notes_tool

源码：[L230](D:/Project/learnLittle/app/ai_service/tools.py:230)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

拿 note_title 复用 search_notes_tool 返回相关卡片。不是新增另一套向量算法。

**输入与签名**

```python
async def get_related_notes_tool(note_title: str, top_k: int=3) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await search_notes_tool(note_title, top_k)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
search_notes_tool
```

<a id="fn-429a64951a45ce8a"></a>

## _empty_params

源码：[L247](D:/Project/learnLittle/app/ai_service/tools.py:247)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

返回无参数对象 Schema，并禁止额外字段用于内置工具描述。LangChain 转换器是否完整保留所有 JSON Schema 语义需另看其实现。

**输入与签名**

```python
def _empty_params() -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'type': 'object', 'properties': {}, 'additionalProperties': False}
```

<a id="fn-50a554cf65d7b856"></a>

## register_builtin_tools

源码：[L251](D:/Project/learnLittle/app/ai_service/tools.py:251)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

若已注册关键内置工具则跳过，否则创建时间/用户/读写笔记/回顾描述，标只读 parallel_safe 并登记。导入模块即调用；这里没有注册邮件/PPT 工具。

**输入与签名**

```python
def register_builtin_tools() -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
registry.get
ToolSpec
_empty_params
registry.register
```
