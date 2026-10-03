# app/ai_service/models.py

[源码](D:/Project/learnLittle/app/ai_service/models.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

角色模型名选择，共享现有 key/base_url。

## 本文件导航

- [settings_for_role](#fn-8978fafb1b08fe9b)
<a id="fn-8978fafb1b08fe9b"></a>

## settings_for_role

源码：[L6](D:/Project/learnLittle/app/ai_service/models.py:6)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

复制 Settings，只替换角色对应 llm_model；reflection/title 有指定回退链，空值复用主模型。key/base_url 不变，所以不是多供应商独立认证。

**输入与签名**

```python
def settings_for_role(settings: Settings, role: str) -> Settings
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return settings.model_copy(update={'llm_model': names.get(role) or settings.llm_model})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
settings.model_copy
names.get
```
