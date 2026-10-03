# app/ai_service/usage_callback.py

[源码](D:/Project/learnLittle/app/ai_service/usage_callback.py) | [任务流程 09](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

每次 LangChain 模型调用的输入/输出/usage/失败计量。

## 本文件导航

- [ModelUsageCallback.__init__](#fn-f5ddf73e602c71b4)
- [ModelUsageCallback.on_chat_model_start](#fn-8449e1e192878f02)
- [ModelUsageCallback.on_llm_end](#fn-e4938fcebe2ba5e1)
- [ModelUsageCallback.on_llm_error](#fn-d7db34d672827548)

## 类与字段

### ModelUsageCallback

LangChain 异步 callback，以 run_id 区分同轮多次模型调用。

声明位置：[L11](D:/Project/learnLittle/app/ai_service/usage_callback.py:11)。父类：`AsyncCallbackHandler`。

<a id="fn-f5ddf73e602c71b4"></a>

## ModelUsageCallback.__init__

源码：[L12](D:/Project/learnLittle/app/ai_service/usage_callback.py:12)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

保存模型名/阶段与按 run_id 跟踪的字典。每个模型实例回调区分工具循环中的多次推理。

**输入与签名**

```python
def __init__(self, model: str, stage: str='agent')
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-8449e1e192878f02"></a>

## ModelUsageCallback.on_chat_model_start

源码：[L17](D:/Project/learnLittle/app/ai_service/usage_callback.py:17)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

序列化完整 messages 批次和工具声明，按 run_id 保存提示文本与起始时间。下一轮包含的工具返回也因此进入输入估算。

**输入与签名**

```python
async def on_chat_model_start(self, serialized, messages, *, run_id, **kwargs)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
kwargs.get
json.dumps
message.model_dump
params.get
time.perf_counter
```

<a id="fn-e4938fcebe2ba5e1"></a>

## ModelUsageCallback.on_llm_end

源码：[L30](D:/Project/learnLittle/app/ai_service/usage_callback.py:30)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

取对应起点，优先 llm_output usage，其次消息 metadata，收集正文/工具调用并记录一次计量。每次模型完成记一次，不把整轮聊天粗略合成一条。

**输入与签名**

```python
async def on_llm_end(self, response, *, run_id, **kwargs)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self.runs.pop
time.perf_counter
(response.llm_output or {}).get
getattr
completion.append
str
metadata.get
json.dumps
any
metadata_usage.values
record_text_call
''.join
int
```

<a id="fn-d7db34d672827548"></a>

## ModelUsageCallback.on_llm_error

源码：[L53](D:/Project/learnLittle/app/ai_service/usage_callback.py:53)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

弹出 run_id 的提示和起点，以异常类型记失败用量与耗时。失败不因没有正常输出而完全消失。

**输入与签名**

```python
async def on_llm_error(self, error, *, run_id, **kwargs)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self.runs.pop
time.perf_counter
record_text_call
type
int
```
