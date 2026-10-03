# tests/test_retriever_predict.py

[源码](D:/Project/learnLittle/tests/test_retriever_predict.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

## 本文件导航

- [_FakeSentenceTransformerCrossEncoder.__init__](#fn-d0a95c50e3c7ed42)
- [_FakeSentenceTransformerCrossEncoder.predict](#fn-2c95e4d23ec82039)
- [test_sentence_transformers_cross_encoder_uses_predict](#fn-323af66150b2a13d)

## 类与字段

### _FakeSentenceTransformerCrossEncoder

测试替身类，显式方法在本文件详解；实例只提供该测试需要的可控行为，不代表生产模型实现。

声明位置：[L6](D:/Project/learnLittle/tests/test_retriever_predict.py:6)。父类：`无显式父类`。

<a id="fn-d0a95c50e3c7ed42"></a>

## _FakeSentenceTransformerCrossEncoder.__init__

源码：[L7](D:/Project/learnLittle/tests/test_retriever_predict.py:7)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

保存预设分数并初始化 pairs 记录。模拟只支持 predict 的模型接口。

**输入与签名**

```python
def __init__(self, scores)
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-2c95e4d23ec82039"></a>

## _FakeSentenceTransformerCrossEncoder.predict

源码：[L11](D:/Project/learnLittle/tests/test_retriever_predict.py:11)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

记录收到的 query/document 对并返回预设 scores。外层测试据此确认适配调用真实发生。

**输入与签名**

```python
def predict(self, pairs)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return self.scores
```

<a id="fn-323af66150b2a13d"></a>

## test_sentence_transformers_cross_encoder_uses_predict

源码：[L16](D:/Project/learnLittle/tests/test_retriever_predict.py:16)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

注入 predict 风格假模型验证重排排序与输入配对。防止只兼容 compute_score 导致 sentence-transformers 静默降级。

**输入与签名**

```python
def test_sentence_transformers_cross_encoder_uses_predict()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert ranked[0]['content'] == 'high'
assert model.pairs == [('q', 'low'), ('q', 'high')]
assert ranked[0]['rerank_score'] == 0.8
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
set_rerank_fn
_FakeSentenceTransformerCrossEncoder
set_cross_encoder
rerank_hits
```
