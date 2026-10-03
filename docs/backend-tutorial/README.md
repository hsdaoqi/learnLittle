# learnLittle 后端：从任务流程读懂全部代码

本教程以 **2026-10-02 本地 `D:\Project\learnLittle` 源码快照**为准，只解释已经存在的后端。不是原项目教程，也不是未来阶段的设计稿。README 中的旧阶段记录、模块头部的旧注释与当前函数冲突时，以当前函数实现为准。

## 怎样读

第一遍按下面的任务顺序阅读，先理解数据怎么走；第二遍在每章对应的函数详解中看参数、分支、调用和边界。不要一开始就从 `auth_utils.py` 第一行背到最后一行。

| 顺序 | 你要弄明白的问题 |
| --- | --- |
| [01 启动与结构](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md) | 谁创建应用？一次请求由谁提交事务？各目录和存储分别负责什么？ |
| [02 账号任务](D:/Project/learnLittle/docs/backend-tutorial/02-account.md) | 验证码、注册、登录、刷新、设备撤销怎样串起来？ |
| [03 笔记任务](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md) | 笔记与分类怎么保存、搜索、删除、恢复？向量为什么晚一点才更新？ |
| [04 学习辅助](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md) | 模板、写作建议、复习和邮件导出怎样复用笔记能力？ |
| [05 文档与检索](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | 文件怎样变成可检索切片？召回、重排、摘要各自改变什么？ |
| [06 一轮对话](D:/Project/learnLittle/docs/backend-tutorial/06-query.md) | 新主链怎样持久化、组装记忆、选择 Agent，并处理重复请求和断流？ |
| [07 Agent 执行](D:/Project/learnLittle/docs/backend-tutorial/07-agent.md) | 工具、ReAct、Plan、反思、深度思考怎样配合？ |
| [08 记忆与降级](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md) | Redis、SQL、摘要、标题有什么区别？没有模型时怎样回答？ |
| [09 运维与用量](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md) | 限流、后台任务、Token 记录、费用和清理如何工作？ |
| [10 迁移与测试](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | 数据结构怎样演进？如何通过隔离测试验证上面的理解？ |
| [11 当前边界](D:/Project/learnLittle/docs/backend-tutorial/11-boundaries.md) | 哪些是已实现但有限制，哪些确实还没实现？ |
| [12 登录逐行讲解](D:/Project/learnLittle/docs/backend-tutorial/12-login-walkthrough.md) | 按 2026-10-02 代码，从点击登录到密码验证、双 Token、Redis 和设备会话逐步解释，含设计目的与实际边界 |

## 每一个函数在哪里

- [逐文件、逐函数详解总目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)：每处函数定义都有独立解释、签名、源码入口和任务章节。嵌套函数、类方法、测试替身和 lambda 都单独计入。
- [结构清单](D:/Project/learnLittle/docs/backend-tutorial/structure.md)：没有函数的 ORM / Schema / 包文件也列出；字段声明帮助你理解数据结构，而不是把“没有函数”当成“没有内容”。
- [覆盖报告](D:/Project/learnLittle/docs/backend-tutorial/coverage.md)：源码快照、函数数量、解释覆盖及检查方式。
- [机器可读清单](D:/Project/learnLittle/docs/backend-tutorial/inventory.json)：AST 提取结果，包含函数源码和文件哈希。

**覆盖口径**：`main.py`、`app/**/*.py`、`tests/**/*.py`、`alembic/env.py`、`alembic/versions/*.py`。不包含前端、第三方依赖、Python 自动生成的方法、尚未实例化的 Alembic 模板和本教程自己的工具。733 处定义不等于 733 个测试用例。函数索引不只统计对外 API，私有辅助函数也算。

详解中的“直接调用表达式”“return / yield / assert”来自 AST，辅助你对照源码；它们不是完整运行时调用图，也不证明一个分支一定执行。人工解释说明职责，源码负责精确行为，测试证明它实际覆盖的场景，三者不能互相代替。

## 阅读时一直问的六个问题

1. 入口是什么：HTTP 路由、后台任务、工具调用，还是测试？
2. 当前用户从哪里来：已校验 Token，还是模型输入？本项目工具闭包绑定前者。
3. 输入数据是什么：Schema、ORM 实体、普通字典、字符串，还是异步事件流？
4. 哪一步改变状态：SQL、Redis、Chroma、磁盘或外部邮件？
5. 谁负责提交：依赖、SSE 自建事务，还是工具自身？
6. 失败后还剩什么：用户消息是否已保存？工具是否可能已经写入？能否安全重试？

## 最小词汇表

| 术语 | 在本项目里的意思 |
| --- | --- |
| Router | HTTP 与 Python 服务之间的适配层，解析参数、注入用户和会话、包装响应 |
| Schema | 请求/响应的数据形状与校验规则，不是数据库表 |
| Model | SQLAlchemy ORM 表映射，负责持久化结构，不负责完整业务流程 |
| Service | 所有权校验、业务顺序、状态变更；普通请求通常由外层提交 |
| `flush` | 把待变更 SQL 发给数据库，可获得 ID；不代表事务已经提交 |
| `refresh` | 从数据库重新读取实体字段，拿到服务端默认值等 |
| `commit` | 提交当前 SQL 事务；不自动提交 Redis、Chroma 或文件操作 |
| `await` | 等待异步操作；不是自动开线程，更不是自动事务 |
| `yield` | 本项目可能是依赖暂借资源，也可能是逐条发送 SSE 事件，须看调用处 |
| 闭包 | 内层函数保留外层的 `user_id` / session factory，让工具不必让模型传用户 ID |
| 注入点 | `set_*_fn` 等替换函数的入口，测试用假模型获得确定结果 |
| RAG | 找相关资料放进提示；不是给模型做训练 |
| ReAct | 模型决定是否调用工具，读取结果后继续生成的循环 |
| Plan | 先产生带依赖的步骤，再执行步骤 Agent，最后综合 |

本次编写只做静态读取与文档检查，没有启动应用、连接业务数据库、执行迁移、发送邮件或调用模型。
