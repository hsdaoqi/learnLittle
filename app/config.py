from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置；环境变量会覆盖这里定义的默认值。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "LearnLittle"
    app_version: str = "0.1.0"
    app_env: Literal["development", "test", "production"] = "development"

    api_host: str = "127.0.0.1"
    api_port: int = 8001
    api_reload: bool = True

    mysql_host: str = "localhost"
    mysql_port: int = 13306
    mysql_user: str = "daoqi"
    mysql_password: str = "123456"
    mysql_database: str = "raglearn"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # 分类 / 笔记回收站：超过该天数由定时任务物理删除
    recycle_bin_cleanup_days: int = 14

    jwt_secret: str = "dev-only-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # 知识库上传：本阶段只落盘 + 记元数据，解析/向量化下一阶段再接
    max_upload_size_mb: int = 50
    upload_dir: str = "data/uploads"
    avatar_dir: str = "data/avatars"
    max_avatar_size_mb: int = 5
    max_device_sessions: int = 5

    # 接口护栏：Redis 固定窗口。测试关闭，避免打爆登录锁定等用例
    rate_limit_enabled: bool = True
    rate_limit_window_seconds: int = 60
    rate_limit_global: int = 100
    rate_limit_default: int = 30

    chroma_persist_dir: str = "data/chroma"
    chroma_collection_rag: str = "rag_collection"
    chroma_collection_notes: str = "notes_collection"
    chunk_size: int = 400
    chunk_overlap: int = 80
    embedding_dim: int = 64
    embedding_batch_size: int = 20
    embedding_cache_ttl_seconds: int = 300
    embedding_cache_max_entries: int = 10000

    # OpenAI 兼容接口；未配置 api_key 时问答退回本地拼接
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_api_key: str = ""
    llm_model: str = "qwen-plus"
    # enable_thinking 协议：auto 仅百炼域名带该字段；none 永不传（GPT 兼容网关）
    llm_thinking_protocol: Literal["auto", "dashscope", "none"] = "auto"

    # Embedding：未配 key 时用哈希向量；embedding_api_key 为空则复用 llm_api_key
    embedding_base_url: str = ""
    embedding_api_key: str = ""
    embedding_model: str = "text-embedding-v3"

    # 混合检索：向量多取几路再和 BM25 做 RRF；重排序可注入 / CrossEncoder / 词重叠
    hybrid_candidate_multiplier: int = (
        4  # 放大候选数量（求 top 5 则各路查 20 条），防止漏掉好答案
    )
    hybrid_max_candidates: int = 50  # 单路最多抓取数量封顶，防止内存与耗时失控
    rrf_k: int = 60  # RRF 倒数排名的平滑常数，平衡向量与关键词的名次权重
    bm25_k1: float = 1.5  # 词频饱和度，防止同一关键词反复出现导致分数恶意膨胀
    bm25_b: float = 0.75  # 篇幅惩罚系数，惩罚废话多的大长文，偏好精准命中的短文本
    bm25_max_docs: int = 500  # 内存 BM25 计算时的文档数量上限，保护 CPU 性能
    rerank_enabled: bool = True  # 总开关：是否在最后使用重排模型对结果做二次打分提纯
    rerank_model: str = "BAAI/bge-reranker-v2-m3"
    rerank_download: bool = False

    # HyDE：问答检索前用 LLM 生成假设性回答；失败或未配密钥则回退原问题
    hyde_enabled: bool = True
    hyde_cache_ttl_seconds: int = 3600

    # RAG 路由：问答前用 Top-1 向量距离判断要不要检索；大于阈值则跳过 HyDE 和混合检索
    rag_route_enabled: bool = True
    rag_route_threshold: float = 0.5

    # 多轮上下文：每个会话带上最近 N 轮（一问一答算一轮）；单条过长则截断
    chat_history_rounds: int = 6
    chat_history_max_chars: int = 400

    # Redis 热缓存：会话列表短 TTL；最近 N 条消息进 List。失败不影响 MySQL
    chat_cache_enabled: bool = True
    chat_cache_buffer_size: int = 20
    chat_cache_session_ttl_seconds: int = 300

    # Token 预算：窗口内先扣固定预留和检索占用，剩余给历史；再按从新到旧滑动截断
    token_model_context_size: int = 32768
    token_system_prompt: int = 500
    token_rag_context_max: int = 2000
    token_current_input_estimate: int = 300
    token_safety_margin: int = 1000
    token_history_min: int = 500
    token_agent_scratchpad_reserve: int = 0
    token_summary_reserve: int = 800

    # 记忆压缩：消息足够多时把窗口外旧对话压成里程碑摘要
    memory_summarize_enabled: bool = True
    memory_summarize_threshold: int = 40
    memory_min_summary_interval: int = 20
    memory_keep_recent: int = 20
    memory_summary_max_tokens: int = 800

    # 检索后摘要：命中后用 LLM 压成短参考；关闭或失败则截断
    rag_summarize_enabled: bool = True
    rag_summarize_truncate_max_chars: int = 800
    rag_summarize_input_max_chars: int = 2000

    # Agent：问答里可调笔记/回顾工具。无密钥时用关键词走本地工具
    agent_enabled: bool = True
    # ReAct 整轮超时（秒）。深度思考时按 2 倍放宽
    llm_stream_timeout: int = 60
    # 同一用户同时打开的 /chat/query SSE 连接上限
    sse_max_connections_per_user: int = 3

    # 查询分类：L1 规则；不确定且开了 L2 才调轻量补全。失败一律 simple
    classifier_enabled: bool = True
    classifier_l2_enabled: bool = True
    classifier_complex_min_length: int = 200
    classifier_short_msg_length: int = 50
    # 分类器思考模式。默认关：qwen-flash 开思考会拖过 L2 超时
    classifier_enable_thinking: bool = False
    # Plan-Execute：complex 查询先规划再执行；失败降级 ReAct。
    plan_execute_enabled: bool = True
    plan_execute_max_steps: int = 5
    # 计划生成思考模式。默认关：开思考容易耗尽规划预算
    plan_enable_thinking: bool = False

    # Reflection：L1 综合后自检；L2 工具失败最多再试一轮。解析失败视为通过
    reflection_l1_enabled: bool = True
    reflection_l2_enabled: bool = True
    reflection_min_answer_chars: int = 80
    reflection_no_retry_tools: str = "send_email"
    # 批判模型思考模式。默认关；修正稿跟主模型思考开关
    reflection_enable_thinking: bool = False

    # 会话自动标题：首轮生成一次；失败回退截断问句；手动改名后不再覆盖
    chat_auto_title_enabled: bool = True
    chat_auto_title_max_chars: int = 20
    chat_auto_title_fallback_chars: int = 40

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "LearnLittle"

    def validate_security(self) -> None:
        """生产环境安全校验：拒绝使用开发默认密钥或过短的 JWT_SECRET。"""
        if self.app_env != "production":
            return
        if (
            self.jwt_secret == "dev-only-secret-change-in-production"
            or len(self.jwt_secret) < 16
        ):
            raise RuntimeError(
                "生产环境必须配置强随机 JWT_SECRET（至少 16 字符），例如："
                'python -c "import secrets; print(secrets.token_hex(32))"'
            )


@lru_cache
def get_settings() -> Settings:
    """每个进程只解析一次配置文件。"""
    return Settings()
