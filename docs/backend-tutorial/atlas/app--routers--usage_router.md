# app/routers/usage_router.py

[源码](D:/Project/learnLittle/app/routers/usage_router.py) | [任务流程 09](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

当前用户用量聚合 HTTP 入口。

## 本文件导航

- [usage_summary](#fn-8e5292c56746ec19)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
router = APIRouter()
```

<a id="fn-8e5292c56746ec19"></a>

## usage_summary

源码：[L15](D:/Project/learnLittle/app/routers/usage_router.py:15)；任务：[第 09 章](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md)。

接有界 days 与可选 session_id，使用当前用户查询用量/费用聚合。未登录拒绝，跨用户数据由 service 条件隔离。

**输入与签名**

```python
async def usage_summary(days: int=Query(30, ge=1, le=365), session_id: str | None=Query(default=None), user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/usage/summary', summary='模型调用用量与费用汇总')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=data)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Query
Depends
get_usage_summary
success_response
router.get
```
