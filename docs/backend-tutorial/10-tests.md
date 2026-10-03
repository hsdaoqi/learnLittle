# 10 通过迁移和测试检查你的理解

## 任务 A：从空库演进到当前结构

迁移入口：[alembic/env.py](D:/Project/learnLittle/alembic/env.py)。它加载配置，以 `Base.metadata` 作为结构描述，在线用异步 engine + `run_sync` 桥接 Alembic 同步迁移；离线模式只生成 SQL。

实际版本顺序不是文件名排序：

| revision | 主要变化 |
| --- | --- |
| e471331632c9 | users |
| 342a95208d0f | note_categories、notes |
| b7c1d4e8f901 | knowledge_documents |
| c8d2e5f0a123 | chat_sessions、chat_messages |
| d9e3f6a1b234 | chat_summaries |
| e0f4a7b2c345 | note_templates、MySQL ngram FULLTEXT |
| 53816adf617f | review_records，同时删除上述 FULLTEXT 索引 |
| e2aebef3f9e7 | users.email_verified |
| c3e9f2a7b890 | model_traces、model_pricing |
| f1a244c10001 | title_manual、message idempotency_key 和唯一索引；保护旧标题 |

ORM 定义不会自动替你更新已存在数据库。`upgrade` 改到下一版，`downgrade` 做逆向结构操作，可能删除数据，不能当“无损撤销”练习。这里没有运行任何迁移。部署前要单独确认数据库地址、备份、已有数据与迁移 SQL。

`f1...` 的 additive migration 测试保留旧消息并保护既有非默认标题。它证明指定迁移场景，不证明任意 MySQL 版本和所有历史脏数据都能无故障迁移。

## 任务 B：隔离依赖再测业务

[tests/conftest.py](D:/Project/learnLittle/tests/conftest.py) 自动隔离设置，阻止真实 `.env` 影响模型路径，清除注入状态。client 使用临时 SQLite、fakeredis、临时 Chroma 和依赖覆盖，结束时清后台任务和资源。

`set_embed_fn/set_react_streamer/set_plan_fn/...` 都是理解测试的钥匙：调用者走同一业务流程，但不访问真实模型。`client.override_session` 仍模拟 commit/rollback，所以能测提交后索引是否错误触发。

SQLite 不等于 MySQL，fakeredis 不等于有网络分区的 Redis；这些测试不能替代 MySQL ngram、SMTP 和实际供应商协议的集成验证。

## 任务 C：按风险读测试

| 测试文件 | 重点观察 |
| --- | --- |
| test_notes_categories | CRUD、用户隔离、树深度/成环、删除提升、恢复、排序合并、模板和 AI 注入 |
| test_persistence_alignment | 提交才索引、回滚不索引、元数据修改不索引、缓存次序、usage 0、旧数据迁移 |
| test_query_lifecycle | 用户消息先保存、最终替换落库、防重与跨用户、SQL 全历史、标题竞争、邮箱默认要求、SSE 单次票、取消 |
| test_agent_alignment | 工具副作用重试护栏、规划依赖、并行读串行写、反思事件时序、真实 LangChain 假模型循环、ContextVar 隔离 |
| test_retriever_predict | sentence-transformers 风格 predict 接口 |
| test_thinking | 协议判断、主/角色开关、附件互斥、超时 |
| test_usage | 估算、空统计、AI 记录、用户隔离、未登录拒绝 |

每个测试及其内部 fake/fixture 都在逐函数详解中有单独条目。测试中的 fake 不是生产降级实现。例如会主动等待的 `stalled` 是在制造超时，不是项目平时就会 sleep 那么久。

文档编写没有重新执行业务测试。需要自己执行时，应先看 conftest 的隔离设置；项目后端测试命令示例：

```powershell
Set-Location D:\Project\learnLittle
.\.venv\Scripts\python.exe -m pytest tests -q
```

这不是要求启动前端，也不是文档检查所必需的步骤。

## 任务 D：用问题验证理解，不只看绿灯

1. 给 `defer_note_index` 登记任务后 rollback，为什么不会查向量库？检查 after_rollback 和对应回归用例。
2. 同一幂等 key 两次请求，如何区分已完成与在途？检查是否存在 assistant key。
3. 模型已写笔记后超时，为什么不能 Plan 整轮 fallback？检查 `wrote` 何时变 True。
4. 自检重写后 SQL 为何不能拼旧稿？追踪 `response_replace` 与 `stream_done`。
5. 摘要覆盖到 ID=100，但未摘要消息超过 20 条，哪些历史会保留？检查 `_load_memory` 与 budget，不用热缓存推断。
6. HTTP 资料请求能不能接受 SSE Token？比较两种 auth dependency。

每题可从任务章回到详解，再点函数源文件。能解释错误路径和副作用，比记住函数名更接近真正理解。

## 任务 E：源码变了，教程如何发现过期

只使用标准库、AST，不导入应用的检查：

```powershell
Set-Location D:\Project\learnLittle
.\.venv\Scripts\python.exe docs\backend-tutorial\tools\build.py --check
```

新增/删除函数、函数所在文件内容变化、遗漏解释、生成文档被改坏，检查会失败。更新时先改人工讲解和章节，再运行 inventory、build，最后 `--check`。单纯重新生成不能证明新逻辑已被人准确解释。
