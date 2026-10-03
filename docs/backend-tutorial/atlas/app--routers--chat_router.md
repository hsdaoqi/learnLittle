# app/routers/chat_router.py

[源码](D:/Project/learnLittle/app/routers/chat_router.py) | [任务流程 06](D:/Project/learnLittle/docs/backend-tutorial/06-query.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

唯一 query 聊天入口和会话管理；直接调用 query_service，没有旧问答兼容链。

## 本文件导航

- [chat_query](#fn-9d58286f8de6f069)
- [list_sessions](#fn-8fd17b1046cd4e38)
- [update_title](#fn-2d503a19d7c653cf)
- [delete_session](#fn-25cc4597be48de4b)
- [list_messages](#fn-c951016cbfcf4f1d)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
router = APIRouter()
```

<a id="fn-9d58286f8de6f069"></a>

## chat_query

源码：[L21](D:/Project/learnLittle/app/routers/chat_router.py:21)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

唯一主聊天 HTTP 入口，校验 QueryRequest 与聊天身份后返回 SSE，直接调用 query_service.stream_query。HTTP 状态成功不等于整个后续流一定成功。

**输入与签名**

```python
async def chat_query(request: Request, data: QueryRequest, user_id: str=Depends(get_chat_user_id))
```

装饰器/挂载：

```python
@router.post('/chat/query', summary='ReAct 流式对话')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return StreamingResponse(query_service.stream_query(request.app.state.db_session_factory, user_id, data, settings), media_type='text/event-stream', headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'X-Accel-Buffering': 'n ... [截短，完整见源码]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
StreamingResponse
query_service.stream_query
router.post
```

<a id="fn-8fd17b1046cd4e38"></a>

## list_sessions

源码：[L41](D:/Project/learnLittle/app/routers/chat_router.py:41)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

按用户调用会话列表服务，允许短期缓存。返回会话元数据不是所有消息。

**输入与签名**

```python
async def list_sessions(request: Request, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/chat/sessions', summary='会话列表')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=await chat_service.list_sessions(db, user_id, request.app.state.settings))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
success_response
chat_service.list_sessions
router.get
```

<a id="fn-2d503a19d7c653cf"></a>

## update_title

源码：[L52](D:/Project/learnLittle/app/routers/chat_router.py:52)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

把用户改名请求交 service，设置手动保护并返回会话数据。后台标题不能再覆盖这个标记。

**输入与签名**

```python
async def update_title(request: Request, session_id: str, data: ChatSessionTitleUpdate, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.put('/chat/sessions/{session_id}/title', summary='修改会话标题')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'id': session.id, 'title': session.title})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
chat_service.update_session_title
success_response
router.put
```

<a id="fn-25cc4597be48de4b"></a>

## delete_session

源码：[L66](D:/Project/learnLittle/app/routers/chat_router.py:66)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

校验用户归属后删除会话及缓存，返回统一响应。不是删除用户全部会话。

**输入与签名**

```python
async def delete_session(request: Request, session_id: str, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.delete('/chat/sessions/{session_id}', summary='删除会话')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='会话已删除')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
chat_service.delete_session
success_response
router.delete
```

<a id="fn-c951016cbfcf4f1d"></a>

## list_messages

源码：[L79](D:/Project/learnLittle/app/routers/chat_router.py:79)；任务：[第 06 章](D:/Project/learnLittle/docs/backend-tutorial/06-query.md)。

按 session_id 查完整 SQL 消息列表，先经过会话权限校验。没有 Redis 20 条截断限制。

**输入与签名**

```python
async def list_messages(session_id: str, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/chat/sessions/{session_id}/messages', summary='消息历史')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=await chat_service.list_messages(db, user_id, session_id))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
success_response
chat_service.list_messages
router.get
```
