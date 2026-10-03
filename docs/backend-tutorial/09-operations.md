# 09 观察用量、限制请求和清理数据

## 任务 A：理解一次 429

[rate_limit.py](D:/Project/learnLittle/app/core/rate_limit.py) 按 endpoint 前缀决定配额，用 access 身份或匿名 IP 作为 key，Redis `INCR` 配合首次 `EXPIRE` 实现固定窗口，同时检查全局与接口额度。不是 token bucket，也不是滑动窗口。

`check_named_limit` 给彻底删除等操作附加业务内计数。中间件在测试配置可关闭，不代表生产默认关闭。当前 SSE Token 不被 identity_for 识别为 access 用户，因此落匿名/IP 桶；`/auth/sse-token` 也会受 auth 前缀限流。

[sse_slot.py](D:/Project/learnLittle/app/ai_service/sse_slot.py) 另外控制同时打开的主聊天连接数，Redis 不可用时退回进程内计数。速率与并发不是一回事。计数 TTL 是 120 秒且不续租，不能把它当成严格覆盖任意长连接生命周期的分布式信号量。

## 任务 B：模型调用花费记录在哪里

[usage_service.py](D:/Project/learnLittle/app/services/usage_service.py) 用 ContextVar 绑定 request/user/session/stage。`set_trace_stage` 复制字典再 set，避免并行步骤共享修改同一个字典。没有 user 或没有 factory 时跳过持久化，不创建匿名账单。

两类记录入口：

- 直接 httpx 补全/embedding/注入函数使用 `UsageTimer` 与 `record_text_call`。
- LangChain 使用 [ModelUsageCallback](D:/Project/learnLittle/app/ai_service/usage_callback.py)，按 run_id 记录每次模型调用的输入、工具声明、输出和耗时。

一个用户问题可能调用分类、规划、多个工具轮次、综合、反思、标题和摘要，所以不是“每次 /chat/query 只插一条 trace”。工具返回结果进入下一次模型输入时，也占输入 Token。

`parse_usage` 优先服务端计数，明确的 0 要保留；没有字段才按字符估算。`record_usage` 用独立事务，计量失败只记日志。它记录调用级用量，不是完整工具审计或完整分布式 trace。

## 任务 C：费用怎么来的

`seed_model_pricing` 使用代码里的种子表，启动时会更新已有行。`get_usage_summary` 按用户、天数、可选 session 过滤，统计总调用、阶段、模型、平均延迟，按每千 Token 输入/输出价格计算。

这些值是项目本地估算口径，不是供应商实时账单，教程也不声称种子价格是当前官方价格。未知模型可能被赋予默认价格，缺价格则算 0；货币输出固定为 cost_cny 等字段。不能把返回 0 推断成模型免费。

## 任务 D：后台任务何时执行

[after_commit.py](D:/Project/learnLittle/app/core/after_commit.py) 注册 SQLAlchemy Session 的提交/回滚监听；[task_runner.py](D:/Project/learnLittle/app/core/task_runner.py) 跟踪 asyncio tasks，同 key 等前一个执行完，完成回调移除引用。关闭应用时限时等待，再取消剩余任务。

当前是单进程内的协调，不是 Celery、持久化 Outbox 或跨 worker 分布式锁。多进程也会各自拥有 `_by_key`。任务异常通常只写日志，应当知道响应成功不代表所有派生副作用已完成。

## 任务 E：14 天清理

[scheduler.py](D:/Project/learnLittle/app/core/scheduler.py) 注册笔记/分类定时任务，包装器自己创建数据库资源和事务，调用各自 cleanup service。按 `deleted_at` 与阈值做物理删除，不是按笔记创建时间删除。

清理条件和定时器是否启动是两回事：默认 `api_reload=True` 时没有后台定时器。不要等待开发服务器自动清理再判断 service 有没有实现。

**排查路径**：

| 现象 | 首先看哪里 |
| --- | --- |
| 正文保存成功、语义搜索落后 | 提交后任务日志、embedding、Chroma |
| 登录 403 | 失败锁定计数，不一定是中间件 |
| 请求 429 | rate_limit 配置与 key |
| SSE 内容 error | 流内部错误，HTTP 头可能已发出 |
| 模型调用成功、usage 空 | ContextVar 用户、session factory、落库异常 |
| 收到 response 但没有 done | 后续反思/落库/连接失败；核查 SQL 和工具副作用 |
