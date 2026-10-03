# app/core/success_response.py

[源码](D:/Project/learnLittle/app/core/success_response.py) | [任务流程 01](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

普通成功响应字典；不承担事务提交。

## 本文件导航

- [success_response](#fn-ef2351297af49caa)
<a id="fn-ef2351297af49caa"></a>

## success_response

源码：[L12](D:/Project/learnLittle/app/core/success_response.py:12)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

把业务 data、message、code 等放入统一成功信封并生成 request_id。只负责输出形状，不提交数据库，也不把这个 ID 自动传给所有模型调用。

**输入与签名**

```python
def success_response(data: Any=None, message: str='ok', code: int=0, request_id: str | None=None) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'code': code, 'message': message, 'data': data, 'request_id': request_id or str(uuid.uuid4())}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
str
uuid.uuid4
```
