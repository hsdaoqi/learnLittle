# app/services/review_service.py

[源码](D:/Project/learnLittle/app/services/review_service.py) | [任务流程 04](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

固定间隔回顾状态与 Agent 文本适配；没有完整复习事件日志。

## 本文件导航

- [next_interval](#fn-ee3ee499f40d7b09)
- [_not_found](#fn-30053d070e930427)
- [_dump](#fn-f21172db41f891c9)
- [ensure_review_record](#fn-4d30a929544ff5f7)
- [get_today_reviews](#fn-ef71870fd243ba05)
- [mark_reviewed](#fn-4e2c8662a61e58ed)
- [get_review_stats](#fn-03c7c26cfa46e7f8)
- [format_today_reviews_text](#fn-ad4dcf019b8ed8d3)
- [complete_review_text](#fn-1dab3160da877d63)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
EBBINGHAUS_INTERVALS = [1, 2, 4, 7, 15, 30]
```

<a id="fn-ee3ee499f40d7b09"></a>

## next_interval

源码：[L24](D:/Project/learnLittle/app/services/review_service.py:24)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

在固定间隔表中前进一档，未知当前间隔回到一日，末档按实现封顶。quality 不参与计算，不是自适应 SM-2。

**输入与签名**

```python
def next_interval(current_days: int) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return EBBINGHAUS_INTERVALS[min(index + 1, len(EBBINGHAUS_INTERVALS) - 1)]
return EBBINGHAUS_INTERVALS[0]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
EBBINGHAUS_INTERVALS.index
min
len
```

<a id="fn-30053d070e930427"></a>

## _not_found

源码：[L32](D:/Project/learnLittle/app/services/review_service.py:32)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

创建回顾记录不存在/无权访问业务异常。供按用户检查失败统一使用。

**输入与签名**

```python
def _not_found() -> BusinessError
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return BusinessError(code=ErrorCode.REVIEW_NOT_FOUND, http_status=404)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
BusinessError
```

<a id="fn-f21172db41f891c9"></a>

## _dump

源码：[L36](D:/Project/learnLittle/app/services/review_service.py:36)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

把 ReviewRecord 与关联笔记转换为响应字典。关联的 note 标题正文用于学习展示，不改复习状态。

**输入与签名**

```python
def _dump(review: ReviewRecord, note: Note) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'review_id': review.id, 'note_id': review.note_id, 'note_title': note.title, 'note_content': note.content, 'review_count': review.review_count, 'interval_days': review.interval_days, 'next_review_at': review.next_review_at}
```

<a id="fn-4d30a929544ff5f7"></a>

## ensure_review_record

源码：[L48](D:/Project/learnLittle/app/services/review_service.py:48)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

对笔记查已有记录，有则返回，无则创建初始 interval=1 的到期记录。创建笔记因此能进入今日待回顾。

**输入与签名**

```python
async def ensure_review_record(db: AsyncSession, user_id: str, note_id: str) -> ReviewRecord
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return existing
return review
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(ReviewRecord).where(ReviewRecord.note_id == note_id, ReviewRecord.user_id == user_id))).scalar_one_or_none
db.execute
select(ReviewRecord).where
select
ReviewRecord
datetime.now
db.add
db.flush
db.refresh
```

<a id="fn-ef71870fd243ba05"></a>

## get_today_reviews

源码：[L76](D:/Project/learnLittle/app/services/review_service.py:76)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

查询当前用户活跃笔记中已经到期的回顾记录并整理结果。不会自动标记这些项完成。

**输入与签名**

```python
async def get_today_reviews(db: AsyncSession, user_id: str) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [_dump(review, note) for review, note in rows]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
datetime.now
(await db.execute(select(ReviewRecord, Note).join(Note, ReviewRecord.note_id == Note.id).where(and_(ReviewRecord.user_id == user_id, ReviewRecord.next_review_at <= now, Note.deleted_at.is_(None))).order_by(ReviewRecord.next_review_at.asc(), ReviewRecord.id.asc()))).all
db.execute
select(ReviewRecord, Note).join(Note, ReviewRecord.note_id == Note.id).where(and_(ReviewRecord.user_id == user_id, ReviewRecord.next_review_at <= now, Note.deleted_at.is_(None))).order_by
select(ReviewRecord, Note).join(Note, ReviewRecord.note_id == Note.id).where
select(ReviewRecord, Note).join
select
and_
Note.deleted_at.is_
ReviewRecord.next_review_at.asc
ReviewRecord.id.asc
_dump
```

<a id="fn-4e2c8662a61e58ed"></a>

## mark_reviewed

源码：[L95](D:/Project/learnLittle/app/services/review_service.py:95)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

校验当前用户记录，写 review_count/quality/reviewed_at 并计算 next_review。初始一日间隔首次完成进入两日，提交由调用方负责。

**输入与签名**

```python
async def mark_reviewed(db: AsyncSession, user_id: str, review_id: int, quality: int=3) -> ReviewRecord
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return review
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(ReviewRecord).where(ReviewRecord.id == review_id, ReviewRecord.user_id == user_id))).scalar_one_or_none
db.execute
select(ReviewRecord).where
select
_not_found
datetime.now
next_interval
timedelta
db.flush
db.refresh
```

<a id="fn-03c7c26cfa46e7f8"></a>

## get_review_stats

源码：[L120](D:/Project/learnLittle/app/services/review_service.py:120)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

按记录当前状态统计学习情况与连续性。每笔记只保留最新 reviewed_at，不是全量历史事件表。

**输入与签名**

```python
async def get_review_stats(db: AsyncSession, user_id: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'pending_today': int(pending_today or 0), 'total_reviews': int(total_reviews or 0), 'completed_today': int(completed_today or 0), 'streak_days': streak_days}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
datetime.now
now.replace
(await db.execute(select(func.count()).select_from(ReviewRecord).join(Note, ReviewRecord.note_id == Note.id).where(ReviewRecord.user_id == user_id, ReviewRecord.next_review_at <= now, Note.deleted_at.is_(None)))).scalar_one
db.execute
select(func.count()).select_from(ReviewRecord).join(Note, ReviewRecord.note_id == Note.id).where
select(func.count()).select_from(ReviewRecord).join
select(func.count()).select_from
select
func.count
Note.deleted_at.is_
(await db.execute(select(func.coalesce(func.sum(ReviewRecord.review_count), 0)).where(ReviewRecord.user_id == user_id))).scalar_one
select(func.coalesce(func.sum(ReviewRecord.review_count), 0)).where
func.coalesce
func.sum
(await db.execute(select(func.count()).select_from(ReviewRecord).where(ReviewRecord.user_id == user_id, ReviewRecord.reviewed_at >= today_start))).scalar_one
select(func.count()).select_from(ReviewRecord).where
timedelta
(await db.execute(select(func.count()).select_from(ReviewRecord).where(ReviewRecord.user_id == user_id, ReviewRecord.reviewed_at >= check_date, ReviewRecord.reviewed_at < day_end))).scalar_one
int
```

<a id="fn-ad4dcf019b8ed8d3"></a>

## format_today_reviews_text

源码：[L185](D:/Project/learnLittle/app/services/review_service.py:185)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

复用今日查询并转为 Agent 可读列表，保留回顾/笔记身份信息。只读适配，方便下一步标记真实 review_id。

**输入与签名**

```python
async def format_today_reviews_text(db: AsyncSession, user_id: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '今日没有待回顾的笔记'
return f'今日待回顾 ({len(reviews)} 篇):\n' + '\n'.join(lines)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_today_reviews
len
'\n'.join
```

<a id="fn-1dab3160da877d63"></a>

## complete_review_text

源码：[L198](D:/Project/learnLittle/app/services/review_service.py:198)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

复用 mark_reviewed 完成指定记录并返回下次日期文字。工具外层还需 commit，字符串本身不替代事务提交。

**输入与签名**

```python
async def complete_review_text(db: AsyncSession, user_id: str, review_id: int, quality: int=3) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'回顾完成！下次回顾时间: {review.next_review_at.strftime('%Y-%m-%d')}'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
mark_reviewed
review.next_review_at.strftime
```
