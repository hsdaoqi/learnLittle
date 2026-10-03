# 后端结构与字段清单

[总教程](D:/Project/learnLittle/docs/backend-tutorial/README.md) | [逐函数入口](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

此清单覆盖零函数文件、类声明、配置与包导出。字段/常量代码块由 AST 提取，不导入应用，不读取真实 .env；源码默认值不能代表运行环境。自动生成的 dataclass/Pydantic/ORM 方法不是本项目手写定义，故不计函数数。

ORM 关系：User -> 分类/笔记/文档/会话/模板/回顾；分类 parent_id 自引用，笔记 category_id 可空；会话 -> 消息与唯一摘要；笔记 -> 唯一回顾记录。Trace 的归属标识用于查询，不应假设所有标识都声明了数据库 FK。

## alembic/env.py

Alembic 在线/离线入口与异步连接桥接；直接执行会采用配置数据库，文档工具不会导入它。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/alembic--env.md)；显式函数 4；类 0。

## alembic/versions/342a95208d0f_add_note_categories_and_notes_tables.py

数据库增量迁移：创建 note_categories 自引用分类表与 notes 表及关联索引。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/alembic--versions--342a95208d0f_add_note_categories_and_notes_tables.md)；显式函数 2；类 0。

## alembic/versions/53816adf617f_add_review_records.py

数据库增量迁移：创建 review_records，同时删除 notes 的全文索引，影响 HEAD 的关键词检索路径。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/alembic--versions--53816adf617f_add_review_records.md)；显式函数 2；类 0。

## alembic/versions/b7c1d4e8f901_add_knowledge_documents_table.py

数据库增量迁移：创建 knowledge_documents 元数据表、用户/MD5 索引。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/alembic--versions--b7c1d4e8f901_add_knowledge_documents_table.md)；显式函数 2；类 0。

## alembic/versions/c3e9f2a7b890_add_model_traces_and_pricing.py

数据库增量迁移：创建 model_traces 与 model_pricing，建立用户/会话时间聚合索引。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/alembic--versions--c3e9f2a7b890_add_model_traces_and_pricing.md)；显式函数 2；类 0。

## alembic/versions/c8d2e5f0a123_add_chat_sessions_and_messages.py

数据库增量迁移：创建 chat_sessions 与 chat_messages 及关联索引。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/alembic--versions--c8d2e5f0a123_add_chat_sessions_and_messages.md)；显式函数 2；类 0。

## alembic/versions/d9e3f6a1b234_add_chat_summaries_table.py

数据库增量迁移：创建每会话唯一的 chat_summaries 表，保存摘要覆盖点和版本。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/alembic--versions--d9e3f6a1b234_add_chat_summaries_table.md)；显式函数 2；类 0。

## alembic/versions/e0f4a7b2c345_add_note_templates_and_fulltext.py

数据库增量迁移：创建 note_templates，并为 notes 建 MySQL ngram 全文索引。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/alembic--versions--e0f4a7b2c345_add_note_templates_and_fulltext.md)；显式函数 2；类 0。

## alembic/versions/e2aebef3f9e7_add_user_email_verrifie.py

数据库增量迁移：为 users 增加非空 email_verified 字段；迁移未设服务端默认，已有数据部署需审查。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/alembic--versions--e2aebef3f9e7_add_user_email_verrifie.md)；显式函数 2；类 0。

## alembic/versions/e471331632c9_initial_users_table.py

数据库增量迁移：创建 users 和用户名索引，作为后续用户外键起点。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/alembic--versions--e471331632c9_initial_users_table.md)；显式函数 2；类 0。

## alembic/versions/f1a244c10001_chat_lifecycle.py

数据库增量迁移：增加 title_manual 并将已有非默认标题标手动，再加消息幂等字段和唯一索引；保留原正文。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/alembic--versions--f1a244c10001_chat_lifecycle.md)；显式函数 2；类 0。

## app/__init__.py

Python 包入口/命名空间文件；本快照没有显式函数，具体导入/赋值见结构声明。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--__init__.md)；显式函数 0；类 0。

## app/ai_service/__init__.py

Python 包入口/命名空间文件；本快照没有显式函数，具体导入/赋值见结构声明。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--__init__.md)；显式函数 0；类 0。

## app/ai_service/chat_graph.py

可取消 LangGraph 分类/执行图与有界输出队列。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--chat_graph.md)；显式函数 8；类 1。

类：`ChatState`。

## app/ai_service/langchain_tools.py

注册表描述到 StructuredTool 的轻量参数 Schema 适配。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--langchain_tools.md)；显式函数 4；类 0。

## app/ai_service/models.py

角色模型名选择，共享现有 key/base_url。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--models.md)；显式函数 1；类 0。

## app/ai_service/plan_execute.py

依赖计划、限量并行读/串行写、步骤 ReAct、综合与安全降级。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--plan_execute.md)；显式函数 18；类 2。

类：`PlanStep`、`ExecutionPlan`。

## app/ai_service/query_classifier.py

L1 规则、L2 补全和安全默认简单路线。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--query_classifier.md)；显式函数 11；类 1。

类：`ClassificationResult`。

## app/ai_service/react_agent.py

真实 LangChain 工具循环、事件协议、工具重试护栏和答案反思。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--react_agent.md)；显式函数 11；类 0。

## app/ai_service/reflection.py

L1 批判/修订实时状态与 L2 修复提示，失败不阻断已有草稿。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--reflection.md)；显式函数 10；类 1。

类：`ReflectionVerdict`。

## app/ai_service/review_tools.py

回顾 service 到 Agent 文本工具的薄适配。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--review_tools.md)；显式函数 2；类 0。

## app/ai_service/runner.py

无模型关键词工具与测试注入；真实模型工具循环只在 ReAct 主链。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--runner.md)；显式函数 6；类 0。

## app/ai_service/sse_slot.py

主聊天按用户并发计数，Redis 故障退进程内。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--sse_slot.md)；显式函数 2；类 0。

## app/ai_service/thinking.py

协议兼容、附件互斥、角色独立 thinking 和超时放宽。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--thinking.md)；显式函数 7；类 1。

类：`ThinkingDecision`。

## app/ai_service/tool_registry.py

内存 ToolSpec/分组/实现绑定/只读能力描述。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--tool_registry.md)；显式函数 8；类 2。

类：`ToolSpec`、`ToolRegistry`。

## app/ai_service/tools.py

绑定认证用户的内置笔记/回顾工具，写工具自管事务。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--tools.md)；显式函数 16；类 0。

## app/ai_service/usage_callback.py

每次 LangChain 模型调用的输入/输出/usage/失败计量。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--ai_service--usage_callback.md)；显式函数 4；类 1。

类：`ModelUsageCallback`。

## app/config.py

配置类型、默认值与生产密钥约束；实际环境可覆盖默认。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--config.md)；显式函数 2；类 1。

类：`Settings`。

## app/core/__init__.py

Python 包入口/命名空间文件；本快照没有显式函数，具体导入/赋值见结构声明。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--core--__init__.md)；显式函数 0；类 0。

## app/core/after_commit.py

Session 事件监听，成功提交派发、回滚丢弃派生工作。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--core--after_commit.md)；显式函数 3；类 0。

## app/core/exception_handlers.py

把业务、校验与未预期异常转换为 HTTP 失败信封。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--core--exception_handlers.md)；显式函数 4；类 0。

## app/core/failed_response.py

错误码、BusinessError 载体与失败响应字典。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--core--failed_response.md)；显式函数 2；类 2。

类：`ErrorCode`、`BusinessError`。

## app/core/rate_limit.py

Redis 固定窗口，全局与具体 path 桶、特殊动作额度。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--core--rate_limit.md)；显式函数 6；类 1。

类：`RateLimitMiddleware`。

## app/core/scheduler.py

每天过期笔记/分类清理的调度和事务包装。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--core--scheduler.md)；显式函数 5；类 0。

## app/core/success_response.py

普通成功响应字典；不承担事务提交。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--core--success_response.md)；显式函数 1；类 0。

## app/core/task_runner.py

进程内后台任务跟踪、同 key 串行与有界关机回收。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--core--task_runner.md)；显式函数 4；类 0。

## app/db/__init__.py

Python 包入口/命名空间文件；本快照没有显式函数，具体导入/赋值见结构声明。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--db--__init__.md)；显式函数 0；类 0。

## app/db/database.py

SQL URL、engine、session 与普通请求事务所有权。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--db--database.md)；显式函数 5；类 0。

## app/db/redis_client.py

Redis 单例资源与注入/探针；并非所有使用者都采用相同容错策略。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--db--redis_client.md)；显式函数 6；类 0。

## app/models/__init__.py

导入并重新导出所有 ORM 类型，让 Base.metadata 收齐表；不是空包标记。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--models--__init__.md)；显式函数 0；类 0。

## app/models/base.py

全体 ORM 的声明式 Base，向 Alembic 暴露 metadata。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--models--base.md)；显式函数 0；类 1。

类：`Base`。

## app/models/category.py

note_categories 自引用树，软删除与同级名称规则由 service 维护。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--models--category.md)；显式函数 2；类 1。

类：`NoteCategory`。

## app/models/chat.py

会话、消息、里程碑摘要三表；手动标题和用户角色哈希幂等键保护生命周期。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--models--chat.md)；显式函数 4；类 3。

类：`ChatSession`、`ChatMessage`、`ChatSummary`。

## app/models/knowledge.py

knowledge_documents 文件路径、MD5、类型和切片数；旧头注释的 chunk_count=0 已过时。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--models--knowledge.md)；显式函数 1；类 1。

类：`KnowledgeDocument`。

## app/models/note.py

notes 表，正文/格式/标签/分类/置顶和删除时间；向量存在 Chroma 而非这一行。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--models--note.md)；显式函数 2；类 1。

类：`Note`。

## app/models/note_template.py

note_templates 保存用户自定义 JSON 骨架和文字 category。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--models--note_template.md)；显式函数 1；类 1。

类：`NoteTemplate`。

## app/models/review.py

review_records 每笔记唯一，保留当前进度/下次时间和最近完成时间。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--models--review.md)；显式函数 1；类 1。

类：`ReviewRecord`。

## app/models/usage.py

model_traces 与 model_pricing 数据结构，不是独立工具审计表。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--models--usage.md)；显式函数 0；类 2。

类：`ModelTrace`、`ModelPricing`。

## app/models/user.py

users 表的凭据、资料与状态；uuid 是其他业务表的归属外键。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--models--user.md)；显式函数 2；类 1。

类：`User`。

## app/rag/__init__.py

Python 包入口/命名空间文件；本快照没有显式函数，具体导入/赋值见结构声明。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--__init__.md)；显式函数 0；类 0。

## app/rag/chat_cache.py

会话列表短 TTL、近期消息 List；不是新 Agent 的唯一记忆。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--chat_cache.md)；显式函数 12；类 0。

## app/rag/chat_history.py

SQL 未摘要历史的实际 Token 预算选择，保持消息角色。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--chat_history.md)；显式函数 3；类 0。

## app/rag/document_parser.py

bytes->纯文本；PDF 文字提取，不含 OCR。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--document_parser.md)；显式函数 2；类 0。

## app/rag/embeddings.py

注入/API/无 key 哈希向量、批处理与进程 TTL/LRU 缓存。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--embeddings.md)；显式函数 13；类 0。

## app/rag/hyde.py

生成假设查询并 Redis 缓存，主聊天默认由外层关闭。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--hyde.md)；显式函数 7；类 0。

## app/rag/llm.py

httpx 非流式辅助补全，复用于分类、计划、摘要、标题和反思；不是工具执行器。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--llm.md)；显式函数 1；类 0。

## app/rag/memory.py

按消息检查点增量压缩旧历史，保留近期原文。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--memory.md)；显式函数 9；类 0。

## app/rag/note_cards.py

带真实 note_id 的搜索文本和用户引用块解析。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--note_cards.md)；显式函数 4；类 0。

## app/rag/rag_route.py

根据当前用户双源 Top-1 距离决定是否检索。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--rag_route.md)；显式函数 3；类 1。

类：`RouteDecision`。

## app/rag/rag_summarize.py

命中副本压缩/截断，原命中留作来源展示。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--rag_summarize.md)；显式函数 8；类 0。

## app/rag/retriever.py

分词、BM25、RRF、CrossEncoder 适配和词重叠兜底。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--retriever.md)；显式函数 19；类 0。

## app/rag/session_title.py

标题文本生成/清洗/失败兜底，写库竞争保护在 query_service。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--session_title.md)；显式函数 6；类 0。

## app/rag/text_splitter.py

标题/段落/字符滑窗切片与 TextChunk 结构。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--text_splitter.md)；显式函数 6；类 2。

类：`TextChunk`、`TextSplitter`。

## app/rag/token_budget.py

tokenizer/字符估算与单条消息开销计数；配额在 chat_history 计算。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--token_budget.md)；显式函数 4；类 1。

类：`TokenCounter`。

## app/rag/vector_store.py

Chroma 双 collection 的嵌入写入、双源检索、用户过滤与删除。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--rag--vector_store.md)；显式函数 22；类 1。

类：`VectorStoreService`。

## app/routers/__init__.py

Python 包入口/命名空间文件；本快照没有显式函数，具体导入/赋值见结构声明。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--routers--__init__.md)；显式函数 0；类 0。

## app/routers/category_router.py

分类树、移动、回收站、排序和批量合并 HTTP 入口。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--routers--category_router.md)；显式函数 10；类 0。

## app/routers/chat_router.py

唯一 query 聊天入口和会话管理；直接调用 query_service，没有旧问答兼容链。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--routers--chat_router.md)；显式函数 5；类 0。

## app/routers/health.py

进程健康与 SQL/Redis 就绪探针。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--routers--health.md)；显式函数 2；类 0。

## app/routers/knowledge_router.py

知识文档上传 SSE、元数据列表/详情/删除与直接检索。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--routers--knowledge_router.md)；显式函数 6；类 0。

## app/routers/note_router.py

笔记 CRUD、批量、搜索及写作/邮件入口；静态路径在动态 note_id 路由前注册。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--routers--note_router.md)；显式函数 15；类 0。

## app/routers/note_template_router.py

模板 HTTP CRUD 和套用创建入口。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--routers--note_template_router.md)；显式函数 7；类 0。

## app/routers/review_router.py

今日回顾、完成和统计 HTTP 入口。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--routers--review_router.md)；显式函数 3；类 0。

## app/routers/usage_router.py

当前用户用量聚合 HTTP 入口。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--routers--usage_router.md)；显式函数 1；类 0。

## app/routers/user.py

账号认证与资料 HTTP 适配，默认注册要求邮箱验证。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--routers--user.md)；显式函数 13；类 0。

## app/schemas/__init__.py

Python 包入口/命名空间文件；本快照没有显式函数，具体导入/赋值见结构声明。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--schemas--__init__.md)；显式函数 0；类 0。

## app/schemas/auth.py

注册/登录/刷新/资料/邮件请求和公开响应的数据契约。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--schemas--auth.md)；显式函数 6；类 12。

类：`UserRegister`、`SendCodeRequest`、`EmailChangeRequest`、`NoteExportEmailRequest`、`UserLogin`、`TokenResponse`、`RefreshTokenRequest`、`LogoutRequest`、`UserUpdate`、`PasswordChange`、`SessionInfo`、`UserInfo`。

## app/schemas/category.py

分类创建/改名/移动/排序/批量参数；Schema 不能代替数据库所有权检查。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--schemas--category.md)；显式函数 1；类 6。

类：`CategoryCreate`、`CategoryUpdate`、`CategoryMoveRequest`、`CategoryReorderRequest`、`CategoryBatchRequest`、`DeletedCategoryResponse`。

## app/schemas/chat.py

QueryRequest 与公开会话/消息响应；附件 ID 当前只用于 thinking 互斥。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--schemas--chat.md)；显式函数 0；类 4。

类：`QueryRequest`、`ChatSessionResponse`、`ChatMessageResponse`、`ChatSessionTitleUpdate`。

## app/schemas/knowledge.py

文档响应不暴露本地路径，搜索 hit 限定公开字段。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--schemas--knowledge.md)；显式函数 0；类 4。

类：`KnowledgeDocumentResponse`、`KnowledgeDocumentListResponse`、`KnowledgeSearchHit`、`KnowledgeSearchResponse`。

## app/schemas/note.py

笔记创建/部分更新/搜索/批量/写作建议的字段限制和响应形状。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--schemas--note.md)；显式函数 1；类 11。

类：`NoteCreate`、`NoteUpdate`、`NoteResponse`、`NoteSummary`、`NoteMoveRequest`、`NoteBatchRequest`、`NoteSearchRequest`、`NoteSearchHit`、`AutocompleteRequest`、`WriteAssistantRequest`、`AutoTagRequest`。

## app/schemas/review.py

待复习项目、完成响应、统计与 0..5 的质量字段。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--schemas--review.md)；显式函数 0；类 4。

类：`ReviewItem`、`ReviewCompleteResponse`、`ReviewStats`、`ReviewCompleteQuery`。

## app/schemas/template.py

模板创建、部分更新、应用和响应契约。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--schemas--template.md)；显式函数 0；类 4。

类：`NoteTemplateCreate`、`NoteTemplateUpdate`、`NoteTemplateApply`、`NoteTemplateResponse`。

## app/services/__init__.py

Python 包入口/命名空间文件；本快照没有显式函数，具体导入/赋值见结构声明。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--services--__init__.md)；显式函数 0；类 0。

## app/services/category_service.py

最多三层树与软删/恢复/合并规则；树算法一次加载再计算。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--services--category_service.md)；显式函数 29；类 0。

## app/services/chat_service.py

会话 CRUD 与消息数据操作；不包含独立问答实现或 query 转发。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--services--chat_service.md)；显式函数 12；类 0。

## app/services/email_service.py

SMTP MIME 发送、验证码 Redis 状态与附件构造；发信不是 SQL 事务。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--services--email_service.md)；显式函数 12；类 0。

## app/services/knowledge_service.py

文件、SQL 文档记录和 Chroma 切片的上传编排；不具备分布式事务。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--services--knowledge_service.md)；显式函数 10；类 0。

## app/services/note_ai_service.py

补全/写作/标签建议，输出建议而不自动保存笔记。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--services--note_ai_service.md)；显式函数 11；类 0。

## app/services/note_service.py

笔记业务权限、SQL 生命周期、关键词检索和提交后向量同步。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--services--note_service.md)；显式函数 22；类 0。

## app/services/note_template_service.py

模板 CRUD 与应用为普通笔记，复用笔记生命周期。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--services--note_template_service.md)；显式函数 8；类 0。

## app/services/query_service.py

用户先提交、并行上下文、图执行、助手提交和后台维护的主编排。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--services--query_service.md)；显式函数 10；类 0。

## app/services/review_service.py

固定间隔回顾状态与 Agent 文本适配；没有完整复习事件日志。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--services--review_service.md)；显式函数 9；类 0。

## app/services/usage_service.py

ContextVar 归属、独立 trace 事务、用量和本地价格聚合。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--services--usage_service.md)；显式函数 14；类 1。

类：`UsageTimer`。

## app/utils/__init__.py

Python 包入口/命名空间文件；本快照没有显式函数，具体导入/赋值见结构声明。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--utils--__init__.md)；显式函数 0；类 0。

## app/utils/auth_utils.py

密码、JWT、Redis 安全状态、短期聊天票和设备会话；顶部旧注释不代表设备功能缺失。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--utils--auth_utils.md)；显式函数 38；类 0。

## app/utils/file_handler.py

文档/头像的大小和格式约束、安全文件名与受限读取，兼用于上传章节。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/app--utils--file_handler.md)；显式函数 8；类 0。

## main.py

应用装配与生命周期；路由/资源从这里接上，不包含全部业务逻辑。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/main.md)；显式函数 2；类 0。

## tests/conftest.py

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/tests--conftest.md)；显式函数 4；类 0。

## tests/test_agent_alignment.py

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/tests--test_agent_alignment.md)；显式函数 42；类 3。

类：`ToolCallingModel`、`FakeAgent`、`FakeAgent`。

## tests/test_chat_routes.py

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/tests--test_chat_routes.md)；显式函数 12；类 0。

## tests/test_notes_categories.py

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/tests--test_notes_categories.md)；显式函数 25；类 0。

## tests/test_persistence_alignment.py

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/tests--test_persistence_alignment.md)；显式函数 7；类 0。

## tests/test_query_lifecycle.py

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/tests--test_query_lifecycle.md)；显式函数 28；类 0。

## tests/test_retriever_predict.py

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/tests--test_retriever_predict.md)；显式函数 3；类 1。

类：`_FakeSentenceTransformerCrossEncoder`。

## tests/test_thinking.py

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/tests--test_thinking.md)；显式函数 16；类 0。

## tests/test_usage.py

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

[完整声明与函数说明](D:/Project/learnLittle/docs/backend-tutorial/atlas/tests--test_usage.md)；显式函数 8；类 0。

