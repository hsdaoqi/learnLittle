# app/rag/token_budget.py

[源码](D:/Project/learnLittle/app/rag/token_budget.py) | [任务流程 08](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

tokenizer/字符估算与单条消息开销计数；配额在 chat_history 计算。

## 本文件导航

- [TokenCounter.get_encoder](#fn-e80f2b35490779f5)
- [TokenCounter.reset_encoders](#fn-883b8af2520cb694)
- [TokenCounter.count](#fn-1f12b061c723a276)
- [count_message](#fn-08f6741fc1d5886b)

## 类与字段

### TokenCounter

类级编码器缓存与计数入口；失败估算不等于供应商账单。

声明位置：[L12](D:/Project/learnLittle/app/rag/token_budget.py:12)。父类：`无显式父类`。

```python
_encoders: dict = {}
```


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

_OVERHEAD_PER_MESSAGE = 4
```

<a id="fn-e80f2b35490779f5"></a>

## TokenCounter.get_encoder

源码：[L18](D:/Project/learnLittle/app/rag/token_budget.py:18)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

按编码名缓存 tokenizer，按实现处理库/编码不可用的情况。不会每次 count 都重新初始化编码器。

**输入与签名**

```python
def get_encoder(cls, model_name: str='cl100k_base')
```

装饰器/挂载：

```python
@classmethod
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return cls._encoders[model_name]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
tiktoken.get_encoding
logger.warning
```

<a id="fn-883b8af2520cb694"></a>

## TokenCounter.reset_encoders

源码：[L30](D:/Project/learnLittle/app/rag/token_budget.py:30)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

清编码器缓存，测试可以重新验证 fallback。与 embedding 缓存是完全不同的数据。

**输入与签名**

```python
def reset_encoders(cls) -> None
```

装饰器/挂载：

```python
@classmethod
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
cls._encoders.clear
```

<a id="fn-1f12b061c723a276"></a>

## TokenCounter.count

源码：[L34](D:/Project/learnLittle/app/rag/token_budget.py:34)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

有编码器则按 encode 长度计数，编码器加载不可用才以字符数粗估，空文本为零。返回预算整数，不直接请求模型；encode 自身异常没有在此统一捕获。

**输入与签名**

```python
def count(cls, text: str, model_name: str='cl100k_base') -> int
```

装饰器/挂载：

```python
@classmethod
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 0
return len(encoder.encode(text))
return max(1, len(text) // 2)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
cls.get_encoder
len
encoder.encode
max
```

<a id="fn-08f6741fc1d5886b"></a>

## count_message

源码：[L43](D:/Project/learnLittle/app/rag/token_budget.py:43)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

计算单条正文及消息额外开销。历史选择把这个值累加，而不是仅按 len(content)。

**输入与签名**

```python
def count_message(content: str) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return TokenCounter.count(content) + _OVERHEAD_PER_MESSAGE
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
TokenCounter.count
```
