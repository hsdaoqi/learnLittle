# 08 历史、摘要、标题和本地降级

## 任务 A：打开一个旧会话

[chat_service.py](D:/Project/learnLittle/app/services/chat_service.py) 负责会话列表、改标题、删除、完整消息列表。先验证用户归属，再返回数据。手动改标题设置 title_manual，避免后台自动标题覆盖。

[chat_cache.py](D:/Project/learnLittle/app/rag/chat_cache.py) 用 `chat:sessions:{user_id}` 缓存列表，短 TTL；用 `chat:msgs:{session_id}` 的 List 存热消息。LPUSH 最新在头，读取后 reverse 才得到从旧到新。回填必须逐条按照正序 LPUSH，不能错误地重复 reverse。

缓存异常多数吞掉并记录，不破坏 SQL 数据。但认证用 Redis 的失败语义不同，不能概括为“整个项目 Redis 坏了也没关系”。

完整消息历史接口读 SQL，不被热缓存窗口截断。新主链的 `_load_memory` 也直接读 SQL，缓存不是唯一记忆来源。

## 任务 B：聊天变长，怎样选历史

[chat_history.py](D:/Project/learnLittle/app/rag/chat_history.py) 只保留当前主链的 `build_agent_history`：从 SQL 全量消息中排除已摘要部分，按实际 Token 配额选择最近历史，保持 user/assistant 角色。太大的最近消息会缩短以符合额度，不再保留固定轮数或逐条字符截断的另一套算法。

历史配额近似为：

```text
模型上下文上限 - system预留 - safety预留 - scratchpad预留
               - 当前问题Tokens - 摘要Tokens - RAGTokens
```

scratchpad 是工具往返/生成空间，旧配置的 0 在新主链解释为自动预留 4000。TokenCounter 尝试 tokenizer，失败有估算；这不是所有供应商都完全精确的计费器。

旧 `CHAT_HISTORY_ROUNDS`、`CHAT_HISTORY_MAX_CHARS`、`TOKEN_RAG_CONTEXT_MAX`、`TOKEN_CURRENT_INPUT_ESTIMATE`、`TOKEN_HISTORY_MIN`、`TOKEN_SUMMARY_RESERVE` 已移除。历史预算扣的是问题、摘要和参考文本的实际计数；真正计费统计走供应商 usage，与预算计数不同。

## 任务 C：压缩旧对话

[memory.py](D:/Project/learnLittle/app/rag/memory.py)：

1. 检查总条数达到阈值。
2. 数上次 `last_message_id` 后新增消息条数，不把自增 ID 差直接当条数。
3. 最近 keep_recent 条留原文，较老的未摘要消息与旧摘要一起送模型。
4. `truncate_summary` 约束长度，`update_summary` 更新正文、覆盖到的 ID、version 和 token_count。
5. 失败保留旧摘要，不中断已完成聊天。

默认阈值 40、新消息间隔 20、保留最近 20 条；实际 settings 可覆盖。摘要代表一个“覆盖到某 ID 的检查点”，不表示可以把其后尚未摘要的消息随意丢弃。

## 任务 D：首轮后起标题

[session_title.py](D:/Project/learnLittle/app/rag/session_title.py) 负责“生成什么文字”，`query_service._update_title` 负责“能否更新数据库”。

新主链提交回答前先放短问句临时标题，然后后台在前几轮生成精炼标题。任务读出 previous_title 和 title_manual，模型完成后用条件 UPDATE 要求仍非手动且标题仍等于旧值。这能避免用户在等待模型时手动改名被覆盖。

标题失败使用 fallback_title，sanitize_title 去引号、空白并限长。前几轮只是更新资格，不代表 done 要等待模型标题。

## 任务 E：没有模型密钥时怎样回答

唯一问答入口是 `/chat/query`，由路由直接调用 `query_service.stream_query`。旧 `/chat/ask`、`/chat/stream` 已删除，访问返回 404。

没有模型密钥且没有 ReAct 替身时，图检查本地关键词；例如“现在几点”交给 `runner.run_agent`，再调用 `run_local_tool` 的时间工具。工具发出 `tool_start/tool_end/response`，外层仍保存最终回答并返回 done。真正的模型工具循环只在 `react_agent.py`，没有第二套手写 HTTP 循环。

没有匹配工具时，使用 `query_service.compose_answer` 根据检索是否发生、是否命中资料生成本地说明或摘录。`rag/llm.py` 仍提供分类、计划、摘要、标题、反思所需的非流式辅助补全；它不再承担旧聊天改写流。

**练习**：为什么 Redis 只留 20 条，但新链能利用第 30 条前的未摘要历史？因为选记忆的输入来自 SQL，不来自这个热窗口。
