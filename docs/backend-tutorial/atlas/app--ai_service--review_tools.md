# app/ai_service/review_tools.py

[源码](D:/Project/learnLittle/app/ai_service/review_tools.py) | [任务流程 07](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

回顾 service 到 Agent 文本工具的薄适配。

## 本文件导航

- [get_today_reviews_tool](#fn-075e89dba3f93937)
- [mark_reviewed_tool](#fn-553dcbd38b9e63e2)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
REVIEW_TOOL_SPECS = ({'name': 'get_today_reviews_tool', 'description': '获取今日待回顾的笔记列表', 'fn': get_today_reviews_tool}, {'name': 'mark_reviewed_tool', 'description': '标记一条回顾记录为已完成', 'fn': mark_reviewed_tool})
```

<a id="fn-075e89dba3f93937"></a>

## get_today_reviews_tool

源码：[L12](D:/Project/learnLittle/app/ai_service/review_tools.py:12)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

把当前用户与 session 交给回顾 service 的文本格式化入口。只读工具，不另造复习业务逻辑。

**输入与签名**

```python
async def get_today_reviews_tool(db: AsyncSession, user_id: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await review_service.format_today_reviews_text(db, user_id)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
review_service.format_today_reviews_text
```

<a id="fn-553dcbd38b9e63e2"></a>

## mark_reviewed_tool

源码：[L16](D:/Project/learnLittle/app/ai_service/review_tools.py:16)；任务：[第 07 章](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md)。

委托 service 完成 review_id 并给出文本，真正 commit 在绑定工具闭包。review_id 来自查询结果，不该由模型杜撰。

**输入与签名**

```python
async def mark_reviewed_tool(db: AsyncSession, user_id: str, review_id: int, quality: int=3) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return await review_service.complete_review_text(db, user_id, review_id, quality)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
review_service.complete_review_text
```
