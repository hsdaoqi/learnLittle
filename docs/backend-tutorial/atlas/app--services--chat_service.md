# app/services/chat_service.py

[源码](D:/Project/learnLittle/app/services/chat_service.py) | [任务流程 08](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

会话 CRUD 与消息数据操作；不包含独立问答实现或 query 转发。

## 本文件导航

- [_session_dump](#fn-899362bbceb4d19a)
- [_message_dump](#fn-19c7fbc4d81912fb)
- [_cache_on](#fn-1c75fe61190a78a2)
- [_cache_buffer](#fn-92078dee0dc3e307)
- [_cache_ttl](#fn-b2c371c8ce2cf7f3)
- [list_sessions](#fn-d4b63103831dcdbb)
- [get_session](#fn-e73938602985722c)
- [create_session](#fn-47154b540baac544)
- [update_session_title](#fn-608276a661f90ae5)
- [delete_session](#fn-282ef15f873ec7a5)
- [list_messages](#fn-9714083f25d591e1)
- [_add_message](#fn-34a3eca9a01bd134)
<a id="fn-899362bbceb4d19a"></a>

## _session_dump

源码：[L21](D:/Project/learnLittle/app/services/chat_service.py:21)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

通过 ChatSessionResponse 把 ORM 会话变成可 JSON 输出字典。隐藏 ORM 内部状态，供缓存/HTTP/meta 使用。

**输入与签名**

```python
def _session_dump(session: ChatSession) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ChatSessionResponse.model_validate(session).model_dump(mode='json')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
ChatSessionResponse.model_validate(session).model_dump
ChatSessionResponse.model_validate
```

<a id="fn-19c7fbc4d81912fb"></a>

## _message_dump

源码：[L25](D:/Project/learnLittle/app/services/chat_service.py:25)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

通过 ChatMessageResponse 序列化消息并处理时间字段。幂等键等内部字段是否暴露取决于该响应 Schema。

**输入与签名**

```python
def _message_dump(message: ChatMessage) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ChatMessageResponse.model_validate(message).model_dump(mode='json')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
ChatMessageResponse.model_validate(message).model_dump
ChatMessageResponse.model_validate
```

<a id="fn-1c75fe61190a78a2"></a>

## _cache_on

源码：[L29](D:/Project/learnLittle/app/services/chat_service.py:29)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

读 settings.chat_cache_enabled，无 settings 则默认开启。是兼容调用配置选择，不触发缓存读写。

**输入与签名**

```python
def _cache_on(settings: Settings | None) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return True if settings is None else settings.chat_cache_enabled
```

<a id="fn-92078dee0dc3e307"></a>

## _cache_buffer

源码：[L33](D:/Project/learnLittle/app/services/chat_service.py:33)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

返回 settings 的热消息条数或模块默认条数。这个数只约束热窗口，不约束新主链 SQL 记忆。

**输入与签名**

```python
def _cache_buffer(settings: Settings | None) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return settings.chat_cache_buffer_size if settings else DEFAULT_BUFFER_SIZE
```

<a id="fn-b2c371c8ce2cf7f3"></a>

## _cache_ttl

源码：[L37](D:/Project/learnLittle/app/services/chat_service.py:37)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

返回会话列表 TTL 配置或默认值。不要把它误用于消息 Token 寿命。

**输入与签名**

```python
def _cache_ttl(settings: Settings | None) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return settings.chat_cache_session_ttl_seconds if settings else DEFAULT_SESSION_LIST_TTL
```

<a id="fn-d4b63103831dcdbb"></a>

## list_sessions

源码：[L45](D:/Project/learnLittle/app/services/chat_service.py:45)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

优先读当前用户列表缓存，miss 查询 SQL 按更新时间排序并回填。缓存失败不等于会话丢失。

**输入与签名**

```python
async def list_sessions(db: AsyncSession, user_id: str, settings: Settings | None=None) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return cached
return data
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_cache_on
get_session_list
(await db.execute(select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()))).scalars().all
(await db.execute(select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()))).scalars
db.execute
select(ChatSession).where(ChatSession.user_id == user_id).order_by
select(ChatSession).where
select
ChatSession.updated_at.desc
_session_dump
set_session_list
_cache_ttl
```

<a id="fn-e73938602985722c"></a>

## get_session

源码：[L69](D:/Project/learnLittle/app/services/chat_service.py:69)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

用 session_id 和 user_id 校验会话归属，失败抛 SESSION_NOT_FOUND。新旧聊天、改名、删除和消息列表共用。

**输入与签名**

```python
async def get_session(db: AsyncSession, user_id: str, session_id: str) -> ChatSession
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return session
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id))).scalar_one_or_none
db.execute
select(ChatSession).where
select
BusinessError
```

<a id="fn-47154b540baac544"></a>

## create_session

源码：[L83](D:/Project/learnLittle/app/services/chat_service.py:83)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

创建会话并 flush/refresh，按开关使用户列表缓存失效。返回实体不 commit，新主链传 uncached 避免提前缓存变更。

**输入与签名**

```python
async def create_session(db: AsyncSession, user_id: str, title: str='新对话', settings: Settings | None=None) -> ChatSession
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return session
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
ChatSession
db.add
db.flush
db.refresh
_cache_on
invalidate_session_list
```

<a id="fn-608276a661f90ae5"></a>

## update_session_title

源码：[L98](D:/Project/learnLittle/app/services/chat_service.py:98)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

校验归属后写标题和 title_manual=True，刷新并失效缓存。手动标记用于阻止后台模型覆盖。

**输入与签名**

```python
async def update_session_title(db: AsyncSession, user_id: str, session_id: str, title: str, settings: Settings | None=None) -> ChatSession
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return session
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_session
db.flush
db.refresh
_cache_on
invalidate_session_list
```

<a id="fn-282ef15f873ec7a5"></a>

## delete_session

源码：[L115](D:/Project/learnLittle/app/services/chat_service.py:115)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

查权限后删除会话并 flush，再清列表与消息缓存。SQL 关联删除行为由 ORM/FK 定义，缓存操作本身不在 SQL 事务内。

**输入与签名**

```python
async def delete_session(db: AsyncSession, user_id: str, session_id: str, settings: Settings | None=None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_session
db.delete
db.flush
_cache_on
invalidate_session_list
delete_messages
```

<a id="fn-9714083f25d591e1"></a>

## list_messages

源码：[L126](D:/Project/learnLittle/app/services/chat_service.py:126)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

先验证会话用户，再从 SQL 按时间/ID 返回完整消息。不是只返回 Redis 最近 N 条。

**输入与签名**

```python
async def list_messages(db: AsyncSession, user_id: str, session_id: str) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [_message_dump(m) for m in rows]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_session
(await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc()))).scalars().all
(await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc()))).scalars
db.execute
select(ChatMessage).where(ChatMessage.session_id == session_id).order_by
select(ChatMessage).where
select
ChatMessage.created_at.asc
ChatMessage.id.asc
_message_dump
```

<a id="fn-34a3eca9a01bd134"></a>

## _add_message

源码：[L142](D:/Project/learnLittle/app/services/chat_service.py:142)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

添加 ChatMessage、flush/refresh，可按开关提前推热缓存；不 commit。新 query 特意传关闭缓存 settings，在自身 commit 后再缓存。

**输入与签名**

```python
async def _add_message(db: AsyncSession, session_id: str, role: str, content: str, settings: Settings | None=None, idempotency_key: str | None=None) -> ChatMessage
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return message
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
ChatMessage
db.add
db.flush
db.refresh
_cache_on
push_message
_cache_buffer
```
