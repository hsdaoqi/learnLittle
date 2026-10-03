# app/rag/vector_store.py

[源码](D:/Project/learnLittle/app/rag/vector_store.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

Chroma 双 collection 的嵌入写入、双源检索、用户过滤与删除。

## 本文件导航

- [VectorStoreService.__init__](#fn-249ac03d872095cf)
- [VectorStoreService._ensure](#fn-804e104f8bbe1e54)
- [VectorStoreService._collection](#fn-bcec9c3a52fcc1f8)
- [VectorStoreService._check_dimension](#fn-c8a416c27179f47a)
- [VectorStoreService.upsert_chunks](#fn-e02cacc334a8d60b)
- [VectorStoreService._candidate_k](#fn-d30f58998f338f76)
- [VectorStoreService._format_hit](#fn-8ec15dac192e0e54)
- [VectorStoreService._vector_search](#fn-7dd4cd317a6282ac)
- [VectorStoreService._bm25_search](#fn-db04a944f8db3908)
- [VectorStoreService._bm25_search.<lambda@216:22>](#fn-e3b1ba6952eccc5a)
- [VectorStoreService._maybe_rerank](#fn-3c7ca314d71e5617)
- [VectorStoreService.search](#fn-5ce99fb5dd20587a)
- [VectorStoreService.compute_route_score](#fn-59f8ba1382dbc7f0)
- [VectorStoreService.search_both](#fn-e471098b85aa1cbf)
- [VectorStoreService.search_both.<lambda@299:42>](#fn-f352e18a2488061e)
- [VectorStoreService.delete_document](#fn-16cf3eacbc4fc7ae)
- [VectorStoreService.delete_note](#fn-173d128d95a4b5e8)
- [VectorStoreService._delete_by](#fn-b573926b09c48d7c)
- [set_vector_store](#fn-75a118d8f1d3d5c5)
- [get_vector_store](#fn-e961062ae761011a)
- [init_vector_store](#fn-ccc54ef4e7695b07)
- [close_vector_store](#fn-f628c630360e9ef4)

## 类与字段

### VectorStoreService

封装 Chroma client 与双 collection 的生命周期、检索和删除。

声明位置：[L25](D:/Project/learnLittle/app/rag/vector_store.py:25)。父类：`无显式父类`。


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

CollectionName = Literal['rag', 'notes']

_service: VectorStoreService | None = None
```

<a id="fn-249ac03d872095cf"></a>

## VectorStoreService.__init__

源码：[L26](D:/Project/learnLittle/app/rag/vector_store.py:26)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

保存 settings 与可选 Chroma client，集合尚未获取，维度检查标记为假。注入 ephemeral client 可避免测试写正式磁盘。

**输入与签名**

```python
def __init__(self, settings: Settings, client: Any | None=None)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-804e104f8bbe1e54"></a>

## VectorStoreService._ensure

源码：[L33](D:/Project/learnLittle/app/rag/vector_store.py:33)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

懒建 PersistentClient 或复用注入实例，获取知识/笔记两个 cosine collection。名字来自配置，不按每个用户另建 collection。

**输入与签名**

```python
def _ensure(self)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
chromadb.PersistentClient
ChromaSettings
self._client.get_or_create_collection
```

<a id="fn-bcec9c3a52fcc1f8"></a>

## VectorStoreService._collection

源码：[L53](D:/Project/learnLittle/app/rag/vector_store.py:53)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

确保初始化后根据 rag/notes 名返回对应集合。用户隔离在查询 metadata 条件，不在此函数。

**输入与签名**

```python
def _collection(self, name: CollectionName)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return self._rag if name == 'rag' else self._notes
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._ensure
```

<a id="fn-c8a416c27179f47a"></a>

## VectorStoreService._check_dimension

源码：[L57](D:/Project/learnLittle/app/rag/vector_store.py:57)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

首次有 probe 时检查非空集合已有向量维度，不匹配抛业务错误，通过后记标记。只验维度不验同维模型语义兼容；报错建议清库不意味着教程授权删除数据。

**输入与签名**

```python
async def _check_dimension(self, probe: list[float]) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
len
col.count
(col.get(limit=1, include=['embeddings']) or {}).get
col.get
hasattr
BusinessError
```

<a id="fn-e02cacc334a8d60b"></a>

## VectorStoreService.upsert_chunks

源码：[L81](D:/Project/learnLittle/app/rag/vector_store.py:81)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

对非空 documents 批量 embedding、维度检查，再把 ID/正文/metadata/向量写指定 collection。调用者负责 metadata 的用户归属和稳定 ID。

**输入与签名**

```python
async def upsert_chunks(self, *, documents: list[str], metadatas: list[dict], ids: list[str], collection: CollectionName='rag') -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._collection
embed_texts
self._check_dimension
target.upsert
```

<a id="fn-d30f58998f338f76"></a>

## VectorStoreService._candidate_k

源码：[L101](D:/Project/learnLittle/app/rag/vector_store.py:101)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

放大 top_k 并应用候选上限，至少保留请求规模。候选量不等于最终返回数量。

**输入与签名**

```python
def _candidate_k(self, top_k: int) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return min(max(top_k * multiplier, top_k), cap)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
max
min
```

<a id="fn-8ec15dac192e0e54"></a>

## VectorStoreService._format_hit

源码：[L106](D:/Project/learnLittle/app/rag/vector_store.py:106)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

统一 Chroma 结果形状，补 source、document/note ID、文件标题、章节、片序和 chunk_id。后续融合靠 chunk_id，展示靠其他 metadata。

**输入与签名**

```python
def _format_hit(self, *, doc: str, meta: dict, collection: CollectionName, chroma_id: str='', score: float=0.0) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'content': doc, 'score': float(score), 'source': source, 'document_id': document_id, 'note_id': note_id, 'filename': meta.get('filename') or meta.get('title') or '', 'section_title': meta.get('section_title') or '', 'chunk_index' ... [截短，完整见源码]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
int
meta.get
float
```

<a id="fn-7dd4cd317a6282ac"></a>

## VectorStoreService._vector_search

源码：[L136](D:/Project/learnLittle/app/rag/vector_store.py:136)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

空 collection 返回空，否则嵌入 query、按 user_id 过滤查询，余弦距离转 1-distance 并格式化。目标 count 是全集合数量，不等于该用户命中数。

**输入与签名**

```python
async def _vector_search(self, query: str, user_id: str, n_results: int, collection: CollectionName) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return []
return formatted
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._collection
target.count
embed_texts
self._check_dimension
min
max
target.query
results.get
enumerate
len
formatted.append
self._format_hit
float
```

<a id="fn-db04a944f8db3908"></a>

## VectorStoreService._bm25_search

源码：[L175](D:/Project/learnLittle/app/rag/vector_store.py:175)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

取当前用户最多 bm25_max_docs 文本，tokenize 后计算 BM25，过滤零分并排序截取。不是数据库 FULLTEXT 那条检索路线。

**输入与签名**

```python
def _bm25_search(self, query: str, user_id: str, top_k: int, collection: CollectionName) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return []
return hits[:top_k]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._collection
target.count
target.get
max
found.get
bm25_scores
tokenize
enumerate
len
hits.append
self._format_hit
hits.sort
```

<a id="fn-e3b1ba6952eccc5a"></a>

## VectorStoreService._bm25_search.<lambda@216:22>

源码：[L216](D:/Project/learnLittle/app/rag/vector_store.py:216)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

取 BM25 hit.score 作降序排列依据，空值用零。只排序当前用户已过滤的候选。

**输入与签名**

```python
lambda item: item.get("score") or 0
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 item.get('score') or 0
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
item.get
```

<a id="fn-3c7ca314d71e5617"></a>

## VectorStoreService._maybe_rerank

源码：[L219](D:/Project/learnLittle/app/rag/vector_store.py:219)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

无结果直接空，允许重排且总开关启用则委托 rerank_hits，否则切 top_k。该同步函数由外层 to_thread 调度较重计算。

**输入与签名**

```python
def _maybe_rerank(self, query: str, hits: list[dict], top_k: int, enabled: bool) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return []
return rerank_hits(query, hits, top_n=top_k, settings=self.settings)
return hits[:top_k]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
rerank_hits
```

<a id="fn-5ce99fb5dd20587a"></a>

## VectorStoreService.search

源码：[L228](D:/Project/learnLittle/app/rag/vector_store.py:228)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

单源先扩大候选向量召回，可选 BM25+RRF，然后可选重排。返回统一 hit 列表，默认 hybrid 开关不保证已开启。

**输入与签名**

```python
async def search(self, query: str, user_id: str, top_k: int=5, collection: CollectionName='rag', rerank: bool=True) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return []
return await asyncio.to_thread(self._maybe_rerank, query, fused, top_k, rerank)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._collection
target.count
self._candidate_k
self._vector_search
asyncio.to_thread
rrf_fuse
```

<a id="fn-59f8ba1382dbc7f0"></a>

## VectorStoreService.compute_route_score

源码：[L250](D:/Project/learnLittle/app/rag/vector_store.py:250)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

只做双源当前用户 Top-1 余弦距离，取最小；空问题/无用户资料返回 inf。不经过 BM25、HyDE 或重排。

**输入与签名**

```python
async def compute_route_score(self, query: str, user_id: str) -> float
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return float('inf')
return best
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(query or '').strip
float
self._ensure
embed_texts
self._check_dimension
self._collection
target.count
target.query
results.get
min
```

<a id="fn-e471098b85aa1cbf"></a>

## VectorStoreService.search_both

源码：[L278](D:/Project/learnLittle/app/rag/vector_store.py:278)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

并行查 rag/notes 各两倍 top_k，按配置 RRF 或直接分数排序，再用原 rerank_query 重排。召回 query 可是 HyDE，而重排保留用户原问题。

**输入与签名**

```python
async def search_both(self, query: str, user_id: str, top_k: int=5, rerank_query: str | None=None) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await asyncio.to_thread(self._maybe_rerank, rerank_query or query, fused, top_k, True)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._ensure
asyncio.gather
self.search
rrf_fuse
sorted
asyncio.to_thread
```

<a id="fn-f352e18a2488061e"></a>

## VectorStoreService.search_both.<lambda@299:42>

源码：[L299](D:/Project/learnLittle/app/rag/vector_store.py:299)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

hybrid 关闭时合并两源，直接按 hit.score 降序。没有 RRF 融合，这也是默认配置的可达分支。

**输入与签名**

```python
lambda hit: hit["score"]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 hit['score']
```

<a id="fn-16cf3eacbc4fc7ae"></a>

## VectorStoreService.delete_document

源码：[L306](D:/Project/learnLittle/app/rag/vector_store.py:306)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按 document_id 字符串删除 rag collection 所有切片。内部 ID 已经来自拥有权限的 service，不重新鉴权。

**输入与签名**

```python
def delete_document(self, document_id: int | str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._delete_by
str
```

<a id="fn-173d128d95a4b5e8"></a>

## VectorStoreService.delete_note

源码：[L309](D:/Project/learnLittle/app/rag/vector_store.py:309)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按 note_id 清 notes collection 切片。SQL 删除与恢复由笔记 service 控制。

**输入与签名**

```python
def delete_note(self, note_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._delete_by
```

<a id="fn-b573926b09c48d7c"></a>

## VectorStoreService._delete_by

源码：[L312](D:/Project/learnLittle/app/rag/vector_store.py:312)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按 metadata 找 ID，再批量 delete 并记录数量。无匹配不报错，方便重复清理。

**输入与签名**

```python
def _delete_by(self, collection: CollectionName, field: str, value: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._collection
target.get
found.get
target.delete
logger.info
len
```

<a id="fn-75a118d8f1d3d5c5"></a>

## set_vector_store

源码：[L327](D:/Project/learnLittle/app/rag/vector_store.py:327)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

替换全局向量服务实例，供测试隔离或生命周期清理。不是替换 SQL session。

**输入与签名**

```python
def set_vector_store(service: VectorStoreService | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-e961062ae761011a"></a>

## get_vector_store

源码：[L332](D:/Project/learnLittle/app/rag/vector_store.py:332)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

返回已初始化服务，没有则 RuntimeError 提示生命周期未完成。业务调用应在初始化之后。

**输入与签名**

```python
def get_vector_store() -> VectorStoreService
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _service
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
RuntimeError
```

<a id="fn-ccc54ef4e7695b07"></a>

## init_vector_store

源码：[L338](D:/Project/learnLittle/app/rag/vector_store.py:338)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

已有实例直接复用，否则创建服务并缓存。并不强制立即打开两个 Chroma collection。

**输入与签名**

```python
def init_vector_store(settings: Settings, client: Any | None=None) -> VectorStoreService
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _service
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
VectorStoreService
```

<a id="fn-f628c630360e9ef4"></a>

## close_vector_store

源码：[L348](D:/Project/learnLittle/app/rag/vector_store.py:348)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

清全局服务引用。不是删除 data/chroma，也不承诺调用所有底层 client 的持久化清理 API。

**输入与签名**

```python
def close_vector_store() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。
