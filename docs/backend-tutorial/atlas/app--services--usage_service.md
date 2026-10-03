# app/services/usage_service.py

[源码](D:/Project/learnLittle/app/services/usage_service.py) | [任务流程 09](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

ContextVar 归属、独立 trace 事务、用量和本地价格聚合。

## 本文件导航

- [set_session_factory](#fn-33465af0687c452e)
- [set_trace_context](#fn-33f468dea821698a)
- [clear_trace_context](#fn-82b6478de51af9b3)
- [set_trace_stage](#fn-e65d40d4489299ff)
- [get_trace_context](#fn-9d4596d88768f7bc)
- [estimate_tokens](#fn-b98c5b1cb06918bd)
- [parse_usage](#fn-3d096bd5f055cf61)
- [record_usage](#fn-9998023a1ccc6d04)
- [record_text_call](#fn-b1495e0a1672bd11)
- [UsageTimer.__init__](#fn-2ec734f07dda7f39)
- [UsageTimer.latency_ms](#fn-4957dc621f7f8de9)
- [UsageTimer.finish](#fn-2e000110003e538b)
- [seed_model_pricing](#fn-eb296701d3cb050d)
- [get_usage_summary](#fn-b0cf831ca9e5feff)

## 类与字段

### UsageTimer

直接客户端和注入函数的一次调用计时包装。

声明位置：[L151](D:/Project/learnLittle/app/services/usage_service.py:151)。父类：`无显式父类`。


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

_trace_ctx: contextvars.ContextVar[dict[str, str] | None] = contextvars.ContextVar('model_trace_ctx', default=None)

_session_factory: async_sessionmaker[AsyncSession] | None = None

DEFAULT_PRICING = {'qwen-plus': {'input_price_per_1k': 0.0008, 'output_price_per_1k': 0.002, 'currency': 'CNY'}, 'qwen-turbo': {'input_price_per_1k': 0.0003, 'output_price_per_1k': 0.0006, 'currency': 'CNY'}, 'text-embedding-v3': {'input_price_per_1k': 0.0005, 'output_price_per_1k': 0.0, 'currency': 'CNY'}}
```

<a id="fn-33465af0687c452e"></a>

## set_session_factory

源码：[L35](D:/Project/learnLittle/app/services/usage_service.py:35)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

设置独立用量写入的会话工厂，应用启动注入、退出清空。没有 factory 时记录函数跳过，不复用聊天事务。

**输入与签名**

```python
def set_session_factory(factory: async_sessionmaker[AsyncSession] | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-33f468dea821698a"></a>

## set_trace_context

源码：[L40](D:/Project/learnLittle/app/services/usage_service.py:40)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

为当前异步上下文放入 request/user/session/stage，未给 request_id 则生成短 ID。它与 HTTP 响应辅助函数的 ID 不是自动相同。

**输入与签名**

```python
def set_trace_context(*, request_id: str | None=None, user_id: str='', session_id: str='', stage: str='chat') -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_trace_ctx.set
uuid.uuid4
```

<a id="fn-82b6478de51af9b3"></a>

## clear_trace_context

源码：[L57](D:/Project/learnLittle/app/services/usage_service.py:57)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

将当前 ContextVar 清为 None，避免后续同上下文误归属用户。不会删除已落库 trace。

**输入与签名**

```python
def clear_trace_context() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_trace_ctx.set
```

<a id="fn-e65d40d4489299ff"></a>

## set_trace_stage

源码：[L61](D:/Project/learnLittle/app/services/usage_service.py:61)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

若已有上下文，复制字典并写新 stage。复制使并行任务继承后的 stage 修改不互相污染。

**输入与签名**

```python
def set_trace_stage(stage: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_trace_ctx.get
_trace_ctx.set
```

<a id="fn-9d4596d88768f7bc"></a>

## get_trace_context

源码：[L67](D:/Project/learnLittle/app/services/usage_service.py:67)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

返回当前上下文的计量归属信息或 None。不是全进程唯一的正在聊天用户。

**输入与签名**

```python
def get_trace_context() -> dict[str, str] | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _trace_ctx.get()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_trace_ctx.get
```

<a id="fn-b98c5b1cb06918bd"></a>

## estimate_tokens

源码：[L71](D:/Project/learnLittle/app/services/usage_service.py:71)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

以字符数约两字一个 Token 向上估计，空字符串返回零。用于缺官方 usage 的粗略计量，不是精确 tokenizer。

**输入与签名**

```python
def estimate_tokens(text: str) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 0
return max(1, (len(text) + 1) // 2)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
max
len
```

<a id="fn-3d096bd5f055cf61"></a>

## parse_usage

源码：[L77](D:/Project/learnLittle/app/services/usage_service.py:77)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

优先取响应 usage 的 prompt/completion/total，字段缺失才用文本估算。显式零值必须保留，不能用 truthy 判断把零替换为估算。

**输入与签名**

```python
def parse_usage(data: dict | None, prompt: str, completion: str) -> tuple[int, int, int]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return (prompt_tokens, completion_tokens, total)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(data or {}).get
usage.get
int
estimate_tokens
```

<a id="fn-9998023a1ccc6d04"></a>

## record_usage

源码：[L85](D:/Project/learnLittle/app/services/usage_service.py:85)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

合并显式参数和 ContextVar，建立 ModelTrace 并用独立 session commit；缺用户/factory 则跳过，落库失败仅日志。保存计数与结果，不是存完整对话审计。

**输入与签名**

```python
async def record_usage(*, stage: str | None=None, model: str | None=None, prompt_tokens: int=0, completion_tokens: int=0, latency_ms: int | None=None, success: bool=True, error: str | None=None, user_id: str | None=None, session_id: str | None=None, request_id: str | None=None) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_trace_ctx.get
ctx.get
int
ModelTrace
factory
db.add
db.commit
logger.warning
```

<a id="fn-b1495e0a1672bd11"></a>

## record_text_call

源码：[L128](D:/Project/learnLittle/app/services/usage_service.py:128)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

把 prompt/completion 与供应商 payload 转计数，再委托 record_usage。调用阶段和模型由调用者明确传入。

**输入与签名**

```python
async def record_text_call(*, stage: str, model: str | None, prompt: str='', completion: str='', usage_payload: dict | None=None, latency_ms: int | None=None, success: bool=True, error: str | None=None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
parse_usage
record_usage
```

<a id="fn-2ec734f07dda7f39"></a>

## UsageTimer.__init__

源码：[L152](D:/Project/learnLittle/app/services/usage_service.py:152)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

记录 stage、model 和 perf_counter 起点，供一次调用计时。构造时不写 SQL。

**输入与签名**

```python
def __init__(self, stage: str, model: str | None=None)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
time.perf_counter
```

<a id="fn-4957dc621f7f8de9"></a>

## UsageTimer.latency_ms

源码：[L157](D:/Project/learnLittle/app/services/usage_service.py:157)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

用当前高精度时钟减起点并转毫秒。它测包装范围总耗时，不一定是供应商纯推理时间。

**输入与签名**

```python
def latency_ms(self) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return int((time.perf_counter() - self._started) * 1000)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
int
time.perf_counter
```

<a id="fn-2e000110003e538b"></a>

## UsageTimer.finish

源码：[L160](D:/Project/learnLittle/app/services/usage_service.py:160)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

把文本、usage、成败和当前耗时传给 record_text_call。一次调用完成或失败路径使用，不能无意重复 finish 造成重复记录。

**输入与签名**

```python
async def finish(self, prompt: str='', completion: str='', usage_payload: dict | None=None, success: bool=True, error: str | None=None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
record_text_call
self.latency_ms
```

<a id="fn-eb296701d3cb050d"></a>

## seed_model_pricing

源码：[L180](D:/Project/learnLittle/app/services/usage_service.py:180)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

从项目种子与当前模型补充价格，查询已有行并更新或新增。是本地配置数据，会覆盖已有种子模型价格，不是查询实时官方价格。

**输入与签名**

```python
async def seed_model_pricing(db: AsyncSession, settings: Settings | None=None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
dict
pricing.items
(await db.execute(select(ModelPricing).where(ModelPricing.model == model))).scalar_one_or_none
db.execute
select(ModelPricing).where
select
float
values.get
db.add
ModelPricing
```

<a id="fn-b0cf831ca9e5feff"></a>

## get_usage_summary

源码：[L208](D:/Project/learnLittle/app/services/usage_service.py:208)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

按用户、时间窗和可选会话聚合总量、stage/model、平均时延并结合价格估费用。未知价格为零，本地费用不是供应商账单。

**输入与签名**

```python
async def get_usage_summary(db: AsyncSession, user_id: str, session_id: str | None=None, days: int=30) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'days': days, 'total_calls': total_calls, 'total_prompt_tokens': total_prompt, 'total_completion_tokens': total_completion, 'total_tokens': total_prompt + total_completion, 'total_cost_cny': round(total_cost, 6), 'avg_latency_ms' ... [截短，完整见源码]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
datetime.now
timedelta
conds.append
(await db.execute(select(func.count(), func.coalesce(func.sum(ModelTrace.prompt_tokens), 0), func.coalesce(func.sum(ModelTrace.completion_tokens), 0), func.coalesce(func.avg(ModelTrace.latency_ms), 0)).where(*conds))).one
db.execute
select(func.count(), func.coalesce(func.sum(ModelTrace.prompt_tokens), 0), func.coalesce(func.sum(ModelTrace.completion_tokens), 0), func.coalesce(func.avg(ModelTrace.latency_ms), 0)).where
select
func.count
func.coalesce
func.sum
func.avg
int
round
float
(await db.execute(select(ModelTrace.stage, func.count(), func.coalesce(func.sum(ModelTrace.prompt_tokens), 0), func.coalesce(func.sum(ModelTrace.completion_tokens), 0)).where(*conds).group_by(ModelTrace.stage))).all
select(ModelTrace.stage, func.count(), func.coalesce(func.sum(ModelTrace.prompt_tokens), 0), func.coalesce(func.sum(ModelTrace.completion_tokens), 0)).where(*conds).group_by
select(ModelTrace.stage, func.count(), func.coalesce(func.sum(ModelTrace.prompt_tokens), 0), func.coalesce(func.sum(ModelTrace.completion_tokens), 0)).where
(await db.execute(select(ModelTrace.model, func.count(), func.coalesce(func.sum(ModelTrace.prompt_tokens), 0), func.coalesce(func.sum(ModelTrace.completion_tokens), 0)).where(*conds).group_by(ModelTrace.model))).all
select(ModelTrace.model, func.count(), func.coalesce(func.sum(ModelTrace.prompt_tokens), 0), func.coalesce(func.sum(ModelTrace.completion_tokens), 0)).where(*conds).group_by
select(ModelTrace.model, func.count(), func.coalesce(func.sum(ModelTrace.prompt_tokens), 0), func.coalesce(func.sum(ModelTrace.completion_tokens), 0)).where
(await db.execute(select(ModelPricing))).scalars().all
(await db.execute(select(ModelPricing))).scalars
prices.get
by_model.append
```
