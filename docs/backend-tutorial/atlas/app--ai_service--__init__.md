# app/ai_service/__init__.py

[源码](D:/Project/learnLittle/app/ai_service/__init__.py) | [任务流程 01](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

Python 包入口/命名空间文件；本快照没有显式函数，具体导入/赋值见结构声明。

## 本文件导航

本文件没有显式函数；请看下方结构声明，不计作遗漏。

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
__all__ = ['get_agent_runner', 'get_classifier_fn', 'get_critique_fn', 'get_react_streamer', 'set_agent_runner', 'set_classifier_fn', 'set_critique_fn', 'set_react_streamer']
```


## 包导入

```python
from app.ai_service.query_classifier import get_classifier_fn, set_classifier_fn

from app.ai_service.react_agent import get_react_streamer, set_react_streamer

from app.ai_service.reflection import get_critique_fn, set_critique_fn

from app.ai_service.runner import get_agent_runner, set_agent_runner

from app.ai_service.tools import register_builtin_tools
```
