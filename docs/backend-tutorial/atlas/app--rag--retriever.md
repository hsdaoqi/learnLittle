# app/rag/retriever.py

[源码](D:/Project/learnLittle/app/rag/retriever.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

分词、BM25、RRF、CrossEncoder 适配和词重叠兜底。

## 本文件导航

- [set_rerank_fn](#fn-f44513d083253f53)
- [get_rerank_fn](#fn-d059cc5cb44c6167)
- [set_cross_encoder](#fn-5a15d64e00817ee6)
- [reset_cross_encoder](#fn-e9e9ae8e17e4949f)
- [_as_float_list](#fn-4d4fa84e5fe62619)
- [cross_encoder_scores](#fn-2845b8b2adda9a9d)
- [_cached_rerank_dir](#fn-25553fa2372701fc)
- [_apply_hub_offline_env](#fn-c0470ab283d38c81)
- [_restore_hub_offline_env](#fn-9f72a8c8cad8d6d7)
- [_load_cross_encoder](#fn-f7e186819df6418c)
- [get_or_load_cross_encoder](#fn-ea3fa8dc8ad3bdd4)
- [tokenize](#fn-1e780643715ae502)
- [bm25_scores](#fn-231d8bb42cc13503)
- [rrf_fuse](#fn-1a4ce2eb384cc9ed)
- [rrf_fuse.<lambda@253:12>](#fn-3339433851bc198e)
- [overlap_scores](#fn-a293c153372cbbe6)
- [_score_hits](#fn-bd65e6a43886e289)
- [rerank_hits](#fn-9c3d04fe2af0a4d2)
- [rerank_hits.<lambda@307:18>](#fn-dc6007a0ea179b22)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

TOKEN_RE = re.compile('[\\w\\u4e00-\\u9fff]+', re.UNICODE)

_CJK_RE = re.compile('[\\u4e00-\\u9fff]')

RerankFn = Callable[[str, list[str]], list[float]]

_injected_rerank: RerankFn | None = None

_cross_encoder: Any | None = None

_cross_encoder_failed = False

_cross_encoder_lock = threading.Lock()
```

<a id="fn-f44513d083253f53"></a>

## set_rerank_fn

源码：[L37](D:/Project/learnLittle/app/rag/retriever.py:37)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

替换重排打分的模块级注入槽 `_injected_rerank`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_rerank_fn(fn: RerankFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-d059cc5cb44c6167"></a>

## get_rerank_fn

源码：[L42](D:/Project/learnLittle/app/rag/retriever.py:42)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

返回重排打分当前的注入函数 `_injected_rerank` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_rerank_fn() -> RerankFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected_rerank
```

<a id="fn-5a15d64e00817ee6"></a>

## set_cross_encoder

源码：[L46](D:/Project/learnLittle/app/rag/retriever.py:46)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

直接注入一个有 predict/compute_score 的模型并重置失败标记。测试不下载真实权重也能验证适配路径。

**输入与签名**

```python
def set_cross_encoder(model: Any | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-e9e9ae8e17e4949f"></a>

## reset_cross_encoder

源码：[L53](D:/Project/learnLittle/app/rag/retriever.py:53)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

清注入模型和加载失败状态。用于测试隔离或显式重新尝试，不删除磁盘权重。

**输入与签名**

```python
def reset_cross_encoder() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
set_cross_encoder
```

<a id="fn-4d4fa84e5fe62619"></a>

## _as_float_list

源码：[L59](D:/Project/learnLittle/app/rag/retriever.py:59)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

把 scalar/array/list 分数规范成浮点列表并检查条数。多文档只回一个数或长度不匹配会报错，避免错位排序。

**输入与签名**

```python
def _as_float_list(scores: Any, expected: int) -> list[float]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [float(scores)]
return values
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
hasattr
scores.tolist
isinstance
float
ValueError
len
```

<a id="fn-2845b8b2adda9a9d"></a>

## cross_encoder_scores

源码：[L72](D:/Project/learnLittle/app/rag/retriever.py:72)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

把 query 与每篇正文配对，优先 model.predict，再兼容 compute_score，统一校验输出。支持不同模型库接口，不把函数名写死成其中一种。

**输入与签名**

```python
def cross_encoder_scores(query: str, documents: list[str], model: Any) -> list[float]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _as_float_list(scores, len(documents))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
hasattr
model.predict
model.compute_score
AttributeError
_as_float_list
len
```

<a id="fn-25553fa2372701fc"></a>

## _cached_rerank_dir

源码：[L84](D:/Project/learnLittle/app/rag/retriever.py:84)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

优先本地路径，再通过缓存中的 config.json 找权重目录，失败 None。这样有缓存时可避免额外 Hub 探测。

**输入与签名**

```python
def _cached_rerank_dir(model_name: str) -> str | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
return model_name
return os.path.dirname(str(cached))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
os.path.isdir
try_to_load_from_cache
os.path.dirname
str
```

<a id="fn-c0470ab283d38c81"></a>

## _apply_hub_offline_env

源码：[L102](D:/Project/learnLittle/app/rag/retriever.py:102)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

记录 Hugging Face/Transformers 原离线环境值，按请求开启离线，并返回旧值。改的是进程环境，后续必须恢复。

**输入与签名**

```python
def _apply_hub_offline_env(enabled: bool) -> dict[str, str | None]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return previous
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
os.environ.get
```

<a id="fn-9f72a8c8cad8d6d7"></a>

## _restore_hub_offline_env

源码：[L111](D:/Project/learnLittle/app/rag/retriever.py:111)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按旧值还原或移除离线环境变量。与加载函数 finally 配对，避免影响后续别的库调用。

**输入与签名**

```python
def _restore_hub_offline_env(previous: dict[str, str | None]) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
previous.items
os.environ.pop
```

<a id="fn-f7e186819df6418c"></a>

## _load_cross_encoder

源码：[L119](D:/Project/learnLittle/app/rag/retriever.py:119)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

检查当前 CrossEncoder 构造签名，选择支持的 local_files_only 参数，暂设离线变量后实例化。finally 恢复环境，不能假设所有版本关键字都一样。

**输入与签名**

```python
def _load_cross_encoder(model_name: str, *, local_files_only: bool) -> Any
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return CrossEncoder(model_name, **kwargs)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
inspect.signature
_apply_hub_offline_env
CrossEncoder
_restore_hub_offline_env
```

<a id="fn-ea3fa8dc8ad3bdd4"></a>

## get_or_load_cross_encoder

源码：[L153](D:/Project/learnLittle/app/rag/retriever.py:153)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

返回注入/已有模型，否则按设置与线程锁懒加载，本地优先、下载由开关控制。一次失败记标记，后续回 None 避免每请求反复加载。

**输入与签名**

```python
def get_or_load_cross_encoder(settings: Settings | None) -> Any | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _cross_encoder
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_cached_rerank_dir
_load_cross_encoder
logger.info
logger.warning
```

<a id="fn-1e780643715ae502"></a>

## tokenize

源码：[L181](D:/Project/learnLittle/app/rag/retriever.py:181)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

英文词小写，含中文串拆单字和双字 token。给 BM25 与词重叠用，不是外部中文分词模型。

**输入与签名**

```python
def tokenize(text: str) -> list[str]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return tokens
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
TOKEN_RE.findall
(text or '').lower
_CJK_RE.search
len
list
tokens.extend
range
tokens.append
```

<a id="fn-231d8bb42cc13503"></a>

## bm25_scores

源码：[L194](D:/Project/learnLittle/app/rag/retriever.py:194)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

用文档频率、查询词频、长度归一与 k1/b 算每篇 BM25，空输入返回零列表。分值只用于本次语料排序。

**输入与签名**

```python
def bm25_scores(query_tokens: Sequence[str], docs_tokens: Sequence[Sequence[str]], *, k1: float=1.5, b: float=0.75) -> list[float]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [0.0] * n
return scores
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
len
Counter
lengths.append
df.update
set
sum
df.get
math.log
zip
query_tf.items
tf.get
scores.append
```

<a id="fn-1a4ce2eb384cc9ed"></a>

## rrf_fuse

源码：[L233](D:/Project/learnLittle/app/rag/retriever.py:233)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按 chunk_id 合并多路排名，对每次出现累加 1/(k+rank)，降序并写 rrf_score/score。缺 ID 的项跳过，不直接相加原始余弦和 BM25 分。

**输入与签名**

```python
def rrf_fuse(ranked_lists: Sequence[Sequence[dict]], *, k: int=60, id_field: str='chunk_id') -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ordered
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
max
enumerate
str
hit.get
rrf.get
dict
sorted
merged.values
item.get
```

<a id="fn-3339433851bc198e"></a>

## rrf_fuse.<lambda@253:12>

源码：[L253](D:/Project/learnLittle/app/rag/retriever.py:253)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

取某 chunk_id 的累计 RRF 分给 sorted，外层 reverse=True 高分优先。缺分回零，计算本身已在融合循环完成。

**输入与签名**

```python
lambda item: rrf.get(str(item.get(id_field)), 0.0)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 rrf.get(str(item.get(id_field)), 0.0)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
rrf.get
str
item.get
```

<a id="fn-a293c153372cbbe6"></a>

## overlap_scores

源码：[L262](D:/Project/learnLittle/app/rag/retriever.py:262)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

计算查询 token 被每篇正文覆盖的比例，返回逐篇数值。是无模型重排降级，不是 CrossEncoder 语义判断。

**输入与签名**

```python
def overlap_scores(query: str, documents: list[str]) -> list[float]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [0.0] * len(documents)
return scores
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
set
tokenize
len
scores.append
```

<a id="fn-bd65e6a43886e289"></a>

## _score_hits

源码：[L274](D:/Project/learnLittle/app/rag/retriever.py:274)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

集中选择注入打分、真实/缓存 CrossEncoder、词覆盖率。实际模型获取失败可降级，已选打分运行失败则交给外层保持原序。

**输入与签名**

```python
def _score_hits(query: str, documents: list[str], settings: Settings | None) -> list[float]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected_rerank(query, documents)
return cross_encoder_scores(query, documents, model)
return overlap_scores(query, documents)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_injected_rerank
get_or_load_cross_encoder
cross_encoder_scores
overlap_scores
```

<a id="fn-9c3d04fe2af0a4d2"></a>

## rerank_hits

源码：[L285](D:/Project/learnLittle/app/rag/retriever.py:285)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

为 hits 写 rerank_score/score 并排序截 top_n，打分异常或条数不匹配返回原顺序切片。正常路径会修改传入 hit 字典的分数字段。

**输入与签名**

```python
def rerank_hits(query: str, hits: list[dict], *, top_n: int | None=None, settings: Settings | None=None) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return []
return hits[:top_n] if top_n is not None else hits
return ranked[:top_n]
return ranked
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
str
hit.get
_score_hits
len
ValueError
logger.warning
zip
float
sorted
```

<a id="fn-dc6007a0ea179b22"></a>

## rerank_hits.<lambda@307:18>

源码：[L307](D:/Project/learnLittle/app/rag/retriever.py:307)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

取 rerank_score 作降序排序 key，缺值/零使用 0.0。不是重新执行模型打分。

**输入与签名**

```python
lambda item: item.get("rerank_score") or 0.0
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 item.get('rerank_score') or 0.0
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
item.get
```
