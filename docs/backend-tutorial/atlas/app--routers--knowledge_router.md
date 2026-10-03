# app/routers/knowledge_router.py

[源码](D:/Project/learnLittle/app/routers/knowledge_router.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

知识文档上传 SSE、元数据列表/详情/删除与直接检索。

## 本文件导航

- [upload_document](#fn-e2694f302932b637)
- [upload_document.event_generator](#fn-9da29cf8189d8ffb)
- [list_documents](#fn-80fdedbb1211075c)
- [search_documents](#fn-07bd6285396bf44c)
- [get_document](#fn-ce1be621c67ddb9f)
- [delete_document](#fn-96bd823dbdb03db5)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

router = APIRouter()
```

<a id="fn-e2694f302932b637"></a>

## upload_document

源码：[L34](D:/Project/learnLittle/app/routers/knowledge_router.py:34)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

流开始前受限读、校验大小/扩展名/重复，随后建立独立进度生成器返回 SSE。早期错误仍是普通 HTTP 错误。

**输入与签名**

```python
async def upload_document(request: Request, file: UploadFile=File(...), user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/knowledge/upload', summary='上传知识库文档（SSE 进度）')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return StreamingResponse(event_generator(), media_type='text/event-stream', headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
File
Depends
BusinessError
read_upload_limited
validate_upload_file
len
calculate_md5_bytes
knowledge_service.find_duplicate
StreamingResponse
event_generator
router.post
```

<a id="fn-9da29cf8189d8ffb"></a>

## upload_document.event_generator

源码：[L54](D:/Project/learnLittle/app/routers/knowledge_router.py:54)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

独立 session 消费保存文档 service 的进度，在 completed 后 commit，再发 finish；错误 rollback 并按流协议通知。文件/向量不是 SQL 回滚的一部分。

**输入与签名**

```python
async def event_generator()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield event
yield knowledge_service.sse_event({'event_type': 'finish'})
yield knowledge_service.sse_event({'event_type': 'error', 'message': '文档处理失败，请稍后重试'})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
session_factory
knowledge_service.iter_save_document
session.commit
knowledge_service.sse_event
session.rollback
logger.exception
```

<a id="fn-80fdedbb1211075c"></a>

## list_documents

源码：[L87](D:/Project/learnLittle/app/routers/knowledge_router.py:87)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

将当前用户交文档列表 service，返回其 documents/total，当前没有分页。不会直接遍历文件目录作为权限依据。

**输入与签名**

```python
async def list_documents(user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/knowledge/documents', summary='文档列表')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=await knowledge_service.list_documents(db, user_id))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
success_response
knowledge_service.list_documents
router.get
```

<a id="fn-07bd6285396bf44c"></a>

## search_documents

源码：[L95](D:/Project/learnLittle/app/routers/knowledge_router.py:95)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

接查询和 top_k，直接搜索用户知识库并包装结果。没有聊天门控/摘要/Agent。

**输入与签名**

```python
async def search_documents(q: str=Query(..., min_length=1, max_length=200, description='检索词'), top_k: int=Query(default=5, ge=1, le=20), user_id: str=Depends(get_current_user_id))
```

装饰器/挂载：

```python
@router.get('/knowledge/search', summary='检索知识库')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=KnowledgeSearchResponse(items=items, total=len(items)).model_dump())
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Query
Depends
knowledge_service.search_documents
success_response
KnowledgeSearchResponse(items=items, total=len(items)).model_dump
KnowledgeSearchResponse
len
router.get
```

<a id="fn-ce1be621c67ddb9f"></a>

## get_document

源码：[L107](D:/Project/learnLittle/app/routers/knowledge_router.py:107)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按文档 ID 和用户加载 SQL 元数据并转响应。不能猜 ID 越权读取。

**输入与签名**

```python
async def get_document(doc_id: int, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/knowledge/documents/{doc_id}', summary='文档详情')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=KnowledgeDocumentResponse.model_validate(doc).model_dump(mode='json'))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
knowledge_service.get_document
success_response
KnowledgeDocumentResponse.model_validate(doc).model_dump
KnowledgeDocumentResponse.model_validate
router.get
```

<a id="fn-96bd823dbdb03db5"></a>

## delete_document

源码：[L119](D:/Project/learnLittle/app/routers/knowledge_router.py:119)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

委托权限检查后的文档删除，涉及文件/向量/SQL。正常 SQL 提交由依赖完成，外部动作不原子。

**输入与签名**

```python
async def delete_document(doc_id: int, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.delete('/knowledge/documents/{doc_id}', summary='删除文档')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='文档已删除')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
knowledge_service.delete_document
success_response
router.delete
```
