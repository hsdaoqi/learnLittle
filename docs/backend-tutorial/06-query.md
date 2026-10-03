# 06 发出一次 `/chat/query`

本章是整个项目的主干。核心源码：[query_service.py](D:/Project/learnLittle/app/services/query_service.py)，路由在 [chat_router.py](D:/Project/learnLittle/app/routers/chat_router.py)，会话与消息数据操作在 [chat_service.py](D:/Project/learnLittle/app/services/chat_service.py)。

实际 HTTP 地址还要加 `/api/v1`。这里不启动服务器，只用请求示意理解路径：

```json
{
  "message": "先搜索我的 Python 笔记，然后总结共同难点",
  "top_k": 5,
  "enable_thinking": false,
  "idempotency_key": "study-turn-001"
}
```

## 1. 先保存“用户说了什么”

路由完成鉴权和 Schema 校验，把 session factory 直接交给 `query_service.stream_query` 流生成器。`chat_service` 只负责会话与消息数据操作，不再提供兼容问答入口。

`query_service.stream_query` 先申请 SSE 槽。`_key(user_id,key,role)` 计算用户隔离、角色隔离的 SHA256，分别用于 user 和 assistant 消息。

没有已有 key 时：验证现有会话归属或创建会话 -> `_add_message` 加 user 消息 -> **commit** -> 可选更新缓存 -> 发 meta。当前用户消息这时已经是 SQL 事实，后续 RAG 失败不会把它吞掉。

## 2. 先判断是不是重复请求

| 数据库状态 | 处理 |
| --- | --- |
| 没有同用户同角色 key | 执行新一轮 |
| key 相同但正文/指定会话不同 | error，不把不同请求当重试 |
| user 和 assistant 都存在 | meta -> response_replace 存档回答 -> done(replayed=true) |
| 只有 user | 报已接收，不自动再跑可能有副作用的工具 |

唯一索引还处理并发插入竞争，`IntegrityError` 返回重复提交提示。key 按用户和角色计算，**不是按会话计算**，因此同用户不应跨会话复用同一业务 key。

它保证的是这个入口不随意重放已有请求，不是所有工具的 exactly-once，也不是一个会话同一时刻只能有一轮。没有 key 的请求不享受这一套消息防重。

## 3. 同时准备资料和记忆

`asyncio.gather` 并行：

- `_retrieve`：当前可见问题 -> 门控 -> 可选 HyDE -> 双源检索 -> 摘要。失败/超时返回空参考与 unavailable 决策。
- `_load_memory`：单独 SQL session 读取当前 message_id 之前的本会话完整消息和摘要。

`visible_question` 去掉引用笔记块，避免标题和检索被引用正文淹没；原始 raw 仍被保存，引用可另进 Agent 系统上下文。

`build_agent_history` 去掉已被摘要覆盖的 message_id，只考虑剩余原消息，再按 Token 配额从新到旧取。它不先套 Redis 20 条、6 轮或每条 400 字限制。当前问题、摘要、RAG 和工具 scratchpad 都占预算。

## 4. 把控制权交给图

`resolve_agent_thinking` 根据请求、附件 ID 和协议决定实际 thinking，必要时发 notice。随后 `stream_chat_graph` 分类并执行 ReAct 或 Plan。详见下一章。

service 逐条消费事件，同时在服务端维护最终答案：

| 事件 | 服务端如何处理 |
| --- | --- |
| `response` | 追加 content |
| `response_replace` | 用 content 替换全部已积累文本，不能继续追加旧草稿 |
| `stream_done` | 内部终态，以 full_response 覆盖积累值，不直接当公开 done |
| `tool_end` | 记录名称、成功/错误和结果，供最终 payload |
| `routing` | 保存路由元数据，稍后合入 done |
| `plan_fallback` | 记录实际降级到 react |
| `error` | 发送后结束，不再保存一条伪成功助手回答 |

## 5. 再保存“助手最后回答了什么”

有效答案形成后，用新 SQL session 重新确认会话，插入 assistant，更新 session.updated_at，默认标题先用短问句占位，然后 **commit**。

之后更新 Redis、安排标题和摘要后台任务，最后发 `done`。`done.answer`、`assistant_message.content` 和 SQL 保存的是最终替换后的回答，不应包含被反思废弃的旧稿。

这并不保证用户断网时一定看到 done；只是本代码把“成功完成事件”放在落库成功之后。

## 6. 断开和失败时谁收尾

生成器用 `aclosing` 关闭下游流；图取消生产 task 并等待回收；Plan 批量执行也取消步骤任务。最外层 `finally` 清除 trace 上下文并释放 SSE 槽。Python 取消不应被随便当作普通可重试错误吞掉。

在工具写入后发生失败时，用户消息和工具产生的数据可能已经在 SQL，助手完整回答则可能没有。下一次查询应先核对状态，不能假设“没有 done 就什么都没做”。

**断点顺序**：`chat_query` -> `query_service.stream_query` 第一次 commit -> `_retrieve/_load_memory` -> `build_agent_history` -> `stream_chat_graph` -> 第二次 commit -> `spawn_background_task`。

**练习**：为什么先存用户消息再调用模型？为了保留已接受请求、建立幂等事实，并让失败仍可追踪；这不是所有操作共享一个超长数据库事务。
