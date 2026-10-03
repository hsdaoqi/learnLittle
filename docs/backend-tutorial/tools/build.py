"""Render and verify backend tutorial coverage using AST only, never app imports."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

import inventory
from notes import INJECTION_LABELS, LAMBDA_NOTES, MIGRATIONS, NOTES

ROOT = inventory.ROOT
DOCS = ROOT / "docs/backend-tutorial"

CHAPTERS = {
    1: "01-structure.md",
    2: "02-account.md",
    3: "03-notes.md",
    4: "04-learning.md",
    5: "05-rag.md",
    6: "06-query.md",
    7: "07-agent.md",
    8: "08-memory.md",
    9: "09-operations.md",
    10: "10-tests.md",
}

MODULES = {}


def modules(chapter, text):
    for line in text.strip().splitlines():
        path, purpose = line.split("|", 1)
        MODULES[path] = (chapter, purpose)


modules(1, """
main.py|应用装配与生命周期；路由/资源从这里接上，不包含全部业务逻辑。
app/config.py|配置类型、默认值与生产密钥约束；实际环境可覆盖默认。
app/db/database.py|SQL URL、engine、session 与普通请求事务所有权。
app/db/redis_client.py|Redis 单例资源与注入/探针；并非所有使用者都采用相同容错策略。
app/core/exception_handlers.py|把业务、校验与未预期异常转换为 HTTP 失败信封。
app/core/success_response.py|普通成功响应字典；不承担事务提交。
app/core/failed_response.py|错误码、BusinessError 载体与失败响应字典。
app/models/base.py|全体 ORM 的声明式 Base，向 Alembic 暴露 metadata。
""")
modules(2, """
app/utils/auth_utils.py|密码、JWT、Redis 安全状态、短期聊天票和设备会话；顶部旧注释不代表设备功能缺失。
app/utils/file_handler.py|文档/头像的大小和格式约束、安全文件名与受限读取，兼用于上传章节。
app/routers/user.py|账号认证与资料 HTTP 适配，默认注册要求邮箱验证。
app/schemas/auth.py|注册/登录/刷新/资料/邮件请求和公开响应的数据契约。
app/models/user.py|users 表的凭据、资料与状态；uuid 是其他业务表的归属外键。
""")
modules(3, """
app/routers/note_router.py|笔记 CRUD、批量、搜索及写作/邮件入口；静态路径在动态 note_id 路由前注册。
app/routers/category_router.py|分类树、移动、回收站、排序和批量合并 HTTP 入口。
app/services/note_service.py|笔记业务权限、SQL 生命周期、关键词检索和提交后向量同步。
app/services/category_service.py|最多三层树与软删/恢复/合并规则；树算法一次加载再计算。
app/models/note.py|notes 表，正文/格式/标签/分类/置顶和删除时间；向量存在 Chroma 而非这一行。
app/models/category.py|note_categories 自引用树，软删除与同级名称规则由 service 维护。
app/schemas/note.py|笔记创建/部分更新/搜索/批量/写作建议的字段限制和响应形状。
app/schemas/category.py|分类创建/改名/移动/排序/批量参数；Schema 不能代替数据库所有权检查。
""")
modules(4, """
app/services/email_service.py|SMTP MIME 发送、验证码 Redis 状态与附件构造；发信不是 SQL 事务。
app/services/note_template_service.py|模板 CRUD 与应用为普通笔记，复用笔记生命周期。
app/services/note_ai_service.py|补全/写作/标签建议，输出建议而不自动保存笔记。
app/services/review_service.py|固定间隔回顾状态与 Agent 文本适配；没有完整复习事件日志。
app/routers/note_template_router.py|模板 HTTP CRUD 和套用创建入口。
app/routers/review_router.py|今日回顾、完成和统计 HTTP 入口。
app/models/note_template.py|note_templates 保存用户自定义 JSON 骨架和文字 category。
app/models/review.py|review_records 每笔记唯一，保留当前进度/下次时间和最近完成时间。
app/schemas/template.py|模板创建、部分更新、应用和响应契约。
app/schemas/review.py|待复习项目、完成响应、统计与 0..5 的质量字段。
""")
modules(5, """
app/routers/knowledge_router.py|知识文档上传 SSE、元数据列表/详情/删除与直接检索。
app/services/knowledge_service.py|文件、SQL 文档记录和 Chroma 切片的上传编排；不具备分布式事务。
app/models/knowledge.py|knowledge_documents 文件路径、MD5、类型和切片数；旧头注释的 chunk_count=0 已过时。
app/schemas/knowledge.py|文档响应不暴露本地路径，搜索 hit 限定公开字段。
app/rag/document_parser.py|bytes->纯文本；PDF 文字提取，不含 OCR。
app/rag/text_splitter.py|标题/段落/字符滑窗切片与 TextChunk 结构。
app/rag/embeddings.py|注入/API/无 key 哈希向量、批处理与进程 TTL/LRU 缓存。
app/rag/vector_store.py|Chroma 双 collection 的嵌入写入、双源检索、用户过滤与删除。
app/rag/retriever.py|分词、BM25、RRF、CrossEncoder 适配和词重叠兜底。
app/rag/hyde.py|生成假设查询并 Redis 缓存，主聊天默认由外层关闭。
app/rag/rag_route.py|根据当前用户双源 Top-1 距离决定是否检索。
app/rag/rag_summarize.py|命中副本压缩/截断，原命中留作来源展示。
""")
modules(6, """
app/routers/chat_router.py|唯一 query 聊天入口和会话管理；直接调用 query_service，没有旧问答兼容链。
app/services/query_service.py|用户先提交、并行上下文、图执行、助手提交和后台维护的主编排。
app/schemas/chat.py|QueryRequest 与公开会话/消息响应；附件 ID 当前只用于 thinking 互斥。
app/models/chat.py|会话、消息、里程碑摘要三表；手动标题和用户角色哈希幂等键保护生命周期。
""")
modules(7, """
app/ai_service/chat_graph.py|可取消 LangGraph 分类/执行图与有界输出队列。
app/ai_service/langchain_tools.py|注册表描述到 StructuredTool 的轻量参数 Schema 适配。
app/ai_service/models.py|角色模型名选择，共享现有 key/base_url。
app/ai_service/plan_execute.py|依赖计划、限量并行读/串行写、步骤 ReAct、综合与安全降级。
app/ai_service/query_classifier.py|L1 规则、L2 补全和安全默认简单路线。
app/ai_service/react_agent.py|真实 LangChain 工具循环、事件协议、工具重试护栏和答案反思。
app/ai_service/reflection.py|L1 批判/修订实时状态与 L2 修复提示，失败不阻断已有草稿。
app/ai_service/review_tools.py|回顾 service 到 Agent 文本工具的薄适配。
app/ai_service/runner.py|无模型关键词工具与测试注入；真实模型工具循环只在 ReAct 主链。
app/ai_service/thinking.py|协议兼容、附件互斥、角色独立 thinking 和超时放宽。
app/ai_service/tool_registry.py|内存 ToolSpec/分组/实现绑定/只读能力描述。
app/ai_service/tools.py|绑定认证用户的内置笔记/回顾工具，写工具自管事务。
""")
modules(8, """
app/services/chat_service.py|会话 CRUD 与消息数据操作；不包含独立问答实现或 query 转发。
app/rag/chat_cache.py|会话列表短 TTL、近期消息 List；不是新 Agent 的唯一记忆。
app/rag/chat_history.py|SQL 未摘要历史的实际 Token 预算选择，保持消息角色。
app/rag/token_budget.py|tokenizer/字符估算与单条消息开销计数；配额在 chat_history 计算。
app/rag/memory.py|按消息检查点增量压缩旧历史，保留近期原文。
app/rag/session_title.py|标题文本生成/清洗/失败兜底，写库竞争保护在 query_service。
app/rag/note_cards.py|带真实 note_id 的搜索文本和用户引用块解析。
app/rag/llm.py|httpx 非流式辅助补全，复用于分类、计划、摘要、标题和反思；不是工具执行器。
""")
modules(9, """
app/core/after_commit.py|Session 事件监听，成功提交派发、回滚丢弃派生工作。
app/core/task_runner.py|进程内后台任务跟踪、同 key 串行与有界关机回收。
app/core/rate_limit.py|Redis 固定窗口，全局与具体 path 桶、特殊动作额度。
app/core/scheduler.py|每天过期笔记/分类清理的调度和事务包装。
app/routers/health.py|进程健康与 SQL/Redis 就绪探针。
app/routers/usage_router.py|当前用户用量聚合 HTTP 入口。
app/services/usage_service.py|ContextVar 归属、独立 trace 事务、用量和本地价格聚合。
app/models/usage.py|model_traces 与 model_pricing 数据结构，不是独立工具审计表。
app/ai_service/usage_callback.py|每次 LangChain 模型调用的输入/输出/usage/失败计量。
app/ai_service/sse_slot.py|主聊天按用户并发计数，Redis 故障退进程内。
""")

CLASS_NOTES = {
    "Settings": "应用配置：默认值可被环境覆盖；配置 groups 见任务章，下面列出当前声明而不读取真实 .env。",
    "Base": "ORM 共享声明式基类，Base.metadata 收集表结构；本身没有业务字段或显式函数。",
    "User": "账户事实。password 为哈希，status 是字段；存在这个字段不等于每条鉴权路径都重新查询状态。",
    "NoteCategory": "自引用 parent_id 表示树，user_id 表示归属，deleted_at 表示软删；三层限制在 service。",
    "Note": "笔记事实。category_id 可空、物理分类删除 SET NULL，tags 是 JSON，format 不由更新 Schema 修改。",
    "KnowledgeDocument": "原文件元数据和存储路径，chunk_count 为实际切片数，正文切片另存 Chroma。",
    "ChatSession": "会话归属、标题与更新时间，title_manual 防后台覆盖人工标题。",
    "ChatMessage": "消息事实，角色/正文/会话外键和可空唯一防重键；idempotency_key 由用户+角色+客户端 key 哈希。",
    "ChatSummary": "每会话唯一摘要；last_message_id 是覆盖到的消息 ID，不是消息数量。",
    "NoteTemplate": "JSON 正文骨架；category 是标签式文字，不是分类树外键。",
    "ReviewRecord": "note_id 唯一，表示每笔记当前复习状态；reviewed_at 仅最后一次，不是事件日志。",
    "ModelTrace": "一次模型调用的归属、阶段、模型、Token、耗时及成败；没有完整工具参数审计。",
    "ModelPricing": "本地每千 Token 输入/输出价格与币种；不是实时官方定价。",
    "ErrorCode": "纯业务码常量集合，与 HTTP 状态分离；没有函数也仍是重要接口契约。",
    "BusinessError": "携带 code/message/detail/http_status 的异常，由 handler 转为 HTTP 响应。",
    "RateLimitMiddleware": "继承请求中间件，把固定窗口检查接到路由之前。",
    "TextChunk": "切片纯数据，保存正文、章节名、序号；dataclass 生成的方法不计为手写函数。",
    "TextSplitter": "持有字符 size/overlap 的切分器，显式方法在函数详解内。",
    "VectorStoreService": "封装 Chroma client 与双 collection 的生命周期、检索和删除。",
    "TokenCounter": "类级编码器缓存与计数入口；失败估算不等于供应商账单。",
    "RouteDecision": "是否检索、距离与原因的不可变结果，不表示 ReAct/Plan 复杂度分类。",
    "PlanStep": "步骤号、action、建议工具、依赖号和执行结果；结果供后续真实 ID 上下文。",
    "ExecutionPlan": "目标与有序步骤集合，依赖执行还要经过拓扑校验。",
    "ClassificationResult": "复杂度、来源、理由、置信值和路线；置信值是程序给定，不是校准概率。",
    "ThinkingDecision": "保留请求值与实际应用值及原因，便于解释附件/协议导致的降级。",
    "ReflectionVerdict": "批判结果 passed/issues；无法可信解析的批判会被按通过处理。",
    "ToolSpec": "模型看到的描述/参数与 Python 实现、分组和只读并行能力。",
    "ToolRegistry": "内存映射管理器，不提供持久化审计或模型权限之外的数据库自动隔离。",
    "ChatState": "LangGraph TypedDict 状态，目前只声明 route；事件不是都塞 state，而是队列转发。",
    "ModelUsageCallback": "LangChain 异步 callback，以 run_id 区分同轮多次模型调用。",
    "UsageTimer": "直接客户端和注入函数的一次调用计时包装。",
}


def module_info(path):
    if path in MODULES:
        return MODULES[path]
    if path.startswith("tests/"):
        return 10, "隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。"
    if path == "alembic/env.py":
        return 10, "Alembic 在线/离线入口与异步连接桥接；直接执行会采用配置数据库，文档工具不会导入它。"
    if path.startswith("alembic/versions/"):
        revision = Path(path).stem.split("_")[0]
        return 10, "数据库增量迁移：" + MIGRATIONS[revision][0] + "。"
    if path.endswith("/__init__.py"):
        if path == "app/models/__init__.py":
            return 1, "导入并重新导出所有 ORM 类型，让 Base.metadata 收齐表；不是空包标记。"
        return 1, "Python 包入口/命名空间文件；本快照没有显式函数，具体导入/赋值见结构声明。"
    raise ValueError(f"Missing module explanation: {path}")


def link(path, line=None, anchor=None):
    target = Path(path).as_posix()
    if line is not None:
        target += f":{line}"
    if anchor:
        target += f"#{anchor}"
    return target


def atlas_name(path):
    return path.replace("/", "--").removesuffix(".py") + ".md"


def anchor(function):
    return "fn-" + hashlib.sha256(function["id"].encode()).hexdigest()[:16]


def explanation(file, function, lambda_position):
    path = file["path"]
    name = function["qualname"]
    if function["anonymous"]:
        return LAMBDA_NOTES[path][lambda_position], "逐项人工说明"
    if name in NOTES.get(path, {}):
        return NOTES[path][name], "逐项人工说明"
    if path.startswith("alembic/versions/"):
        revision = Path(path).stem.split("_")[0]
        if name == "upgrade":
            return MIGRATIONS[revision][0] + "。由 Alembic 在此版本执行；不要把表定义 import 当成已经迁移。", "迁移逐项说明"
        if name == "downgrade":
            return MIGRATIONS[revision][1] + "。逆向结构操作有数据风险，本教程不执行。", "迁移逐项说明"
    node = ast.parse(function["source"]).body[0]
    if function["name"] == "__repr__" and path.startswith("app/models/"):
        returned = ast.unparse(next(n for n in node.body if isinstance(n, ast.Return)).value)
        return (
            f"{name.rsplit('.', 1)[0]} 的调试字符串表示，返回 `{returned}`。"
            "用于日志/交互查看，不是 API Schema 序列化，也不查询或提交数据库。"
        ), "按精确返回式说明"
    label = INJECTION_LABELS.get(path)
    if label and function["name"].startswith("set_"):
        assignments = [n for n in node.body if isinstance(n, ast.Assign)]
        globals_ = [n for n in node.body if isinstance(n, ast.Global)]
        if len(assignments) == 1 and len(globals_) == 1:
            target = ast.unparse(assignments[0].targets[0])
            if target.startswith("_injected"):
                return (
                    f"替换{label}的模块级注入槽 `{target}`，赋值为传入函数；None 表示撤销注入。"
                    "setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。"
                ), "简单注入槽的 AST 校验说明"
    if label and function["name"].startswith("get_") and len(node.body) == 1:
        returned = node.body[0]
        if isinstance(returned, ast.Return) and isinstance(returned.value, ast.Name):
            if returned.value.id.startswith("_injected"):
                return (
                    f"返回{label}当前的注入函数 `{returned.value.id}` 或 None，不调用它。"
                    "调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。"
                ), "简单注入槽的 AST 校验说明"
    raise ValueError(f"Missing function explanation: {path}::{name}")


def facts(function):
    if function["anonymous"]:
        node = ast.parse(function["source"], mode="eval").body
        return "", [("表达式返回", ast.unparse(node.body))]
    node = ast.parse(function["source"]).body[0]
    results = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, child):
            if child is node:
                self.generic_visit(child)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, child):
            pass

        def visit_Lambda(self, child):
            pass

        def visit_Return(self, child):
            results.append(("return", ast.unparse(child.value) if child.value else "None"))
            self.generic_visit(child)

        def visit_Yield(self, child):
            results.append(("yield", ast.unparse(child.value) if child.value else "None"))
            self.generic_visit(child)

        def visit_YieldFrom(self, child):
            results.append(("yield from", ast.unparse(child.value)))
            self.generic_visit(child)

        def visit_Assert(self, child):
            results.append(("assert", ast.unparse(child.test)))
            self.generic_visit(child)

    Visitor().visit(node)
    returns = " -> " + ast.unparse(node.returns) if node.returns else ""
    return returns, list(dict.fromkeys(results))


def compact(text, limit=230):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit] + " ... [截短，完整见源码]"


def statement_block(statements):
    return "\n\n".join(ast.unparse(n) for n in statements)


def class_explanation(node, path):
    if node.name in CLASS_NOTES:
        return CLASS_NOTES[node.name]
    if path.startswith("app/schemas/"):
        fields = [
            n.target.id for n in node.body
            if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
        ]
        return (
            "Pydantic 数据契约，声明 " + "、".join(fields) + "。"
            "下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。"
            "未声明的业务所有权/数据库关系仍由 service 校验。"
        )
    if path.startswith("tests/"):
        return "测试替身类，显式方法在本文件详解；实例只提供该测试需要的可控行为，不代表生产模型实现。"
    raise ValueError(f"Missing class explanation: {path}::{node.name}")


def generate(data):
    outputs = {}
    manifest = []
    index = [
        "# 后端逐函数详解",
        "",
        f"[教程入口]({link(DOCS / 'README.md')}) | [全部函数快查]({link(DOCS / 'functions.md')})",
        "",
        "按文件分册，每个函数都有独立说明。简单注入 setter/getter 和 ORM repr 按精确 AST 模式解释，"
        "不是把所有未知函数套一句泛化说明；未知项会让生成失败。",
        "",
        "| 文件 | 函数数 | 任务章 |",
        "| --- | ---: | --- |",
    ]
    quick = ["# 全部函数快查", "", "按文件/定义顺序列出；点击名称进入对应解释，不必全文搜索源代码。", ""]
    structure = [
        "# 后端结构与字段清单", "",
        f"[总教程]({link(DOCS / 'README.md')}) | [逐函数入口]({link(DOCS / 'atlas/README.md')})", "",
        "此清单覆盖零函数文件、类声明、配置与包导出。字段/常量代码块由 AST 提取，不导入应用，"
        "不读取真实 .env；源码默认值不能代表运行环境。自动生成的 dataclass/Pydantic/ORM 方法不是本项目手写定义，故不计函数数。",
        "",
        "ORM 关系：User -> 分类/笔记/文档/会话/模板/回顾；分类 parent_id 自引用，笔记 category_id 可空；"
        "会话 -> 消息与唯一摘要；笔记 -> 唯一回顾记录。Trace 的归属标识用于查询，不应假设所有标识都声明了数据库 FK。",
        "",
    ]
    errors = []
    used_manual = set()
    for file in data["files"]:
        path = file["path"]
        chapter, purpose = module_info(path)
        chapter_path = DOCS / CHAPTERS[chapter]
        outpath = DOCS / "atlas" / atlas_name(path)
        index.append(f"| [{path}]({link(outpath)}) | {len(file['functions'])} | [{chapter:02d}]({link(chapter_path)}) |")
        quick += [f"## {path}", ""]
        lines = [
            f"# {path}", "",
            f"[源码]({link(ROOT / path)}) | [任务流程 {chapter:02d}]({link(chapter_path)}) | "
            f"[详解目录]({link(DOCS / 'atlas/README.md')})", "",
            purpose, "",
            "## 本文件导航", "",
        ]
        for fn in file["functions"]:
            lines.append(f"- [{fn['qualname']}](#{anchor(fn)})")
            quick.append(f"- [{fn['qualname']}]({link(outpath, anchor=anchor(fn))})")
        if not file["functions"]:
            lines.append("本文件没有显式函数；请看下方结构声明，不计作遗漏。")
            quick.append("- 无显式函数，结构声明仍在文件详解。")
        tree = ast.parse((ROOT / path).read_text(encoding="utf-8-sig"))
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        if classes:
            lines += ["", "## 类与字段", ""]
            for cls in sorted(classes, key=lambda n: n.lineno):
                try:
                    meaning = class_explanation(cls, path)
                except ValueError as exc:
                    errors.append(str(exc))
                    meaning = ""
                declarations = [
                    n for n in cls.body if isinstance(n, (ast.Assign, ast.AnnAssign))
                ]
                lines += [
                    f"### {cls.name}", "",
                    meaning, "",
                    f"声明位置：[L{cls.lineno}]({link(ROOT / path, line=cls.lineno)})。"
                    f"父类：`{', '.join(ast.unparse(b) for b in cls.bases) or '无显式父类'}`。", "",
                ]
                if declarations:
                    lines += ["```python", statement_block(declarations), "```", ""]
        top_declarations = [
            n for n in tree.body if isinstance(n, (ast.Assign, ast.AnnAssign))
        ]
        if top_declarations:
            lines += ["", "## 模块声明", "", "常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。", "",
                      "```python", statement_block(top_declarations), "```", ""]
        if path.endswith("/__init__.py"):
            imports = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
            lines += ["", "## 包导入", "", "```python",
                      statement_block(imports) if imports else "# No explicit package imports.",
                      "```", ""]
        lambda_position = 0
        for fn in file["functions"]:
            try:
                text, origin = explanation(file, fn, lambda_position)
            except (ValueError, KeyError, IndexError) as exc:
                errors.append(f"{fn['id']}: {exc}")
                text, origin = "", "missing"
            if fn["anonymous"]:
                lambda_position += 1
            elif fn["qualname"] in NOTES.get(path, {}):
                used_manual.add((path, fn["qualname"]))
            if len(text) < 30:
                errors.append(f"Explanation too short: {fn['id']}")
            returns, exits = facts(fn)
            prefix = "lambda" if fn["anonymous"] else (
                "async def" if fn["source"].startswith("async def") else "def"
            )
            signature = (
                fn["source"] if fn["anonymous"]
                else f"{prefix} {fn['name']}({fn['params']}){returns}"
            )
            lines += [
                f'<a id="{anchor(fn)}"></a>', "",
                f"## {fn['qualname']}", "",
                f"源码：[L{fn['line']}]({link(ROOT / path, line=fn['line'])})；"
                f"任务：[第 {chapter:02d} 章]({link(chapter_path)})。", "",
                text, "",
                "**输入与签名**", "", "```python", signature, "```", "",
            ]
            if fn["decorators"]:
                lines += ["装饰器/挂载：", "", "```python",
                          "\n".join("@" + d for d in fn["decorators"]), "```", ""]
            lines += ["**出口与观察点**", ""]
            if exits:
                lines += [
                    "下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，"
                    "嵌套函数的出口列在其自身条目。", "",
                    "```python",
                    "\n".join(f"{kind} {compact(value)}" for kind, value in exits[:8]),
                    "```", "",
                ]
                if len(exits) > 8:
                    lines += [f"另有 {len(exits) - 8} 个出口/断言，完整条件见源码。", ""]
            else:
                lines += [
                    "没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，"
                    "正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。", ""
                ]
            if fn["calls"]:
                lines += [
                    "**调用线索**", "",
                    "下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。", "",
                    "```text", "\n".join(fn["calls"]), "```", "",
                ]
            manifest.append({
                "id": fn["id"], "path": path, "qualname": fn["qualname"],
                "line": fn["line"], "source_sha256": file["sha256"],
                "explanation": text, "origin": origin,
                "atlas": outpath.relative_to(DOCS).as_posix(),
                "anchor": anchor(fn), "chapter": CHAPTERS[chapter],
            })
        if lambda_position != len(LAMBDA_NOTES.get(path, [])):
            errors.append(f"Lambda explanation count mismatch: {path}")
        outputs[outpath] = "\n".join(lines).rstrip() + "\n"
        structure += [
            f"## {path}", "", purpose, "",
            f"[完整声明与函数说明]({link(outpath)})；"
            f"显式函数 {len(file['functions'])}；类 {len(classes)}。", "",
        ]
        if classes:
            structure += ["类：" + "、".join(f"`{c.name}`" for c in classes) + "。", ""]
    stale = set((path, name) for path, entries in NOTES.items() for name in entries) - used_manual
    errors.extend(f"Stale manual explanation: {path}::{name}" for path, name in sorted(stale))
    if errors:
        raise ValueError("\n".join(errors))
    outputs[DOCS / "atlas/README.md"] = "\n".join(index) + "\n"
    outputs[DOCS / "functions.md"] = "\n".join(quick) + "\n"
    outputs[DOCS / "structure.md"] = "\n".join(structure) + "\n"
    outputs[DOCS / "explanations.json"] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    named = sum(not fn["anonymous"] for f in data["files"] for fn in f["functions"])
    test_defs = sum(fn["name"].startswith("test_") for f in data["files"] if f["path"].startswith("tests/")
                    for fn in f["functions"])
    counts = {}
    for row in manifest:
        counts[row["origin"]] = counts.get(row["origin"], 0) + 1
    report = [
        "# 后端教程覆盖报告", "",
        "源代码快照日期：2026-10-02。报告由静态 AST 与人工说明映射生成，不启动应用。", "",
        f"- Python 文件：{len(data['files'])}。",
        f"- 显式函数定义：{len(manifest)}，其中命名函数/方法/嵌套函数 {named}，lambda {len(manifest)-named}。",
        f"- 独立函数解释及锚点：{len(manifest)}；缺失：0；陈旧映射：0。",
        f"- test_* 定义：{test_defs}；参数化执行数另算，未在本轮重新执行业务测试。",
        "- 全部文件 SHA256 已与清单核对；AST 本身重新扫描以发现新增/删除文件。",
        "- 文档覆盖率不等于测试覆盖率，也不代表所有外部服务集成已验证。",
        "",
        "## 说明来源", "",
    ]
    report += [f"- {origin}：{count}。" for origin, count in sorted(counts.items())]
    report += [
        "", "所有非通用业务函数及测试/辅助函数有逐项人工说明；通用注入槽只有在 AST 符合"
        "单全局赋值/单返回模式时才采用精确模式说明。没有以 TODO、仅列函数名或原 docstring 凑覆盖。",
        "", "## 检查命令", "", "```powershell",
        "Set-Location D:\\Project\\learnLittle",
        ".\\.venv\\Scripts\\python.exe docs\\backend-tutorial\\tools\\build.py --check",
        "```", "",
        "检查失败时，先审读改变的源函数并更新 tools/notes.py 和任务章，再执行：", "",
        "```powershell",
        ".\\.venv\\Scripts\\python.exe docs\\backend-tutorial\\tools\\inventory.py",
        ".\\.venv\\Scripts\\python.exe docs\\backend-tutorial\\tools\\build.py",
        ".\\.venv\\Scripts\\python.exe docs\\backend-tutorial\\tools\\build.py --check",
        "```", "",
        "检查器验证当前源码与 inventory 一致、每个函数有解释、每个解释有对应定义、生成文档内容一致、"
        "教程内本地文件/显式锚点链接有效。人工语义准确性仍需审读，不能由覆盖数字替代。",
        "", "## 每文件快照", "", "| 文件 | 函数数 | SHA256 |", "| --- | ---: | --- |",
    ]
    report += [
        f"| `{f['path']}` | {len(f['functions'])} | `{f['sha256']}` |"
        for f in data["files"]
    ]
    outputs[DOCS / "coverage.md"] = "\n".join(report) + "\n"
    return outputs, manifest


def verify_links(outputs):
    errors = []
    checked = 0
    sources = {p: p.read_text(encoding="utf-8-sig") for p in DOCS.rglob("*.md")}
    sources.update({p: content for p, content in outputs.items() if p.suffix == ".md"})
    for path, content in sources.items():
        # Source snippets can contain strings resembling Markdown; only inspect prose.
        prose = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        for target in re.findall(r"\]\(([^)\n]+)\)", prose):
            if target.startswith(("http:", "https:")):
                continue
            target = target.strip("<>")
            base, _, fragment = target.partition("#")
            line_match = re.search(r":(\d+)$", base)
            line = int(line_match.group(1)) if line_match else None
            if line_match:
                base = base[:line_match.start()]
            dest = Path(base) if base else path
            if base and not dest.is_absolute():
                dest = path.parent / dest
            if dest not in outputs and not dest.is_file():
                errors.append(f"Broken link in {path.name}: {target}")
                continue
            checked += 1
            if fragment:
                dest_content = outputs.get(dest)
                if dest_content is None:
                    dest_content = dest.read_text(encoding="utf-8-sig")
                if f'id="{fragment}"' not in dest_content:
                    errors.append(f"Missing explicit anchor in {path.name}: {target}")
            if line is not None:
                count = len(dest.read_text(encoding="utf-8-sig").splitlines())
                if not 1 <= line <= count:
                    errors.append(f"Invalid line in {path.name}: {target}")
    if errors:
        raise ValueError("\n".join(errors))
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    saved = json.loads(inventory.OUTPUT.read_text(encoding="utf-8"))
    current = inventory.collect()
    if saved != current:
        raise ValueError("Source inventory is stale. Review changes before rebuilding inventory and explanations.")
    outputs, manifest = generate(current)
    checked_links = verify_links(outputs)
    if args.check:
        mismatches = [
            str(path) for path, content in outputs.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        if mismatches:
            raise ValueError("Missing or stale generated files:\n" + "\n".join(mismatches))
        for row in manifest:
            text = outputs[DOCS / row["atlas"]]
            if text.count(f'id="{row["anchor"]}"') != 1:
                raise ValueError(f"Duplicate/missing anchor: {row['id']}")
        status = "verified"
    else:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        status = "generated"
    print(json.dumps({
        "status": status, "source_files": len(current["files"]),
        "function_explanations": len(manifest), "missing": 0,
        "generated_files": len(outputs), "checked_local_links": checked_links,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
