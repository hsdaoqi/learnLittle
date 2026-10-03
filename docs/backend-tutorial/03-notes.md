# 03 保存一篇笔记，再整理分类

入口：[note_router.py](D:/Project/learnLittle/app/routers/note_router.py)、[category_router.py](D:/Project/learnLittle/app/routers/category_router.py)。核心：[note_service.py](D:/Project/learnLittle/app/services/note_service.py)、[category_service.py](D:/Project/learnLittle/app/services/category_service.py)。

## 任务 A：创建“Python 异步”笔记

```text
NoteCreate 校验
  -> create_note
  -> ensure_category：分类存在、属于当前用户、未删除
  -> Note 入 session -> flush -> refresh
  -> ensure_review_record：建立回顾记录
  -> defer_note_index：登记提交后工作
  -> 请求依赖 commit
  -> after_commit 派发后台索引
  -> sync_latest 用新 session 重新读取
  -> index_note -> TextSplitter -> Chroma notes collection
```

这里同时形成三种状态：SQL 正文、回顾记录、派生向量。前两者在 SQL 事务内，向量在成功提交后更新。所以“接口已返回，立刻向量搜索不到”可能是后台同步尚未完成，不一定是正文没保存。

`defer_after_commit` 把工厂放入 `session.info`，同一个 key 后写覆盖前写；回滚事件清空任务。后台按笔记 key 串行，并重新读取最新 SQL，不沿用请求中旧 ORM 实例。进程崩溃仍可能丢任务，它不是可靠消息队列。

`index_note` 把标题和正文组装切片，先删除旧切片，再写新切片。只有拼接后的整体为空才只删除；有标题而正文为空仍会索引标题。删除后写失败会暂时没有向量，SQL 正文并不会因此回滚。

## 任务 B：部分修改而不是整体覆盖

`NoteUpdate.model_dump(exclude_unset=True)` 保留“本次真的传了的字段”。例如：

```json
{"is_pinned": true}
```

只调整置顶；不会把标题正文清空。

```json
{"category_id": null}
```

表示移出分类；省略 `category_id` 则表示不改。`format` 创建后不改。传入 title/content 字段会触发重新索引，即使值与原来相同；只改标签、分类、置顶不重建正文向量。

`get_active_note` 是很多操作共同的权限关口：按笔记 ID、用户和未删除过滤，不允许通过猜测 ID 读别人的笔记。

## 任务 C：三种“搜索”不是一个函数

| 需求 | 入口与实现 |
| --- | --- |
| 笔记列表里按关键词过滤 | `list_notes` 的 SQL 过滤、分页和排序 |
| 全局关键词搜索 | `keyword_search` 尝试 MySQL FULLTEXT，失败或适用条件不满足则 LIKE |
| AI 找相关笔记 | 工具先做 Chroma 检索、按 note_id 去重并回 SQL 校验，再视结果回退关键词 |

`_escape_like` 把用户 `%`、`_` 等当字面量，避免用户输入意外变成任意匹配。LIKE 结果标题命中显示分 1.0，正文命中 0.5；FULLTEXT 返回的展示分是固定 0.9，不应当拿这些数和向量相似度比较。

本地迁移链后面的 review 迁移删除过 FULLTEXT 索引，所以不能仅凭早期迁移“创建了”就断言当前数据库仍有它。LIKE 兜底也是实际可达路径。

## 任务 D：删除与恢复笔记

软删除设置 `deleted_at`，回收站可列出；恢复清空删除时间并恢复索引；永久删除移除 SQL 记录并安排清向量。当前 `permanent_delete_note` 不要求笔记已经在回收站，这是代码行为，不要误以为与分类永久删除一样。

批量处理逐条捕获业务错误并记录结果，但没有每条 savepoint，也不是捕获所有数据库错误后保证其他项成功。14 天清理由调度器触发 service，开发 reload 默认不会自动启动它。

## 任务 E：在三层分类树中移动

创建分类检查同父级活跃名称、父分类所有权与最大三层深度。移动时同时检查：

1. 目标父节点有效。
2. 不能移到自己或自己的后代，否则成环。
3. 目标深度加整个子树高度不能超过三层，不只检查当前节点。
4. 新位置不能同级重名。

`_load_active` 一次加载当前用户活跃分类，在内存计算 `_depth_of`、`_subtree_height`、`_is_descendant`；它不是无限递归向数据库发 SQL。

`get_category_tree` 用父 ID 分组、计直属笔记数，再嵌套 `build` 递归组树。直属数不是所有后代笔记总数。

## 任务 F：删除分类不是删整棵树

假设 `学习 -> Python -> 异步`，Python 有直属笔记：

```text
删除 Python 前：学习 -> Python -> 异步
删除 Python 后：学习 -> 异步
Python 的直属笔记：变为未分类
Python：进入回收站
```

恢复会拉回已删除祖先链和可恢复的已删除后代；但已经提升的活跃孩子、已经变未分类的笔记不会凭空重新挂回。这不是完整撤销操作。

物理删除分类先保护仍活跃的直接孩子，避免 FK CASCADE 误删；已删除后代仍可能由级联一起移除。

合并分类先拒绝目标在来源子树内、来源之间存在祖先/后代关系等冲突，再迁移笔记与孩子并软删来源。排序要求同父级 ID 集合匹配，当前不是显式检查无重复的严格排列校验。`_next_sort_order` 中 `(max or -1)+1` 把 max=0 当成空，是应当知道的现存边界，教程不在这里偷偷修复它。

**练习**：把分类移到第三层时，为何有孩子的分类会被拒绝？因为限制施加于移动后整个子树，而非单节点。
