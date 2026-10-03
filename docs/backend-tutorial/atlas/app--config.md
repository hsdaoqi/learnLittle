# app/config.py

[源码](D:/Project/learnLittle/app/config.py) | [任务流程 01](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

配置类型、默认值与生产密钥约束；实际环境可覆盖默认。

## 本文件导航

- [Settings.validate_security](#fn-553548c5b5b21ff7)
- [get_settings](#fn-f3e0a20a279c3fb9)

## 类与字段

### Settings

应用配置：默认值可被环境覆盖；配置 groups 见任务章，下面列出当前声明而不读取真实 .env。

声明位置：[L7](D:/Project/learnLittle/app/config.py:7)。父类：`BaseSettings`。

```python
model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

app_name: str = 'LearnLittle'

app_version: str = '0.1.0'

app_env: Literal['development', 'test', 'production'] = 'development'

api_host: str = '127.0.0.1'

api_port: int = 8001

api_reload: bool = True

mysql_host: str = 'localhost'

mysql_port: int = 13306

mysql_user: str = 'daoqi'

mysql_password: str = '123456'

mysql_database: str = 'raglearn'

redis_host: str = 'localhost'

redis_port: int = 6379

redis_db: int = 0

recycle_bin_cleanup_days: int = 14

jwt_secret: str = 'dev-only-secret-change-in-production'

jwt_algorithm: str = 'HS256'

access_token_expire_minutes: int = 30

refresh_token_expire_days: int = 7

max_upload_size_mb: int = 50

upload_dir: str = 'data/uploads'

avatar_dir: str = 'data/avatars'

max_avatar_size_mb: int = 5

max_device_sessions: int = 5

rate_limit_enabled: bool = True

rate_limit_window_seconds: int = 60

rate_limit_global: int = 100

rate_limit_default: int = 30

chroma_persist_dir: str = 'data/chroma'

chroma_collection_rag: str = 'rag_collection'

chroma_collection_notes: str = 'notes_collection'

chunk_size: int = 400

chunk_overlap: int = 80

embedding_dim: int = 64

embedding_batch_size: int = 20

embedding_cache_ttl_seconds: int = 300

embedding_cache_max_entries: int = 10000

llm_base_url: str = 'https://dashscope.aliyuncs.com/compatible-mode/v1'

llm_api_key: str = ''

llm_model: str = 'qwen-plus'

classifier_model: str = ''

plan_model: str = ''

reflection_model: str = ''

title_model: str = ''

classifier_timeout: float = 15.0

plan_timeout: float = 30.0

plan_step_timeout: float = 90.0

plan_synthesize_timeout: float = 60.0

plan_total_timeout: float = 300.0

plan_max_parallel_steps: int = 3

reflection_timeout: float = 15.0

rag_timeout: float = 30.0

chat_hyde_enabled: bool = False

llm_thinking_protocol: Literal['auto', 'dashscope', 'none'] = 'auto'

embedding_base_url: str = ''

embedding_api_key: str = ''

embedding_model: str = 'text-embedding-v3'

hybrid_candidate_multiplier: int = 4

hybrid_retrieval_enabled: bool = False

hybrid_max_candidates: int = 50

rrf_k: int = 60

bm25_k1: float = 1.5

bm25_b: float = 0.75

bm25_max_docs: int = 500

rerank_enabled: bool = True

rerank_model: str = 'BAAI/bge-reranker-v2-m3'

rerank_download: bool = False

hyde_enabled: bool = True

hyde_cache_ttl_seconds: int = 3600

rag_route_enabled: bool = True

rag_route_threshold: float = 0.5

chat_cache_enabled: bool = True

chat_cache_buffer_size: int = 20

chat_cache_session_ttl_seconds: int = 300

token_model_context_size: int = 32768

token_system_prompt: int = 500

token_safety_margin: int = 1000

token_agent_scratchpad_reserve: int = 4000

memory_summarize_enabled: bool = True

memory_summarize_threshold: int = 40

memory_min_summary_interval: int = 20

memory_keep_recent: int = 20

memory_summary_max_tokens: int = 800

rag_summarize_enabled: bool = True

rag_summarize_truncate_max_chars: int = 800

rag_summarize_input_max_chars: int = 2000

agent_enabled: bool = True

llm_stream_timeout: int = 60

sse_max_connections_per_user: int = 3

classifier_enabled: bool = True

classifier_l2_enabled: bool = True

classifier_complex_min_length: int = 200

classifier_short_msg_length: int = 50

classifier_enable_thinking: bool = False

plan_execute_enabled: bool = True

plan_execute_max_steps: int = 5

plan_enable_thinking: bool = False

reflection_l1_enabled: bool = True

reflection_l2_enabled: bool = True

reflection_min_answer_chars: int = 500

reflection_no_retry_tools: str = 'send_email,create_note_tool,update_note_tool,mark_reviewed_tool'

reflection_enable_thinking: bool = False

chat_auto_title_enabled: bool = True

chat_auto_title_max_chars: int = 20

chat_auto_title_fallback_chars: int = 40

chat_auto_title_rounds: int = 3

registration_require_email: bool = True

smtp_host: str = ''

smtp_port: int = 587

smtp_username: str = ''

smtp_password: str = ''

smtp_from_name: str = 'LearnLittle'
```

<a id="fn-553548c5b5b21ff7"></a>

## Settings.validate_security

源码：[L177](D:/Project/learnLittle/app/config.py:177)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

仅在 production 检查 JWT secret 不是开发默认值且长度至少 16。失败直接 RuntimeError 阻止应用构造；不验证 SMTP、数据库连通性或全部生产安全项。

**输入与签名**

```python
def validate_security(self) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
len
RuntimeError
```

<a id="fn-f3e0a20a279c3fb9"></a>

## get_settings

源码：[L192](D:/Project/learnLittle/app/config.py:192)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

读取 BaseSettings 并由 lru_cache 保存结果，供不通过 request 注入的模块共享。环境变化不会自动刷新缓存，测试使用 cache_clear 隔离。

**输入与签名**

```python
def get_settings() -> Settings
```

装饰器/挂载：

```python
@lru_cache
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return Settings()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Settings
```
