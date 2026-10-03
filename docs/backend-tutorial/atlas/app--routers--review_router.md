# app/routers/review_router.py

[源码](D:/Project/learnLittle/app/routers/review_router.py) | [任务流程 04](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

今日回顾、完成和统计 HTTP 入口。

## 本文件导航

- [get_today_reviews](#fn-0ce154e0257dff08)
- [mark_reviewed](#fn-854c3cb3c61c176e)
- [get_review_stats](#fn-b9885d690d559a10)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
router = APIRouter()
```

<a id="fn-0ce154e0257dff08"></a>

## get_today_reviews

源码：[L21](D:/Project/learnLittle/app/routers/review_router.py:21)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

获取当前用户到期复习项目并包装成功响应。只读，不在取列表时标记已完成。

**输入与签名**

```python
async def get_today_reviews(user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/review/today', summary='今日待回顾')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'reviews': items, 'count': len(items)})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
review_service.get_today_reviews
ReviewItem.model_validate(item).model_dump
ReviewItem.model_validate
success_response
len
router.get
```

<a id="fn-854c3cb3c61c176e"></a>

## mark_reviewed

源码：[L33](D:/Project/learnLittle/app/routers/review_router.py:33)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

接 review_id 与质量字段，调用 service 更新间隔/下次时间。质量目前存储而非自适应间隔输入。

**输入与签名**

```python
async def mark_reviewed(review_id: int, quality: int=Query(default=3, ge=0, le=5), user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/review/{review_id}/complete', summary='标记回顾完成')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=ReviewCompleteResponse(review_id=review.id, next_review_at=review.next_review_at, interval_days=review.interval_days, review_count=review.review_count).model_dump(mode='json'))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Query
Depends
review_service.mark_reviewed
success_response
ReviewCompleteResponse(review_id=review.id, next_review_at=review.next_review_at, interval_days=review.interval_days, review_count=review.review_count).model_dump
ReviewCompleteResponse
router.post
```

<a id="fn-b9885d690d559a10"></a>

## get_review_stats

源码：[L51](D:/Project/learnLittle/app/routers/review_router.py:51)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

按用户请求当前回顾统计并返回。不是读取独立的完整历史打卡事件流。

**输入与签名**

```python
async def get_review_stats(user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/review/stats', summary='回顾统计')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=ReviewStats.model_validate(stats).model_dump())
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
review_service.get_review_stats
success_response
ReviewStats.model_validate(stats).model_dump
ReviewStats.model_validate
router.get
```
