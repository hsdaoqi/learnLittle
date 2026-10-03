# 01 从“收到一个请求”理解整个后端

任务：假设 API 进程已经由你启动，用户请求自己的笔记列表。先不要关心列表 SQL，先回答“代码为什么会到那里”。

## 1. 目录就是职责边界

```text
main.py                 组装 FastAPI、路由和资源生命周期
app/config.py           配置类型、默认值与生产密钥检查
app/routers/            HTTP 入出口
app/schemas/            请求字段约束和响应数据形状
app/services/           业务流程；query_service 是新聊天主流程
app/models/             ORM 表及关联
app/db/                 SQL engine/session 与 Redis 实例
app/core/               响应、异常、限流、提交后任务、定时任务
app/utils/              密码/Token/设备、文件安全处理
app/rag/                文档、向量、检索、模型客户端、聊天记忆
app/ai_service/         分类图、ReAct、计划、反思、工具
alembic/                数据库版本演进
tests/                  隔离的业务与回归测试
templates/              邮箱验证码 HTML 等模板
data/                   本地上传文件、头像、Chroma 等运行数据
```

阅读入口：[main.py](D:/Project/learnLittle/main.py)、[字段与类清单](D:/Project/learnLittle/docs/backend-tutorial/structure.md)、[本章函数详解入口](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)。

## 2. 创建应用不等于启动所有资源

模块末尾 `app = create_app()` 会创建 FastAPI 实例。`create_app` 选择传入配置或 `get_settings()`，检查生产密钥，注册错误处理、中间件、业务路由、健康探针和头像静态目录。它也会创建头像目录，所以“import 应用绝对没有文件副作用”并不成立。

真正进入 ASGI lifespan 后，内层 `lifespan` 才建立数据库 engine/session factory、初始化 Redis 和向量服务、给用量记录器设置 session factory、播种定价。如果测试已放入自己的 session factory，不再新建生产数据库 engine。

向量服务初始化还不等于下载嵌入模型或读取所有文档：Chroma collection 在 `_ensure` 中按需准备。定时清理仅在 `api_reload=False` 且非 test 环境启动。关闭时先等待受管理后台任务，再关闭用量、调度器、向量服务、Redis 和自己拥有的 engine。

## 3. 一次普通请求的路径

```text
HTTP /api/v1/note/...
  -> RateLimitMiddleware.dispatch
  -> FastAPI 匹配路由、解析 Schema、解析 Depends
  -> get_current_user_id -> get_current_token_payload
  -> get_db_session 暂借一个 AsyncSession
  -> 路由 -> note_service -> ORM/SQL
  -> Schema.model_validate / success_response
  -> get_db_session 恢复运行：commit；异常则 rollback
```

Schema 只说明数据形状，不证明这条笔记属于你；所有权必须再由 service 的 `user_id` 条件保证。不要把请求体中的 `user_id` 作为可信身份。

`get_db_session` 的 `yield session` 表示把 session 暂时交给路由。控制权回来后才提交。普通 service 因而经常只有 `add/flush/refresh`。`expire_on_commit=False` 便于提交后读已有属性，但服务端生成或被 UPDATE 失效的字段仍可能需要显式 `refresh`。

流式聊天、上传和 Agent 工具会自己创建 session、显式 commit，不能套用普通路由的事务顺序。

## 4. 四类存储不要混在一起

| 存储 | 存什么 | 是不是可重建的派生数据 |
| --- | --- | --- |
| SQL | 用户、笔记、分类、文档记录、会话消息、摘要、模板、回顾、用量、定价 | 主要业务事实；不能随意清空 |
| Redis | 登录失败、Token 状态、设备、限流、聊天热缓存、HyDE 缓存 | 有些可重建；认证状态丢失会改变登录行为 |
| Chroma | 知识文档和笔记切片及向量 | 可从保留的原始资料重建，但不是 SQL 事务的一部分 |
| 本地磁盘 | 上传原文件、头像、Chroma 数据目录 | 部分是原始资料；不要把 `data` 当临时目录删除 |

## 5. 返回失败也是一条流程

业务失败抛 `BusinessError`，异常处理器转为统一 JSON；请求校验失败走 validation handler；未处理异常由 general handler 记录并返回服务端错误。`failed_response` 和 `success_response` 负责响应信封，不负责 rollback。

普通业务成功常用 `code=0`；`/health` 使用自己的 `code=200`，不要用一个未经区分的判断覆盖所有接口。响应 `request_id` 和模型 trace 的 request_id 并非天然贯通。

`/health` 只说明 API 进程能回答；`/ready` 检查 MySQL、Redis，失败为 HTTP 503，不替你验证 SMTP、LLM、重排模型或 Chroma。

## 6. 配置与非 Python 文件

`Settings` 从环境与 `.env` 加载；`get_settings` 有进程缓存。教程不读取或复制真实 `.env`。配置默认值不等于你机器上的生效值。创建应用时传入 settings 也不代表所有模块都不用全局 `get_settings`，测试需同步隔离它。

`requirements.txt` 是运行依赖，`requirement-dev.txt` 是测试依赖；`pyproject.toml` 当前不能被当作一份完整构建说明。`docker-compose.yml` 只声明 MySQL/Redis，不包含整个应用；其中 Redis 默认映射 16379，而代码默认连接 6379，实际使用时必须一致。`alembic.ini` 提供迁移框架配置，连接参数由迁移环境根据 Settings 组装。`templates` 提供邮件内容，`data` 是运行状态而非 Python 代码。

**练习**：为什么列表查询 service 没有 commit 仍能工作？为什么启动时能创建 app，却可能在 Redis 初始化失败？为什么 `/ready` 成功但 AI 回答仍可能失败？

答案：普通请求由依赖管理事务；构造与 lifespan 是不同阶段；探针没有检查全部外部依赖。
