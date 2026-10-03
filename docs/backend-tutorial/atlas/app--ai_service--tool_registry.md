# app/ai_service/tool_registry.py

[源码](D:/Project/learnLittle/app/ai_service/tool_registry.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

内存 ToolSpec/分组/实现绑定/只读能力描述。

## 本文件导航

- [ToolRegistry.__init__](#fn-d9a36bd4f64c4e33)
- [ToolRegistry.register](#fn-b0214b99a9007a69)
- [ToolRegistry.register_group](#fn-44d38f32f384ad3f)
- [ToolRegistry.get](#fn-0aee6001cc5ff194)
- [ToolRegistry.resolve](#fn-3e79db2ee454812a)
- [ToolRegistry.unregister](#fn-ef8fcb0f6177cbe0)
- [ToolRegistry.bind](#fn-1f92bd767d182f2e)
- [ToolRegistry.groups_for](#fn-aebc7577c31a9772)

## 类与字段

### ToolSpec

模型看到的描述/参数与 Python 实现、分组和只读并行能力。

声明位置：[L11](D:/Project/learnLittle/app/ai_service/tool_registry.py:11)。父类：`无显式父类`。

```python
name: str

description: str

parameters: dict

fn: Callable[..., Any] | None

group: str = 'base'

parallel_safe: bool = False
```

### ToolRegistry

内存映射管理器，不提供持久化审计或模型权限之外的数据库自动隔离。

声明位置：[L20](D:/Project/learnLittle/app/ai_service/tool_registry.py:20)。父类：`无显式父类`。


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
registry = ToolRegistry()
```

<a id="fn-d9a36bd4f64c4e33"></a>

## ToolRegistry.__init__

源码：[L21](D:/Project/learnLittle/app/ai_service/tool_registry.py:21)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

初始化组->名称列表与名称->ToolSpec 两个字典。只是内存注册表，不存数据库审计。

**输入与签名**

```python
def __init__(self) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-b0214b99a9007a69"></a>

## ToolRegistry.register

源码：[L25](D:/Project/learnLittle/app/ai_service/tool_registry.py:25)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

拒绝重名，保存 spec 并将名称追加到组。parallel_safe 等能力来自注册描述，必须由开发者正确标记。

**输入与签名**

```python
def register(self, spec: ToolSpec) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
ValueError
self._groups.setdefault(spec.group, []).append
self._groups.setdefault
```

<a id="fn-44d38f32f384ad3f"></a>

## ToolRegistry.register_group

源码：[L31](D:/Project/learnLittle/app/ai_service/tool_registry.py:31)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

用名称列表设置一个组，允许组织现有工具别名分组。不会自动创建缺失 ToolSpec。

**输入与签名**

```python
def register_group(self, group: str, names: list[str]) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
list
```

<a id="fn-0aee6001cc5ff194"></a>

## ToolRegistry.get

源码：[L34](D:/Project/learnLittle/app/ai_service/tool_registry.py:34)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按名称取 spec，未知返回 None。执行器把未知工具按可能有副作用保守处理。

**输入与签名**

```python
def get(self, name: str) -> ToolSpec | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return self._specs.get(name)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._specs.get
```

<a id="fn-3e79db2ee454812a"></a>

## ToolRegistry.resolve

源码：[L37](D:/Project/learnLittle/app/ai_service/tool_registry.py:37)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按可选组解析工具，指定组时去重，过滤不存在 spec 的名称。返回描述列表，不绑定当前用户。

**输入与签名**

```python
def resolve(self, groups: list[str] | None=None) -> list[ToolSpec]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [self._specs[name] for name in names if name in self._specs]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._groups.values
set
self._groups.get
seen.add
names.append
```

<a id="fn-ef8fcb0f6177cbe0"></a>

## ToolRegistry.unregister

源码：[L50](D:/Project/learnLittle/app/ai_service/tool_registry.py:50)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

移除 spec，并从各组清除所有同名引用。测试动态注册结束需清理，避免污染后续。

**输入与签名**

```python
def unregister(self, name: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self._specs.pop
self._groups.values
names.remove
```

<a id="fn-1f92bd767d182f2e"></a>

## ToolRegistry.bind

源码：[L56](D:/Project/learnLittle/app/ai_service/tool_registry.py:56)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

对已注册工具优先使用 spec.fn，否则从当前用户内置闭包取函数。没有实现的工具不加入返回映射。

**输入与签名**

```python
def bind(self, builtins: dict[str, Callable]) -> dict[str, Callable]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {spec.name: spec.fn or builtins[spec.name] for spec in self.resolve() if spec.fn is not None or spec.name in builtins}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self.resolve
```

<a id="fn-aebc7577c31a9772"></a>

## ToolRegistry.groups_for

源码：[L63](D:/Project/learnLittle/app/ai_service/tool_registry.py:63)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

根据工具取 base+自身组，写笔记额外提供 note_read，未知返回 None。支持步骤先读真实内容再写。

**输入与签名**

```python
def groups_for(self, name: str) -> list[str] | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
return list(dict.fromkeys(groups))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
self.get
groups.append
list
dict.fromkeys
```
