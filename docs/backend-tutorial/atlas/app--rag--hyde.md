# app/rag/hyde.py

[源码](D:/Project/learnLittle/app/rag/hyde.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

生成假设查询并 Redis 缓存，主聊天默认由外层关闭。

## 本文件导航

- [set_hyde_fn](#fn-5aec2742c0679dd7)
- [get_hyde_fn](#fn-259135ff10a31eff)
- [build_hyde_prompt](#fn-d0e501afa47ac756)
- [hyde_cache_key](#fn-518d60ff13df7955)
- [_cache_get](#fn-79acff92daa98cf0)
- [_cache_set](#fn-02330b09650adecc)
- [generate_hyde](#fn-e301802b92650983)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

HydeFn = Callable[[str], Awaitable[str]]

_injected: HydeFn | None = None
```

<a id="fn-5aec2742c0679dd7"></a>

## set_hyde_fn

源码：[L26](D:/Project/learnLittle/app/rag/hyde.py:26)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

替换HyDE 假设生成的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_hyde_fn(fn: HydeFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-259135ff10a31eff"></a>

## get_hyde_fn

源码：[L31](D:/Project/learnLittle/app/rag/hyde.py:31)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

返回HyDE 假设生成当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_hyde_fn() -> HydeFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-d0e501afa47ac756"></a>

## build_hyde_prompt

源码：[L35](D:/Project/learnLittle/app/rag/hyde.py:35)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

要求模型生成像资料陈述句的假设回答以辅助召回。该文本不作为已验证事实直接回答用户。

**输入与签名**

```python
def build_hyde_prompt(question: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'请根据下列问题写一段假设性回答，用于检索相关文档。不需要完全正确，但要像文档里会出现的陈述句，包含可能的术语和实体。不要提问，不要解释你在做什么，只输出假设性回答本身。\n\n问题：{question}\n\n假设性回答：'
```

<a id="fn-518d60ff13df7955"></a>

## hyde_cache_key

源码：[L45](D:/Project/learnLittle/app/rag/hyde.py:45)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

用模型、用户和问题 MD5 组成 Redis key。把不同用户的假设检索缓存分开。

**输入与签名**

```python
def hyde_cache_key(question: str, user_id: str, model: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'hyde:v1:{model}:{user_id}:{digest}'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
hashlib.md5(question.encode('utf-8')).hexdigest
hashlib.md5
question.encode
```

<a id="fn-79acff92daa98cf0"></a>

## _cache_get

源码：[L50](D:/Project/learnLittle/app/rag/hyde.py:50)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

尝试读 HyDE 缓存，异常或空返回 None。缓存故障不会终止检索。

**输入与签名**

```python
async def _cache_get(key: str) -> str | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return value or None
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().get
get_redis
```

<a id="fn-02330b09650adecc"></a>

## _cache_set

源码：[L60](D:/Project/learnLittle/app/rag/hyde.py:60)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

以 TTL 写假设文本，异常忽略。返回成功不构成 SQL 事务承诺。

**输入与签名**

```python
async def _cache_set(key: str, value: str, ttl: int) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().set
get_redis
max
```

<a id="fn-e301802b92650983"></a>

## generate_hyde

源码：[L69](D:/Project/learnLittle/app/rag/hyde.py:69)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

开关允许时先查缓存，再用注入/模型生成假设并缓存；无 key/失败/空结果回原问题。主 query 还受 chat_hyde_enabled 外层开关约束。

**输入与签名**

```python
async def generate_hyde(question: str, user_id: str, settings: Settings) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return query
return cached
return text
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(question or '').strip
hyde_cache_key
_cache_get
set_trace_stage
UsageTimer
(await _injected(query)).strip
_injected
timer.finish
str
complete_openai_compatible
build_hyde_prompt
logger.warning
_cache_set
```
