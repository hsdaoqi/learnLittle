# app/ai_service/langchain_tools.py

[源码](D:/Project/learnLittle/app/ai_service/langchain_tools.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

注册表描述到 StructuredTool 的轻量参数 Schema 适配。

## 本文件导航

- [json_schema_to_model](#fn-ba1bc523d4a3ce2e)
- [spec_to_langchain_tool](#fn-45274d44571b7445)
- [spec_to_langchain_tool._run](#fn-e0a69ac3dce42cd4)
- [build_langchain_tools](#fn-fcb858d0f69c91d6)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
_JSON_TYPES = {'string': str, 'integer': int, 'number': float, 'boolean': bool}
```

<a id="fn-ba1bc523d4a3ce2e"></a>

## json_schema_to_model

源码：[L25](D:/Project/learnLittle/app/ai_service/langchain_tools.py:25)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

把工具 parameters 的简单属性/required 转动态 Pydantic 参数类。只支持当前简单类型映射，不是完整 JSON Schema 验证器。

**输入与签名**

```python
def json_schema_to_model(name: str, schema: dict | None) -> type[BaseModel]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return create_model(model_name)
return create_model(model_name, **fields)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
schema.get
set
props.items
_JSON_TYPES.get
spec.get
Field
''.join
part.capitalize
name.split
create_model
```

<a id="fn-45274d44571b7445"></a>

## spec_to_langchain_tool

源码：[L45](D:/Project/learnLittle/app/ai_service/langchain_tools.py:45)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

按 spec.fn 优先、绑定内置函数其次找到实现，创建 args_schema 与 StructuredTool。返回 LangChain 可调用对象，尚未执行工具。

**输入与签名**

```python
def spec_to_langchain_tool(spec: ToolSpec, bound: dict[str, Callable[..., Any]])
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return StructuredTool.from_function(name=spec.name, description=spec.description, coroutine=_run, args_schema=model)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
bound.get
json_schema_to_model
StructuredTool.from_function
```

<a id="fn-e0a69ac3dce42cd4"></a>

## spec_to_langchain_tool._run

源码：[L52](D:/Project/learnLittle/app/ai_service/langchain_tools.py:52)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

删除值为 None 的可选参数，让底层 Python 默认值生效，再调用同步/异步实现；不存在实现返回未知工具文字。保留外层绑定用户，模型不提供 user_id。

**输入与签名**

```python
async def _run(**kwargs: Any) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'未知工具: {spec.name}'
return await result if isawaitable(result) else result
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
kwargs.items
fn
isawaitable
```

<a id="fn-fcb858d0f69c91d6"></a>

## build_langchain_tools

源码：[L67](D:/Project/learnLittle/app/ai_service/langchain_tools.py:67)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

为当前用户绑定注册表工具，按组解析并在只读模式排除非 parallel_safe。返回提供给模型的工具集合，而不是所有路由都开放。

**输入与签名**

```python
def build_langchain_tools(user_id: str, session_factory, groups: list[str] | None=None, *, read_only: bool=False)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [spec_to_langchain_tool(spec, bound) for spec in registry.resolve(groups) if not read_only or spec.parallel_safe]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
registry.bind
bind_user_tools
spec_to_langchain_tool
registry.resolve
```
