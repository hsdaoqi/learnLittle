# app/rag/rag_route.py

[源码](D:/Project/learnLittle/app/rag/rag_route.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

根据当前用户双源 Top-1 距离决定是否检索。

## 本文件导航

- [set_route_fn](#fn-7969891cecb899c7)
- [get_route_fn](#fn-302c439eb83c65a2)
- [decide_retrieval](#fn-f9a9a4bf72cbcd21)

## 类与字段

### RouteDecision

是否检索、距离与原因的不可变结果，不表示 ReAct/Plan 复杂度分类。

声明位置：[L23](D:/Project/learnLittle/app/rag/rag_route.py:23)。父类：`无显式父类`。

```python
retrieve: bool

distance: float

reason: str
```


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

RouteFn = Callable[[str, str, Settings], Awaitable[RouteDecision]]

_injected: RouteFn | None = None
```

<a id="fn-7969891cecb899c7"></a>

## set_route_fn

源码：[L34](D:/Project/learnLittle/app/rag/rag_route.py:34)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

替换RAG 检索门控的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_route_fn(fn: RouteFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-302c439eb83c65a2"></a>

## get_route_fn

源码：[L39](D:/Project/learnLittle/app/rag/rag_route.py:39)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

返回RAG 检索门控当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_route_fn() -> RouteFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-f9a9a4bf72cbcd21"></a>

## decide_retrieval

源码：[L43](D:/Project/learnLittle/app/rag/rag_route.py:43)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

空 query 跳过，关闭门控则检索；注入优先，否则比较当前用户双库 Top-1 距离与阈值，评分失败放行。返回 RouteDecision，不直接生成回答。

**输入与签名**

```python
async def decide_retrieval(question: str, user_id: str, settings: Settings) -> RouteDecision
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return RouteDecision(False, float('inf'), 'empty')
return RouteDecision(True, 0.0, 'disabled')
return await _injected(query, user_id, settings)
return RouteDecision(True, float('inf'), 'score_failed')
return RouteDecision(False, distance, 'above_threshold')
return RouteDecision(True, distance, 'below_threshold')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(question or '').strip
RouteDecision
float
_injected
get_vector_store().compute_route_score
get_vector_store
logger.warning
logger.debug
```
