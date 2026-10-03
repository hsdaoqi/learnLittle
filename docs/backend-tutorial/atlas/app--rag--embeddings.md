# app/rag/embeddings.py

[源码](D:/Project/learnLittle/app/rag/embeddings.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

注入/API/无 key 哈希向量、批处理与进程 TTL/LRU 缓存。

## 本文件导航

- [set_embed_fn](#fn-def8332025c8f634)
- [get_embed_fn](#fn-bbc7a170c5bc838e)
- [reset_embedding_cache](#fn-4945d572c80e2448)
- [hash_embed_text](#fn-8f6c14d44a86fc15)
- [hash_embed_texts](#fn-5a91b5baa495e5a4)
- [_backend_tag](#fn-f8471f1fbe78306f)
- [_cache_key](#fn-0ea1415c83403b40)
- [_embedding_api_key](#fn-224dc01985311850)
- [_embedding_base_url](#fn-86edf386f08099a3)
- [embed_openai_compatible](#fn-388ca181c079085f)
- [embed_openai_compatible.<lambda@125:19>](#fn-5bc8a99cdd7cfeb8)
- [_embed_batch](#fn-097ce3fe59095d20)
- [embed_texts](#fn-1cb42f17b385fff9)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

EmbedFn = Callable[[list[str]], Awaitable[list[list[float]]]]

_TOKEN_RE = re.compile('[\\w\\u4e00-\\u9fff]+', re.UNICODE)

_injected: EmbedFn | None = None

_cache: OrderedDict[str, tuple[list[float], float]] = OrderedDict()

embed_text = hash_embed_text
```

<a id="fn-def8332025c8f634"></a>

## set_embed_fn

源码：[L32](D:/Project/learnLittle/app/rag/embeddings.py:32)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

替换批量嵌入的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_embed_fn(fn: EmbedFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-bbc7a170c5bc838e"></a>

## get_embed_fn

源码：[L37](D:/Project/learnLittle/app/rag/embeddings.py:37)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

返回批量嵌入当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_embed_fn() -> EmbedFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-4945d572c80e2448"></a>

## reset_embedding_cache

源码：[L41](D:/Project/learnLittle/app/rag/embeddings.py:41)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

清进程内 embedding LRU 缓存，测试/切换环境使用。不会清 Chroma 已持久化向量。

**输入与签名**

```python
def reset_embedding_cache() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_cache.clear
```

<a id="fn-8f6c14d44a86fc15"></a>

## hash_embed_text

源码：[L45](D:/Project/learnLittle/app/rag/embeddings.py:45)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

把文本 token 确定性映射到指定维度槽并归一化，返回浮点列表。便于无 key 测试流程，不是真实语义模型。

**输入与签名**

```python
def hash_embed_text(text: str, dim: int=64) -> list[float]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [v / norm for v in vector]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_TOKEN_RE.findall
(text or '').lower
hashlib.sha256(token.encode('utf-8')).digest
hashlib.sha256
token.encode
range
min
len
math.sqrt
sum
```

<a id="fn-5a91b5baa495e5a4"></a>

## hash_embed_texts

源码：[L63](D:/Project/learnLittle/app/rag/embeddings.py:63)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

逐条调用哈希嵌入并保持输入次序，返回向量列表。不能将这批结果混入另一真实模型的语义空间。

**输入与签名**

```python
def hash_embed_texts(texts: list[str], dim: int=64) -> list[list[float]]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [hash_embed_text(t, dim) for t in texts]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
hash_embed_text
```

<a id="fn-f8471f1fbe78306f"></a>

## _backend_tag

源码：[L71](D:/Project/learnLittle/app/rag/embeddings.py:71)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

构造描述注入/API/哈希后端的缓存标签。它不是所有 endpoint 参数的完整指纹。

**输入与签名**

```python
def _backend_tag(settings: Settings) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 'injected'
return f'api:{settings.embedding_model}'
return f'hash:{settings.embedding_dim}'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_embedding_api_key
```

<a id="fn-0ea1415c83403b40"></a>

## _cache_key

源码：[L79](D:/Project/learnLittle/app/rag/embeddings.py:79)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

组合后端标签与文本 MD5 作为缓存 key。没有 user_id，意图是复用相同文本的向量计算。

**输入与签名**

```python
def _cache_key(text: str, settings: Settings) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return hashlib.md5(raw.encode('utf-8')).hexdigest()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_backend_tag
hashlib.md5(raw.encode('utf-8')).hexdigest
hashlib.md5
raw.encode
```

<a id="fn-224dc01985311850"></a>

## _embedding_api_key

源码：[L84](D:/Project/learnLittle/app/rag/embeddings.py:84)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

优先 embedding 专用 key，空时复用主 LLM key。这里只选配置，不向外输出密钥。

**输入与签名**

```python
def _embedding_api_key(settings: Settings) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return (settings.embedding_api_key or settings.llm_api_key or '').strip()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(settings.embedding_api_key or settings.llm_api_key or '').strip
```

<a id="fn-86edf386f08099a3"></a>

## _embedding_base_url

源码：[L88](D:/Project/learnLittle/app/rag/embeddings.py:88)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

优先 embedding 专用 URL，空时复用主接口 URL。专用模型与主聊天模型可以不同，但必须按配置理解实际目的地。

**输入与签名**

```python
def _embedding_base_url(settings: Settings) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return (settings.embedding_base_url or settings.llm_base_url).rstrip('/')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(settings.embedding_base_url or settings.llm_base_url).rstrip
```

<a id="fn-388ca181c079085f"></a>

## embed_openai_compatible

源码：[L92](D:/Project/learnLittle/app/rag/embeddings.py:92)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

POST /embeddings，传模型和批量 input，检查响应后按 index 排序返回向量。当前未接用量落库；API 错误抛出，不静默改哈希。

**输入与签名**

```python
async def embed_openai_compatible(texts: list[str], settings: Settings, api_key: str) -> list[list[float]]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return vectors
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_embedding_base_url
httpx.AsyncClient
client.post
BusinessError
str
resp.json
list
data.get
items.sort
item.get
len
any
```

<a id="fn-5bc8a99cdd7cfeb8"></a>

## embed_openai_compatible.<lambda@125:19>

源码：[L125](D:/Project/learnLittle/app/rag/embeddings.py:125)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

API embedding 返回项按 index 升序排列，恢复与 input 对应关系。缺 index 时按零处理，不能把返回次序随意当输入次序。

**输入与签名**

```python
lambda item: item.get("index", 0)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 item.get('index', 0)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
item.get
```

<a id="fn-097ce3fe59095d20"></a>

## _embed_batch

源码：[L136](D:/Project/learnLittle/app/rag/embeddings.py:136)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

选择注入、配置 API 或无 key 的哈希实现并返回一批向量。选择优先级由此集中控制。

**输入与签名**

```python
async def _embed_batch(texts: list[str], settings: Settings) -> list[list[float]]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await _injected(texts)
return await embed_openai_compatible(texts, settings, api_key)
return hash_embed_texts(texts, settings.embedding_dim)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_injected
_embedding_api_key
embed_openai_compatible
hash_embed_texts
```

<a id="fn-1cb42f17b385fff9"></a>

## embed_texts

源码：[L145](D:/Project/learnLittle/app/rag/embeddings.py:145)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按输入查 TTL/LRU 缓存，收集缺项分批嵌入、回填、淘汰，并按原序返回。缓存是进程内派生结果，模型换配置仍需注意已有 Chroma 的一致性。

**输入与签名**

```python
async def embed_texts(texts: list[str], settings: Settings) -> list[list[float]]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return []
return filled
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
time
len
enumerate
_cache_key
_cache.get
_cache.move_to_end
missing_idx.append
missing_texts.append
max
range
new_vectors.extend
_embed_batch
zip
_cache.popitem
RuntimeError
filled.append
```
