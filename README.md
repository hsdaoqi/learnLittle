# RAG LearnLittleCode Rebuild

从零、分阶段复现
[`RAG_LearnLittleCode`](https://github.com/qiaojoin586-droid/RAG_LearnLittleCode)
的学习项目。

原项目使用 MIT License。这里不直接复制实现，而是参照其功能和模块边界逐步重建。

## 当前阶段：31 笔记 AI 辅助

已经完成：

**基础设施与认证（01-05 阶段）**

- FastAPI 应用工厂、`/health` `/ready`（MySQL+Redis）探针、统一响应/异常体系
- 异步 SQLAlchemy + Alembic；Docker Compose 起 MySQL(13306) + Redis(16379)
- 注册 / 登录 / 刷新 / 登出 / 当前用户；bcrypt + PyJWT
- 登录失败锁定、Refresh 白名单与轮换、Access 黑名单（Redis 三件套）

**分类与笔记（06 阶段后端）**

- NoteCategory 模型：3 级树（parent_id 自引用）、软删除、同级同名校验、排序权重
- Note 模型：标题/Markdown 正文/JSON 标签/置顶/软删除/分类外键（SET NULL）
- 注册时自动播种默认分类树（工作/学习/技术/生活/闪念/阅读/三体/其他）
- 分类接口：树（含笔记计数）、创建、重命名、移动（环检测 + 深度校验）、软删除（活跃子分类自动提升，笔记转未分类）
- 笔记接口：创建、列表（分类/未分类/关键词/分页，置顶优先）、详情、部分更新、
  回收站（软删除 / 列表 / 恢复 / 彻底删除）
- 新增错误码：40401 笔记不存在、40407 分类不存在、40904 同级同名冲突
- 32 个测试全部通过；真实 MySQL 冒烟全链路验证
- 修复两个异步 SQLAlchemy 陷阱：flush 后读取服务端默认值列（created_at/updated_at）
  必须显式 `await db.refresh()`，否则 Pydantic 同步读属性触发 MissingGreenlet

**前端（08 阶段）**

- 分类树侧栏：模板树展示、选中过滤、新建/重命名/删除（子分类提升规则与后端一致）
- 笔记列表：按分类/未分类/关键词过滤、置顶、移入回收站、新建后进入编辑器
- 笔记编辑器：标题 + Markdown 文本框 + 分类下拉 + 保存
- 回收站页：恢复 / 彻底删除
- 资料页挪到 `/profile`；首页改为笔记列表

**前端（09 阶段）**

- 编辑器左右分栏：Markdown 源码 + 实时预览（GFM 表格/列表，代码高亮）
- 预览按需加载（react-markdown 拆成独立 chunk，不拖垮列表页体积）
- 标签编辑：回车/逗号添加，Backspace 删最后一个
- Ctrl/Cmd+S 保存，工具栏显示最近保存时间

**知识库文档管理（10 阶段）**

- KnowledgeDocument 模型 + Alembic 迁移：文件名/路径/大小/类型/MD5/切片数（本阶段恒为 0）
- 上传接口同步 JSON（不做 SSE、不解析、不写向量）：PDF / MD / TXT，默认 50MB，按用户+MD5 去重
- 列表 / 详情 / 删除（删元数据并尝试删本地文件）；跨用户一律 404
- 新增错误码：40004 文件过大、40005 类型不支持、40404 文档不存在、40905 重复上传
- 前端知识库页：拖拽/点击上传、列表、删除；导航增加「知识库」
- 本阶段明确不接 Chroma / TextSplitter，作为 RAG 前置

**解析 / 切片 / 向量检索（11 阶段）**

- 上传后解析 TXT/MD/PDF，按标题/段落切片，写入本地 Chroma（`data/chroma`）
- Embedding 用确定性哈希向量（不调云模型），方便测试与离线运行
- `GET /knowledge/search`：按 user_id 隔离检索切片
- 删除文档时同步删向量；向量写入失败回滚落盘文件
- 不接 HyDE / 重排序 / LLM 问答，那些放到下一阶段

**知识库问答（12 阶段）**

- chat_sessions / chat_messages：会话列表、改标题、删除、消息历史
- `POST /chat/ask`：检索知识库切片并拼成带出处的回答（不调 LLM、不 SSE）
- 无命中时明确提示先上传文档；跨用户会话 404
- 前端「问答」页：会话侧栏 + 同步发送

**笔记向量双写（13 阶段）**

- 笔记创建/更新/恢复写入 `notes_collection`；软删除与彻底删除同步删向量
- `POST /chat/ask` 混合检索知识库 + 笔记，回答里标注来源
- 向量失败不阻断笔记保存（只打日志）；无新的 MySQL 迁移

**LLM 流式改写（14 阶段）**

- `POST /chat/stream`：SSE 事件 `meta` / `token` / `done`
- 可注入假 LLM 测流式；配 `LLM_API_KEY` 走 OpenAI 兼容接口；未配置则把本地拼接答案分片推送
- 模型失败自动降级拼接；同步 `POST /chat/ask` 仍保留

**真实 Embedding API（15 阶段）**

- 写入/检索向量改为异步：注入函数 > Embedding API > 哈希回退
- OpenAI 兼容 `/embeddings`；`EMBEDDING_API_KEY` 为空则复用 `LLM_API_KEY`
- 文本 MD5 + 后端标签的 LRU 缓存（TTL / 条数上限 / 按批 20 条）
- 集合非空时校验已存维度与当前模型输出，不一致则 50004
- 换 Embedding 模型后需删除 `data/chroma` 再重新上传文档、保存笔记

**混合检索（16 阶段）**

- 检索改为向量召回 + BM25 词法召回，再用 RRF 融合名次
- 知识库搜索、问答 `search_both` 都走同一套管线；两边 collection 先各自融合，再跨源 RRF
- 重排序默认识别查询词重叠，测试可 `set_rerank_fn` 注入；失败则保持融合顺序
- 本阶段不下载 CrossEncoder，测试不打外网

**HyDE（17 阶段）**

- 问答检索前用 LLM 生成假设性回答，用它做向量 + BM25 召回；重排序仍用用户原问题
- Redis 缓存键含模型名和 user_id；失败、关闭或未配密钥时回退原问题
- 知识库页关键词搜索不走 HyDE；测试可 `set_hyde_fn` 注入

**RAG 路由（18 阶段）**

- 问答在 HyDE / 混合检索之前，用当前用户知识库+笔记的 Top-1 余弦距离判断要不要检索
- 距离大于 `RAG_ROUTE_THRESHOLD`（默认 0.5）则跳过检索，不调 HyDE；关闭开关或打分失败则放行
- 跳过与「检索过但没命中」用不同文案；响应带 `used_retrieval` / `route_distance`
- 知识库页关键词搜索不走这层门控；测试可 `set_route_fn` 注入

**多轮问答上下文（19 阶段）**

- 同一会话把最近 N 轮对话带进路由打分、HyDE、混合检索和 LLM 改写
- 短追问（「那是什么」）能对上上一轮实体；单条过长会截断
- `CHAT_HISTORY_ROUNDS=0` 则每轮仍孤立；本阶段不做 token 预算和摘要压缩

**Token 预算与滑动窗口（20 阶段）**

- 先按轮数取窗口，再按 Token 配额从新到旧截断；最新一条即使超配额也保留
- 配额 = 模型窗口 - 系统提示/当前输入/安全余量 - 检索占用（尚未检索时按上限预留，检索后按实际）
- 计数用 tiktoken `cl100k_base`（与原项目相同）；加载失败回退 `len(text)//2`
- 摘要压缩、Agent 预留本阶段为 0
- 原项目 `allocate()` 把 RAG 上限算进固定项后又减一次实际 RAG，这里只减一次

**记忆压缩（21 阶段）**

- 消息超过阈值后，把窗口外旧对话和已有摘要融合，写入 `chat_summaries`
- 检索和 LLM 改写提示带上 `[历史对话摘要]`；失败保留旧摘要，不打断问答
- 触发条件对齐原项目：`threshold=40`、`min_interval=20`、`keep_recent=20`
- 间隔按「上次摘要之后的消息条数」判断，不把自增 ID 当条数减

**检索后摘要（22 阶段）**

- 问答命中后、生成答案前：命中切片用 LLM 压成短参考，再进拼接 / 流式改写和 Token 预算
- 关闭开关、未配密钥或单条失败则截断拼接，不打断问答
- API `sources` 仍返回原始命中；知识库页关键词搜索不走这层
- 测试可 `set_summarize_fn` 注入

**CrossEncoder 重排序（23 阶段）**

- 混合检索 RRF 之后：注入函数 > bge-reranker CrossEncoder > 查询词重叠
- 默认 `RERANK_DOWNLOAD=false`，测试环境不加载模型；加载失败或未安装 `sentence-transformers` 则回退词重叠
- 本机已有缓存时可直接用；首次拉模型把 `RERANK_DOWNLOAD` 设为 true
- 测试可 `set_rerank_fn` / `set_cross_encoder` 注入，不打外网

**知识库上传 SSE（24 阶段）**

- `POST /knowledge/upload` 改为 SSE：`processing`（saving / parsing / splitting / vectorizing）→ `completed` → `finish`
- 类型不支持、文件过大、同用户 MD5 重复仍在开流前返回 HTTP JSON（400 / 409）
- 处理失败推 `error`，向量写入失败回滚 DB 并删已落盘文件；独立 session，避免流式响应关掉请求级 Depends
- 前端知识库页按阶段显示进度条；`sources` / 检索行为不变

**Redis 热缓存（25 阶段）**

- 会话列表 `chat:sessions:{user_id}`，JSON，TTL 300s；创建 / 改标题 / 删除 / 问答后失效
- 最近消息 `chat:msgs:{session_id}`，List，LPUSH 最新在前，LTRIM 保留 20 条（覆盖默认 6 轮窗口）
- 写入：MySQL 先成功再写 Redis；读取：Redis miss 回填 MySQL。Redis 失败不影响问答
- 前端消息历史仍走 MySQL 全量，避免只拿到热窗口；问答读历史可走热缓存

**前端壳升级（26 阶段）**

- 主布局改为顶栏 + 56px 图标栏 + 分类树 + 内容区；问答从 `/chat` 页改为 480px 右侧浮层（首次打开才挂载）
- 旧 `/chat` 路由跳回笔记页并打开浮层；Escape / 再点问答按钮关闭
- 浅色 / 深色用 `data-theme` CSS 变量；中英词表自管，不引入 i18next / lucide
- 顶栏搜索入口先占位，全局搜索下一阶段再接

**分类进阶（27 阶段）**

- 分类回收站：列表带剩余天数；恢复会级联拉回已删除祖先（以及该节点下已删除子孙），避免树断链
- 软删除仍提升活跃子分类、笔记转未分类；彻底删除前再把残留活跃子分类提升为顶级
- `POST /category/reorder` 必须提交同级全部 ID；`POST /category/batch` 支持 delete / merge / restore / permanent_delete
- 合并：笔记和活跃子分类并入目标后软删除源分类；禁止目标是源的子孙、源之间有父子、合并后超过 3 级
- 定时任务每天 03:30 物理删除超过 `RECYCLE_BIN_CLEANUP_DAYS`（默认 14）天的分类；`api_reload` / 测试环境不启动调度器

**笔记进阶（28 阶段）**

- 创建时可选 `format=md|txt`，写入后不可改；纯文本编辑器不走 Markdown 预览
- `PUT /note/{id}/category` 单独移动分类（null = 未分类）；`POST /note/batch` 支持 delete / pin / unpin / move / restore / permanent_delete
- 批量彻底删除最多 50 条、恢复最多 100 条；单条失败不打断其余条目
- 笔记回收站返回 `days_remaining`；定时任务 03:00 物理删除超过 14 天的笔记并清向量（与分类 03:30 共用同一调度器）

**笔记搜索（29 阶段）**

- `POST /note/search`：当前用户活跃笔记的关键词搜索，标题命中 score=1.0 排在正文命中 0.5 前面
- LIKE 转义 `%` `_` `\`，避免把通配符当模式；已删笔记不进结果
- 本阶段不接 MySQL FULLTEXT（测试是 SQLite）；问答向量检索仍走 retriever
- 顶栏 Ctrl/Cmd+K 打开全局搜索：笔记走后端搜索，会话/知识库客户端按标题、文件名过滤
- MySQL 上 `MATCH ... AGAINST` + ngram 全文索引；SQLite / 无索引 / 无命中时回退标题加权 LIKE

**笔记模板（30 阶段）**

- `note_templates` 表：名称 + JSON 骨架（`markdown` / `content` / `body`）
- CRUD + `POST /note-template/{id}/apply` 套用模板新建笔记；跨用户 404
- 前端「模板」页可保存骨架并套用进编辑器

**笔记 AI 辅助（31 阶段）**

- `POST /note/autocomplete`、`/note/write-assistant`（continue / expand / summary）、`/note/auto-tag`
- 注入函数 > `LLM_API_KEY` > 空结果；失败不打断编辑
- 测试可 `set_note_ai_fn` 注入，不打外网

## 本地运行

```powershell
# 后端
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt -r requirement-dev.txt
Copy-Item .env.example .env
docker compose up -d
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m pytest
.venv\Scripts\python main.py          # API: http://127.0.0.1:8001/docs

# 前端（另开终端）
cd front
npm install
npm run dev                            # http://localhost:3000
```

注意：本机 npm 全局缓存目录若有写入权限问题，可加 `--cache .npm-cache` 使用项目内缓存。

## 前端目录同步约定

前端代码同时维护两份，内容保持一致（每次前端改动后同步）：

- 主开发位置：`D:\Project\RAG_LearnLittleCode_Rebuild\front`
- 同步副本：`D:\Project\learnLittle\front`（该目录下另有一份后端拷贝，由所有者自行管理，本项目不读写）

`learnLittle\front` 只包含前端文件；后端代码、依赖与配置不会写入 `D:\Project\learnLittle`。

## 下一阶段

艾宾浩斯回顾（今日待复习 / 完成 / 统计；给后面 Agent 工具留接口）。

