# app/services/knowledge_service.py

[源码](D:/Project/learnLittle/app/services/knowledge_service.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

文件、SQL 文档记录和 Chroma 切片的上传编排；不具备分布式事务。

## 本文件导航

- [sse_event](#fn-e414f5ac31ee4bba)
- [_processing](#fn-e936d996527e943d)
- [_doc_type](#fn-30eb8cb99ac2970d)
- [find_duplicate](#fn-0f40eaf7e9f37521)
- [_index_chunks](#fn-7737367e08d43af6)
- [iter_save_document](#fn-3ed02d823d067148)
- [list_documents](#fn-a770c8c5ecd2bd67)
- [get_document](#fn-f3026f597a90aaa2)
- [delete_document](#fn-1d1c1e95a6f96a66)
- [search_documents](#fn-8163cb09a9f1933a)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)
```

<a id="fn-e414f5ac31ee4bba"></a>

## sse_event

源码：[L38](D:/Project/learnLittle/app/services/knowledge_service.py:38)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

将字典编码成 data: JSON 加空行的 SSE 帧，类别在 JSON.event_type 中，不是 event: 行。只做编码，不意味着 SQL 已提交。

**输入与签名**

```python
def sse_event(data: dict) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'data: {json.dumps(data, ensure_ascii=False)}\n\n'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
json.dumps
```

<a id="fn-e936d996527e943d"></a>

## _processing

源码：[L42](D:/Project/learnLittle/app/services/knowledge_service.py:42)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

统一生成含当前处理步骤/进度信息的 processing 事件。上传 service 在各阶段调用，便于流消费者观察。

**输入与签名**

```python
def _processing(filename: str, progress: int, stage: str, message: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return sse_event({'event_type': 'processing', 'filename': filename, 'progress': progress, 'stage': stage, 'message': message})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
sse_event
```

<a id="fn-30eb8cb99ac2970d"></a>

## _doc_type

源码：[L54](D:/Project/learnLittle/app/services/knowledge_service.py:54)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

把规范扩展名映射为文档类型。后续解析和模型字段使用这个类型，不从正文猜测业务分类。

**输入与签名**

```python
def _doc_type(filename: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 'md'
return ext or 'txt'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Path(filename).suffix.lower().lstrip
Path(filename).suffix.lower
Path
```

<a id="fn-0f40eaf7e9f37521"></a>

## find_duplicate

源码：[L61](D:/Project/learnLittle/app/services/knowledge_service.py:61)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按用户与文件 MD5 查重复上传记录。不同用户可有相同文件，摘要本身不代替所有权。

**输入与签名**

```python
async def find_duplicate(db: AsyncSession, user_id: str, md5: str) -> KnowledgeDocument | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return (await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.user_id == user_id, KnowledgeDocument.md5_hash == md5))).scalar_one_or_none()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.user_id == user_id, KnowledgeDocument.md5_hash == md5))).scalar_one_or_none
db.execute
select(KnowledgeDocument).where
select
```

<a id="fn-7737367e08d43af6"></a>

## _index_chunks

源码：[L74](D:/Project/learnLittle/app/services/knowledge_service.py:74)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

把切片与文档/user/章节/序号 metadata、稳定 ID 组装后交给向量库。写 Chroma 与 SQL 事务不是同一个提交。

**输入与签名**

```python
async def _index_chunks(doc: KnowledgeDocument, chunks) -> None
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
str
store.upsert_chunks
```

<a id="fn-3ed02d823d067148"></a>

## iter_save_document

源码：[L96](D:/Project/learnLittle/app/services/knowledge_service.py:96)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按落盘、解析、切片、建文档记录、写向量顺序 yield 进度，最后 completed。外层路由才 commit；解析/索引异常有清理逻辑，但不等于所有取消/提交失败都跨介质回滚。

**输入与签名**

```python
async def iter_save_document(db: AsyncSession, *, user_id: str, original_filename: str, content: bytes, declared_type: str | None, settings: Settings, md5: str | None=None) -> AsyncIterator[str]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield _processing(safe_name, 0, 'saving', '正在保存文件...')
yield _processing(safe_name, 20, 'saved', '文件保存完成')
yield _processing(safe_name, 30, 'parsing', '正在解析文档内容...')
yield _processing(safe_name, 50, 'parsed', '文档解析完成')
yield _processing(safe_name, 60, 'splitting', '正在文本切片...')
yield _processing(safe_name, 75, 'splitted', f'文本切片完成，共 {len(chunks)} 个片段')
yield _processing(safe_name, 85, 'vectorizing', '正在向量化...')
yield _processing(safe_name, 100, 'vectorized', '向量化入库完成')
```

另有 1 个出口/断言，完整条件见源码。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
len
validate_upload_file
calculate_md5_bytes
find_duplicate
BusinessError
get_safe_filename
uuid.uuid4
Path
_processing
ensure_dir
str
file_path.write_bytes
parse_document
TextSplitter
splitter.split
_doc_type
KnowledgeDocument
infer_mime
db.add
db.flush
db.refresh
_index_chunks
file_path.unlink
logger.warning
sse_event
KnowledgeDocumentResponse.model_validate(doc).model_dump
KnowledgeDocumentResponse.model_validate
```

<a id="fn-a770c8c5ecd2bd67"></a>

## list_documents

源码：[L172](D:/Project/learnLittle/app/services/knowledge_service.py:172)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按用户筛选文档记录并按创建时间倒序返回 documents/total，当前没有分页参数。读 SQL 元数据，不把 Chroma 切片当上传列表。

**输入与签名**

```python
async def list_documents(db: AsyncSession, user_id: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return KnowledgeDocumentListResponse(documents=[KnowledgeDocumentResponse.model_validate(d) for d in docs], total=len(docs)).model_dump(mode='json')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.user_id == user_id).order_by(KnowledgeDocument.created_at.desc()))).scalars().all
(await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.user_id == user_id).order_by(KnowledgeDocument.created_at.desc()))).scalars
db.execute
select(KnowledgeDocument).where(KnowledgeDocument.user_id == user_id).order_by
select(KnowledgeDocument).where
select
KnowledgeDocument.created_at.desc
list
KnowledgeDocumentListResponse(documents=[KnowledgeDocumentResponse.model_validate(d) for d in docs], total=len(docs)).model_dump
KnowledgeDocumentListResponse
KnowledgeDocumentResponse.model_validate
len
```

<a id="fn-f3026f597a90aaa2"></a>

## get_document

源码：[L191](D:/Project/learnLittle/app/services/knowledge_service.py:191)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按文档 ID 与当前用户查实体，不存在返回统一业务错误。删除等动作先经此权限检查。

**输入与签名**

```python
async def get_document(db: AsyncSession, user_id: str, doc_id: int) -> KnowledgeDocument
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return doc
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id, KnowledgeDocument.user_id == user_id))).scalar_one_or_none
db.execute
select(KnowledgeDocument).where
select
BusinessError
```

<a id="fn-1d1c1e95a6f96a66"></a>

## delete_document

源码：[L207](D:/Project/learnLittle/app/services/knowledge_service.py:207)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

确认文档归属，删除关联向量和原文件并删除 SQL 实体。文件/向量删除无法由 SQL rollback 自动恢复。

**输入与签名**

```python
async def delete_document(db: AsyncSession, user_id: str, doc_id: int) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_document
Path(doc.file_path).unlink
Path
logger.warning
get_vector_store().delete_document
get_vector_store
db.delete
db.flush
```

<a id="fn-8163cb09a9f1933a"></a>

## search_documents

源码：[L221](D:/Project/learnLittle/app/services/knowledge_service.py:221)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

直接查询用户知识库向量并整理搜索响应。知识库搜索不使用聊天 RAG 门控和检索后摘要。

**输入与签名**

```python
async def search_documents(user_id: str, query: str, top_k: int=5) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await get_vector_store().search(keyword, user_id, top_k, collection='rag')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
query.strip
BusinessError
get_vector_store().search
get_vector_store
```
