# app/models/__init__.py

[源码](D:/Project/learnLittle/app/models/__init__.py) | [任务流程 01](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

导入并重新导出所有 ORM 类型，让 Base.metadata 收齐表；不是空包标记。

## 本文件导航

本文件没有显式函数；请看下方结构声明，不计作遗漏。

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
__all__ = ['Base', 'ChatMessage', 'ChatSession', 'ChatSummary', 'KnowledgeDocument', 'ModelPricing', 'ModelTrace', 'Note', 'NoteCategory', 'NoteTemplate', 'ReviewRecord', 'User']
```


## 包导入

```python
from app.models.base import Base

from app.models.category import NoteCategory

from app.models.chat import ChatMessage, ChatSession, ChatSummary

from app.models.knowledge import KnowledgeDocument

from app.models.note import Note

from app.models.note_template import NoteTemplate

from app.models.review import ReviewRecord

from app.models.usage import ModelPricing, ModelTrace

from app.models.user import User
```
