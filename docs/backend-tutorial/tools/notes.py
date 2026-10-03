"""Human-written explanations; build.py rejects any uncovered definition."""

NOTES = {}


def put(path, text):
    entries = NOTES.setdefault(path, {})
    for line in text.strip().splitlines():
        name, explanation = line.strip().split("|", 1)
        if name in entries:
            raise ValueError(f"Duplicate explanation: {path}::{name}")
        entries[name] = explanation


put("main.py", """
create_app|应用组装入口，接收可选 Settings，校验生产密钥后创建 FastAPI、异常处理、中间件、业务路由和头像静态挂载。返回应用对象；这一步会创建头像目录，但数据库/Redis 的运行资源在 lifespan 中准备。
create_app.lifespan|ASGI 启停上下文：没有注入 factory 才创建 engine，初始化 Redis/向量/用量，播种定价并按条件开清理任务。yield 后按顺序等待后台任务、关闭各资源，只 dispose 自己创建的 engine；不要把构造 app 与执行这段生命周期混淆。
""")
put("app/config.py", """
Settings.validate_security|仅在 production 检查 JWT secret 不是开发默认值且长度至少 16。失败直接 RuntimeError 阻止应用构造；不验证 SMTP、数据库连通性或全部生产安全项。
get_settings|读取 BaseSettings 并由 lru_cache 保存结果，供不通过 request 注入的模块共享。环境变化不会自动刷新缓存，测试使用 cache_clear 隔离。
""")
put("app/db/database.py", """
build_database_url|用 SQLAlchemy URL.create 把配置拼成 mysql+aiomysql URL，正确表达密码特殊字符。返回结构化 URL，不连接数据库，也不要把含密码的渲染结果写入公开日志。
create_database_engine|从 settings 创建异步 engine，开启连接检查与 1800 秒回收。engine 是连接资源管理器，不等于一次业务事务；最终由生命周期 dispose。
create_session_factory|创建绑定 engine 的 async_sessionmaker，expire_on_commit=False 使已加载属性提交后仍可读。返回会话工厂，不是共享一个会话给所有请求。
get_db_session|FastAPI 依赖用 yield 暂借独立 AsyncSession，路由正常结束后 commit，异常 rollback 后继续抛出。普通 service 的 flush 不提交，靠这一层完成事务；流生成器和工具另开自己的会话。
check_database|在两秒内开连接执行 SELECT 1，成功 True，SQL/超时/系统连接异常 False。只做数据库探针，不执行迁移。
""")
put("app/db/redis_client.py", """
set_redis|替换模块持有的 Redis 实例，测试用 FakeRedis。是进程级状态替换，不是给 Redis 写业务键。
get_redis|返回已经初始化的客户端，未准备好则 RuntimeError。这样业务不会拿到 None 后悄悄丢操作。
create_redis_client|根据 host/port/db 建异步 Redis 客户端，decode_responses=True 让命令返回字符串。连通验证在初始化或探针，不在这个构造函数内。
init_redis|复用注入实例或新建客户端，并通过 ping 验证。应用启动调用；初始化错误可阻止正常启动，不等于聊天缓存的容错读写。
close_redis|关闭当前 Redis 客户端并清理模块引用。由生命周期调用，避免连接跨测试或跨运行残留。
check_redis|两秒内 ping，成功返回 True，失败 False。为 ready 探针服务，不检查每种 Redis 数据结构是否完整。
""")
put("app/core/success_response.py", """
success_response|把业务 data、message、code 等放入统一成功信封并生成 request_id。只负责输出形状，不提交数据库，也不把这个 ID 自动传给所有模型调用。
""")
put("app/core/failed_response.py", """
BusinessError.__init__|把业务 code、可选 message/detail 与 HTTP 状态存到异常实例，并选取默认错误文案。它是可被统一 handler 识别的信号，不是直接返回给浏览器的 Response。
failed_response|构造带 code/message/detail/request_id 的普通字典。HTTP 状态由 handler 或中间件的 JSONResponse 决定，本函数本身不创建 Response。
""")
put("app/core/exception_handlers.py", """
register_exception_handlers|向指定 FastAPI 应用登记业务、请求校验和兜底异常处理器。函数本身完成注册，内层 handler 在未来请求失败时才执行。
register_exception_handlers.business_error_handler|读取 BusinessError 携带的状态、code 和 detail，交给 failed_response。保留业务可识别原因，不将所有失败都变成 500。
register_exception_handlers.validation_error_handler|把 FastAPI/Pydantic 的参数验证异常格式化为统一失败响应。发生于路由业务逻辑之前，不能当作数据库约束错误。
register_exception_handlers.general_exception_handler|记录未处理异常并返回通用服务端失败信封。避免把完整堆栈直接作为用户响应；事务回滚仍由拥有事务的代码负责。
""")
put("app/core/after_commit.py", """
defer_after_commit|将异步工作工厂放到 session.info 的字典，以 key 去重覆盖。现在只登记，不立即调用；用于避免 SQL 回滚后却已经同步向量。
_committed|SQLAlchemy after_commit 监听器取出登记的工厂，交给后台 task runner。任务在进程内运行，提交 SQL 与派发任务之间不是持久化 Outbox 协议。
_rolled_back|after_rollback 监听器丢弃待派发工作，保证失败事务不执行这些后续动作。不会撤销此前已完成的外部动作。
""")
put("app/core/task_runner.py", """
spawn_background_task|接收返回 awaitable 的 factory，创建并跟踪 task；同 key 关联前一个 task，以便顺序执行。返回任务对象，异常由内部记录；不提供跨进程或重启恢复。
spawn_background_task.run|有前驱时用 shield 等待其结束，再执行当前 factory；普通前驱异常不会阻止新工作。捕获并记录当前工作异常，不把后台失败反向抛到已完成请求。
spawn_background_task.finished|任务完成回调，从跟踪集合移除引用；只有 key 仍指向该任务才删除 key。防止旧任务完成时误删后来任务的登记。
drain_background_tasks|限时等待当前任务集合，然后取消还没结束的项并 gather 回收异常。应用退出和测试结束使用；不保证所有任务一定在关机前成功完成。
""")
put("app/core/rate_limit.py", """
endpoint_limit_for|根据 URL 前缀决定接口窗口配额，认证、聊天和普通接口限制不同。返回数值供计数检查，并不是路由注册函数。
identity_for|尝试把合法 access JWT 解析成用户标识，否则按客户端 IP 标识匿名请求。SSE type 不算 access，限流身份与实际聊天鉴权是两段逻辑。
_hit|对一个 Redis key INCR，首次设置 window+1 秒 TTL，返回整数计数。limit 参数在此未用于比较，超限判断在上层；INCR 与 EXPIRE 不是一条原子脚本。
check_rate_limit|组织用户/IP 的全局和接口计数，超额抛业务限制错误。一个请求可能涉及多个计数键，不能理解为一条原子多键命令。
check_named_limit|给特定业务动作建立独立窗口计数，例如彻底删除。路由决定是否调用，不替代通用中间件额度。
RateLimitMiddleware.dispatch|请求进入路由前按开关/路径/身份检查限流，错误转为统一响应，否则 call_next。关闭限流不会跳过路由自己的鉴权。
""")
put("app/core/scheduler.py", """
_run_cleanup|为一次清理创建 SQL engine/session，调用传入清理函数，提交成功结果，异常回滚并记录，最后释放资源。是定时任务事务包装器，不复用某个 HTTP 请求的会话。
cleanup_expired_notes|调度器的笔记清理入口，把 note service 的过期删除交给统一包装器。不要与同名 service 函数混淆：这里负责调度适配。
cleanup_expired_categories|调度器的分类清理入口，委托 category service 执行业务删除。删除规则在 service，资源/事务在包装器。
init_scheduler|为模块已构造的 scheduler 登记每日 03:00 笔记、03:30 分类清理并启动，运行中则返回。由 lifespan 在非 reload、非 test 时调用，不是所有 import 都启动调度。
shutdown_scheduler|scheduler 正在运行时调用 shutdown(wait=False) 并记录日志。没有清空模块引用，也不是清空回收站的命令。
""")
put("app/utils/auth_utils.py", """
hash_password|对明文 UTF-8 密码使用 bcrypt 自动盐生成哈希字符串。返回值可落 User.password，不能由此还原原密码。
verify_password|比较明文与 bcrypt 哈希，格式非法的 ValueError 视为不匹配。调用者据此处理失败计数，本函数不查用户、不修改 Redis。
validate_password_strength|检查至少八位，同时有字母和数字，返回布尔值与失败原因。它只是当前项目策略，不是所有强密码条件的证明。
_create_token|按用户、type 和寿命创建带 sub/iat/exp/jti 的签名 JWT，配置决定算法和密钥。返回字符串，白名单登记由调用者另做。
create_access_token|以 access 类型和分钟寿命调用底层签发器。短期访问身份检查还需黑名单，不是只要签名对就永远可用。
create_refresh_token|生成 refresh JWT 并解码取 jti，返回二元组供路由登记白名单。签发本身不使该 refresh 自动进入 Redis。
decode_token|用配置算法验证 JWT 与过期时间，分别把过期和非法转换为 401 业务错误。这里不判断 access/refresh/sse 业务类型，也不检查白名单。
_attempts_key|把用户名编码进登录失败计数键。锁定是用户名级状态，不是当前浏览器私有计数。
check_login_attempts|读取失败次数，达到五次即抛锁定错误，路由会在查密码前调用。正确密码也不能绕过仍有效的计数窗口。
record_login_failure|INCR 用户失败计数，第一次失败设置 900 秒 TTL。后续失败不在此每次重新开始整个窗口。
clear_login_attempts|登录成功后删除用户名失败计数。只清此项，不撤销其他设备或其他安全状态。
_refresh_key|把 user_id 与 refresh jti 组成白名单键。不同用户、不同 refresh 各有独立记录。
_refresh_ttl_seconds|将配置中的 refresh 天数换算成秒。白名单与设备状态使用这个 TTL，而不是 access 的分钟寿命。
store_refresh_token|以 TTL 写入 refresh 白名单，值为存在性标记。只有登记的票才能通过刷新路由的后续检查。
verify_refresh_token|读取指定用户/jti 白名单是否存在并返回 bool。JWT 签名和类型需在调用它之前另行验证。
revoke_refresh_token|删除单枚 refresh 白名单，轮换/注销时调用。不会自动删除对应 access 黑名单之外的所有访问凭证。
revoke_all_refresh_tokens|SCAN 当前用户所有 refresh 键并删除，再清理设备会话。是撤销刷新能力，不是枚举所有已发 access 并拉黑。
_blacklist_key|以 access jti 组成黑名单键。和按 user_id 组织的 refresh 白名单用途相反。
blacklist_access_token|剩余寿命大于零时写黑名单并设置剩余 TTL，已过期则不再写。只撤销传入 jti 的 access。
is_token_blacklisted|查询 access jti 是否在黑名单，返回布尔值。不存在表示没有被此机制撤销，不表示 Token 的其他条件都合法。
get_current_token_payload|解析 Authorization 的 Bearer 格式，校验签名/过期/access 类型/黑名单，返回完整 payload。是普通受保护接口共用的 Depends。
get_current_user_id|从已验证 payload 取 sub，缺失抛 401，返回可信用户 ID。业务查询用这个 ID 做所有权过滤。
create_sse_token|签发 type=sse、60 秒 JWT，并将其 jti->用户写入 Redis。只有聊天鉴权依赖消费它，不是普通用户资料凭证。
get_chat_user_id|允许正常 access，或对 sse JWT 用 Redis GETDEL 单次消费并比对 owner。重复使用或 Redis 条目失效即拒绝；不会因它叫 SSE 就从任意 URL 参数读 token。
remaining_ttl_seconds|用 payload.exp 减当前时间得到剩余秒数，供 access 黑名单设置过期。可能为非正数，写入函数会处理。
_session_key|组合用户和 device_id 为设备 Hash 的键。设备 ID 与 refresh jti 分开，设备 Hash 内保存当前 refresh jti。
_sessions_set_key|生成用户设备 ID 集合的键，用于列举与限制设备数。集合成员过期不会自动随独立 Hash 消失，列表函数会清残留。
parse_device_name|按 User-Agent 字串识别系统/浏览器并拼可读名称，未知值返回兜底。是简单启发式，不是可信设备指纹。
_client_ip|优先读 X-Forwarded-For 首项，回退 request.client.host，无请求返回空。反向代理头是否可信需由部署边界约束。
store_device_session|写设备 Hash 的 jti、名称、IP、UA、时间并刷新 TTL，同时加入用户设备集合。同设备已有 created_at 会保留，不把每次登录都算新设备创建。
get_device_session|读取单设备 Hash 并输出允许的字段，缺失返回 None。它本身不校验 JWT，由路由传入可信 user_id。
update_device_session|已有设备才更新新 refresh jti、last_used/IP，并刷新 Hash 和集合 TTL。不存在则不创建新的设备记录。
delete_device_session|删除单设备 Hash 与用户集合成员。撤销 refresh 是调用者的配套动作，不能仅删设备展示就以为刷新票也撤销。
list_user_sessions|遍历用户设备集合，删掉 Hash 已过期的成员，标出 current_device_id，按最近使用倒序返回。输出不暴露 refresh jti。
enforce_session_limit|超限时按 created_at 升序找到最旧设备，撤销其 refresh 并删 Hash/集合成员。不是按 last_used 做 LRU。
_clear_all_device_sessions|删当前用户所有设备 Hash，最后删设备集合。由全量 refresh 撤销联动调用，不涉及 SQL 用户记录。
""")
put("app/utils/file_handler.py", """
infer_mime|优先使用客户端声明的 MIME，未声明才按扩展名映射，.markdown 归一为 .md。只是元数据描述，不能据此证明文件真实内容。
calculate_md5_bytes|为已读取字节生成 MD5 摘要，上传用来检查同用户重复文件。不是安全密码哈希，也不是用户权限凭证。
validate_upload_file|校验上传长度和支持扩展名，返回规范化 .pdf/.md/.txt。异常在流开始前可作为普通业务错误返回。
read_upload_limited|分块读取 UploadFile，累计超过上限立即报错，最终返回 bytes。限制内仍会积累完整内容，不是磁盘流式零内存上传。
get_safe_filename|取文件 basename，替换残留分隔符并删除空字节，空名返回 unnamed。随机前缀由 knowledge service 另加，这个函数不生成随机名称。
ensure_dir|确保目录存在，允许已有目录。是文件系统副作用，不属于数据库回滚范围。
_match_magic|比较允许的图片文件头特征，辅助头像格式检查。只做签名字节检查，不完成完整图片解码。
validate_avatar_file|结合大小、扩展名和 magic bytes 检查头像并返回规范扩展名。不等于恶意内容扫描或重新编码图片。
""")
put("app/services/email_service.py", """
smtp_available|有注入发信函数即 True，否则检查 SMTP host/username/password。配置齐不表示连接成功，也不保证真实依赖安装齐。
generate_code|产生六位数字验证码。实现使用 random.randint，教程不把它称为密码学安全随机数。
_build_message|用 MIMEMultipart 构造文本/可选 HTML/附件层级，设置发件人与收件人等头。返回 MIME 对象，实际网络发送在 send_email。
send_email|优先使用测试注入，否则根据设置通过 aiosmtplib 发 SMTP 邮件；连接类错误按代码重试，认证失败不重试。邮件一旦发送不能靠 SQL rollback 撤回。
_render_verification_html|读取验证码邮件模板并替换指定占位符，提供邮件 HTML。不是执行完整模板语言；找不到模板时按代码兜底。
send_verification_code|先检查 SMTP 可用，生成 code 并写 Redis 300 秒 TTL，再渲染和发送邮件，返回 code。发送失败时这个已写验证码不会在本函数自动撤回。
verify_code|比较 Redis 验证码，正确即消费并清错误计数；错误累计并在阈值后删 code。返回 bool，不替用户完成注册或改邮箱。
enforce_send_code_limits|检查邮箱发送冷却和 IP 小时额度，超限抛 BusinessError。是发送验证码专属约束，不等于普通路由限流。
mark_send_code_cooldown|发送成功后给邮箱设置短期冷却标记。分离这个动作使失败发送不会被当作成功冷却。
note_attachment|按请求 format 把笔记标题正文编码为邮件附件，返回文件名/内容/类型数据。只组附件，不发信、不改笔记。
""")
put("app/services/note_service.py", """
_not_found|生成统一笔记不存在业务错误，供权限/删除状态过滤失败时使用。避免通过不同响应泄露别人的笔记是否存在。
_escape_like|转义 LIKE 特殊符号，使关键词中的百分号和下划线按字面匹配。它不是 SQL 拼接安全的唯一措施，查询仍使用参数绑定。
index_note|先删旧 note 向量，把标题与正文拼接后检查是否为空，非空则切片写 notes collection 和归属 metadata。有标题而正文为空仍可索引；删除与 upsert 非原子，出错可能暂时缺索引。
drop_note_vectors|按 note_id 从 notes collection 删除相关切片。只改变向量库，不物理删除 SQL 笔记。
_try_index|在索引调用外捕获并记录异常，使派生搜索故障不反向破坏笔记业务提交。失败不等于已经安排持久化重试。
defer_note_index|取会话绑定工厂和笔记身份，向 after_commit 登记同笔记工作。现在不读写 Chroma，避免事务回滚仍留下向量。
defer_note_index.sync_latest|提交后用新 session 重读当前 SQL 笔记；缺失/删除就清向量，否则索引最新内容。同 key 串行配合重读，减少旧任务覆盖新内容，但仅限本进程。
ensure_category|按 ID、当前用户和未删除状态确认分类可挂载，失败抛业务错误。无分类时由调用者跳过此检查，本函数不会把空 ID 当成有效分类。
create_note|验证分类、创建 Note、flush/refresh，再确保回顾记录并登记提交后索引。返回实体，普通路由的 commit 在外层。
get_active_note|按 note_id/user_id/deleted_at 查询当前用户活跃笔记，缺失抛统一错误。是读取、修改、邮件导出和工具复用的权限关口。
list_notes|组合分类/未分类/关键词过滤与分页，置顶优先，再按时间等规则排序，返回列表和总数。使用 SQL 元数据，不是语义向量搜索。
_note_hit|把 Note 包装成关键词搜索结果中的 note 摘要与 score。score 是展示排序值，不是统一语义相关概率。
_like_search|分别优先匹配标题再补正文，转义关键词并去重、限 top_k。标题和正文采用不同固定分值用于排序。
keyword_search|整理 query，适用时尝试 MySQL FULLTEXT ngram，异常或不可用退回 LIKE。返回搜索响应字典；迁移 HEAD 不一定保有 FULLTEXT 索引。
update_note|移除 format，处理显式字段并检查分类，flush/refresh；传入 title/content 字段就登记索引，并不比较新旧值是否相等。category_id 的 null 表示解绑。
soft_delete_note|加载活跃笔记并设置 deleted_at，安排提交后移除向量。SQL 正文仍保留供回收站恢复。
list_recycle_bin|列出当前用户软删笔记和剩余保留天数。不会自动执行物理清理，过期删除另有任务。
move_note|复用更新流程把 category_id 改为目标或 None。分类元数据改变不重新嵌入正文。
batch_notes|按 operation 对每个 ID 执行软删、恢复、永久删、移动或置顶，捕获 BusinessError 记录逐项结果。没有单项 savepoint，不应宣称所有数据库异常都可局部隔离。
cleanup_expired_notes|筛选早于阈值的已删除笔记，物理移除并安排向量清理，返回数量。调用者负责提交；阈值基于 deleted_at 而不是 created_at。
restore_note|只加载当前用户已删除笔记，清 deleted_at 并安排重新索引。活跃笔记调用恢复会按不存在处理。
permanent_delete_note|按用户定位笔记后物理删除并安排清向量。当前并不要求先在回收站，删除后不能靠 restore 找回。
""")
put("app/services/category_service.py", """
seed_template_tree|遍历默认分类模板，为新用户递归创建分类。与 User 使用同一 SQL session，注册失败时一起回滚。
seed_template_tree._seed|递归处理一个模板节点，生成 ID、写 parent_id/排序等，再处理孩子。是播种细节，不负责单独 commit。
_not_found|构造分类不存在的统一业务异常。用于隐藏无权访问与不存在之间的差异。
_load_active|一次读取当前用户全部未删除分类并形成按 ID 索引，供树计算。避免深度检查每走一层都发 SQL。
_depth_of|沿父链计算节点深度，根为一层。创建/移动用它结合子树高度判断三层限制。
_subtree_height|递归计算指定节点向下的最大层数，单节点为一。移动限制考虑整棵子树，而不只考虑根节点。
_is_descendant|从节点沿祖先关系判断是否位于目标祖先之下。用于阻止移动成环和非法合并。
_assert_same_name_free|检查同用户、同父级活跃分类中是否已有名称，可排除自己。是应用级唯一性检查，非数据库唯一约束替代品。
_next_sort_order|读取同级最大排序号并加一，给新节点找位置。当前 max=0 会被 or -1 当作空，排序边界见第 11 章。
_to_dict|把分类实体、直属笔记数和孩子转换为树节点字典。主要是响应数据塑形，不修改实体。
get_category_tree|加载活跃分类、统计每类直属活跃笔记数，再按父级递归构建有序树。返回树列表，不把后代笔记数混成直属数。
get_category_tree.build|从 parent_id 对应节点组排序，递归把每个孩子填入 children。服务于树响应，不额外产生数据库事务。
get_category_dict|读取单个当前用户活跃分类并计算直属笔记数，供写操作后回显。其 children 表现不等于重新查询整个树。
create_category|校验父分类、同级名称和三层限制，设置排序并写实体。返回 ORM 对象，外层事务统一提交。
update_category|更新分类名称/颜色/图标等，名称改变时检查同级冲突。不会借重命名自动移动子树。
move_category|验证新父节点归属、拒绝自己/后代环，检查移动后子树高度和同名冲突，再更新父级与排序。整棵子树关系由 parent_id 链继承。
_load_deleted|读取当前用户回收站中的分类集合，供恢复与数量计算。与 _load_active 的选择条件相反。
_promote_active_children|物理删父分类前把仍活跃的直接孩子升为顶级，避免数据库 CASCADE 把它们一起删掉。不会恢复其他已删除孩子。
soft_delete_category|将活跃孩子提升到被删分类的父级，把直属笔记设为未分类，再标 deleted_at。返回影响数量，不是递归删除整树。
restore_category|恢复当前用户目标分类，同时补回已删除祖先链并收集可恢复已删后代。已经提升的活跃孩子和解绑笔记不重新挂回。
restore_category.collect_deleted_children|在已删节点集合中递归收集目标的后代，供一次恢复处理。不会凭空推断删除前已改变的活跃树关系。
permanent_delete_category|要求目标为本用户已删分类，先保护活跃孩子再物理删除。关联已删后代可被 FK 级联删除，操作不可用普通恢复撤销。
list_recycle_bin|返回软删分类及后代数量、剩余保留时间等展示信息。统计不是执行恢复或清理。
list_recycle_bin.count_descendants|在已删除关系中递归计算某回收站节点的后代数。是展示计数辅助函数，不操作数据库状态。
reorder_categories|确认给定排序 ID 集合对应指定父级的分类，按位置更新 sort_order。当前 set 比较不能替代显式重复 ID 检查。
merge_categories|检查来源/目标关系、深度等条件，迁移笔记与孩子到目标并软删来源。写同一 SQL 事务，但不是保留完整历史的可逆合并。
cleanup_expired_categories|筛选超保留期回收站分类，保护活跃孩子并删除，返回处理数量。由调度包装器提交，不按活跃分类年龄删除。
""")
put("app/services/note_template_service.py", """
_not_found|统一模板不存在/无权访问的业务错误。避免根据 ID 读到其他用户模板。
body_from_structure|按 markdown/content/body 顺序找可用字符串正文，否则返回空。模板结构是 JSON，不自动执行其中代码或完整模板语言。
create_template|按 Schema 数据创建当前用户模板，flush/refresh 后返回实体。模板 category 是文字分类，不是 NoteCategory 外键。
list_templates|查询当前用户全部模板，按 sort_order 升序、创建时间倒序返回实体列表，当前没有分类筛选参数。只读骨架，不创建笔记或修改已应用的正文。
get_template|按模板 ID 与用户定位单项，缺失抛业务异常。应用模板与更新删除都复用这个权限入口。
update_template|加载有权限模板后仅更新给定字段并刷新。修改模板不会反向修改已生成笔记。
delete_template|加载当前用户模板并删除 SQL 实体。已用模板创建的笔记独立存在。
apply_template|取模板正文与默认/覆盖标题，组 NoteCreate 并委托普通笔记创建。复用回顾记录和提交后向量索引，而非直接绕过 service 写表。
""")
put("app/services/note_ai_service.py", """
_clip|按上限截取输入文本，为模型提示控制长度。只截字符串，不按 Token 精确预算。
build_autocomplete_prompt|用光标位置分割正文，截前文/后文并约束只续写。当前前文取切片前 1200 字，不一定是离光标最近的末尾 1200。
build_write_prompt|按 continue/expand/summary 模式生成写作要求，并限制输入正文长度。返回 prompt，不调用模型。
build_tag_prompt|把标题和正文放入标签建议提示，要求有限数量短标签。最终格式仍需 parse_tags 校验。
parse_tags|解析模型返回的 JSON/分隔文本，去空、大小写去重并限制数量和长度。返回建议数组，不写 Note.tags。
_complete|优先注入写作模型，再用配置 API，记录耗时/用量；缺 key 或失败返回空。容错是建议为空，不是自动离线生成。
autocomplete|构造光标补全提示并调用 _complete，返回续写文字。不会修改数据库正文。
write_assist|根据模式构造提示并返回写作结果。接受结果需要调用普通笔记更新。
suggest_tags|发标签提示后调用 parse_tags 得到干净标签列表。建议与保存分离，失败可为空列表。
""")
put("app/services/review_service.py", """
next_interval|在固定间隔表中前进一档，未知当前间隔回到一日，末档按实现封顶。quality 不参与计算，不是自适应 SM-2。
_not_found|创建回顾记录不存在/无权访问业务异常。供按用户检查失败统一使用。
_dump|把 ReviewRecord 与关联笔记转换为响应字典。关联的 note 标题正文用于学习展示，不改复习状态。
ensure_review_record|对笔记查已有记录，有则返回，无则创建初始 interval=1 的到期记录。创建笔记因此能进入今日待回顾。
get_today_reviews|查询当前用户活跃笔记中已经到期的回顾记录并整理结果。不会自动标记这些项完成。
mark_reviewed|校验当前用户记录，写 review_count/quality/reviewed_at 并计算 next_review。初始一日间隔首次完成进入两日，提交由调用方负责。
get_review_stats|按记录当前状态统计学习情况与连续性。每笔记只保留最新 reviewed_at，不是全量历史事件表。
format_today_reviews_text|复用今日查询并转为 Agent 可读列表，保留回顾/笔记身份信息。只读适配，方便下一步标记真实 review_id。
complete_review_text|复用 mark_reviewed 完成指定记录并返回下次日期文字。工具外层还需 commit，字符串本身不替代事务提交。
""")
put("app/services/knowledge_service.py", """
sse_event|将字典编码成 data: JSON 加空行的 SSE 帧，类别在 JSON.event_type 中，不是 event: 行。只做编码，不意味着 SQL 已提交。
_processing|统一生成含当前处理步骤/进度信息的 processing 事件。上传 service 在各阶段调用，便于流消费者观察。
_doc_type|把规范扩展名映射为文档类型。后续解析和模型字段使用这个类型，不从正文猜测业务分类。
find_duplicate|按用户与文件 MD5 查重复上传记录。不同用户可有相同文件，摘要本身不代替所有权。
_index_chunks|把切片与文档/user/章节/序号 metadata、稳定 ID 组装后交给向量库。写 Chroma 与 SQL 事务不是同一个提交。
iter_save_document|按落盘、解析、切片、建文档记录、写向量顺序 yield 进度，最后 completed。外层路由才 commit；解析/索引异常有清理逻辑，但不等于所有取消/提交失败都跨介质回滚。
list_documents|按用户筛选文档记录并按创建时间倒序返回 documents/total，当前没有分页参数。读 SQL 元数据，不把 Chroma 切片当上传列表。
get_document|按文档 ID 与当前用户查实体，不存在返回统一业务错误。删除等动作先经此权限检查。
delete_document|确认文档归属，删除关联向量和原文件并删除 SQL 实体。文件/向量删除无法由 SQL rollback 自动恢复。
search_documents|直接查询用户知识库向量并整理搜索响应。知识库搜索不使用聊天 RAG 门控和检索后摘要。
""")
put("app/services/chat_service.py", """
_session_dump|通过 ChatSessionResponse 把 ORM 会话变成可 JSON 输出字典。隐藏 ORM 内部状态，供缓存/HTTP/meta 使用。
_message_dump|通过 ChatMessageResponse 序列化消息并处理时间字段。幂等键等内部字段是否暴露取决于该响应 Schema。
_cache_on|读 settings.chat_cache_enabled，无 settings 则默认开启。是兼容调用配置选择，不触发缓存读写。
_cache_buffer|返回 settings 的热消息条数或模块默认条数。这个数只约束热窗口，不约束新主链 SQL 记忆。
_cache_ttl|返回会话列表 TTL 配置或默认值。不要把它误用于消息 Token 寿命。
list_sessions|优先读当前用户列表缓存，miss 查询 SQL 按更新时间排序并回填。缓存失败不等于会话丢失。
get_session|用 session_id 和 user_id 校验会话归属，失败抛 SESSION_NOT_FOUND。新旧聊天、改名、删除和消息列表共用。
create_session|创建会话并 flush/refresh，按开关使用户列表缓存失效。返回实体不 commit，新主链传 uncached 避免提前缓存变更。
update_session_title|校验归属后写标题和 title_manual=True，刷新并失效缓存。手动标记用于阻止后台模型覆盖。
delete_session|查权限后删除会话并 flush，再清列表与消息缓存。SQL 关联删除行为由 ORM/FK 定义，缓存操作本身不在 SQL 事务内。
list_messages|先验证会话用户，再从 SQL 按时间/ID 返回完整消息。不是只返回 Redis 最近 N 条。
_add_message|添加 ChatMessage、flush/refresh，可按开关提前推热缓存；不 commit。新 query 特意传关闭缓存 settings，在自身 commit 后再缓存。
""")
put("app/services/query_service.py", """
_sse_data|把包含 type 的 payload 编成 data: JSON 帧，供当前聊天使用。事件类别在 JSON 内，而不是单独的 event 行；这里只编码，不保存消息。
compose_answer|生成无模型时的本地降级回答，分别处理跳过检索、检索无结果、知识库或笔记命中。保留资料编号和来源，不宣称整个项目没有模型能力。
_key|空幂等 key 返回 None，否则哈希 user_id、角色和客户端 key。保证两用户及 user/assistant 的消息键分开，但不包含 session_id。
_load_memory|用独立 SQL session 查当前消息 ID 之前的本会话全量消息，连同摘要文字和覆盖到的 ID 返回。新链不先用 Redis 热窗口截断。
_retrieve|给 RAG 总流程套超时：门控、可选聊天 HyDE、双源检索、摘要；返回原 hits/提示副本/决策。普通错误或超时记录日志并返回 unavailable，不阻断后续 Agent。
_update_title|读会话手动标记和用户轮次数，早期轮次才生成标题，再用非手动且旧标题相等的条件 UPDATE 提交。模型等待期间不占同一个会话对象，防止慢模型覆盖人工改名。
_summarize|新建 SQL session，调用里程碑摘要检查并 commit。由后台任务执行，不让 done 等它完成。
stream_query|当前聊天总编排：SSE 槽、防重、用户先提交、并行 RAG/SQL 历史、预算、图执行、事件追加/替换、助手提交、后台维护后 done。error 终止不写假成功回答，finally 清 trace/释放槽；副作用不在一个总 SQL 事务里。
""")
put("app/services/usage_service.py", """
set_session_factory|设置独立用量写入的会话工厂，应用启动注入、退出清空。没有 factory 时记录函数跳过，不复用聊天事务。
set_trace_context|为当前异步上下文放入 request/user/session/stage，未给 request_id 则生成短 ID。它与 HTTP 响应辅助函数的 ID 不是自动相同。
clear_trace_context|将当前 ContextVar 清为 None，避免后续同上下文误归属用户。不会删除已落库 trace。
set_trace_stage|若已有上下文，复制字典并写新 stage。复制使并行任务继承后的 stage 修改不互相污染。
get_trace_context|返回当前上下文的计量归属信息或 None。不是全进程唯一的正在聊天用户。
estimate_tokens|以字符数约两字一个 Token 向上估计，空字符串返回零。用于缺官方 usage 的粗略计量，不是精确 tokenizer。
parse_usage|优先取响应 usage 的 prompt/completion/total，字段缺失才用文本估算。显式零值必须保留，不能用 truthy 判断把零替换为估算。
record_usage|合并显式参数和 ContextVar，建立 ModelTrace 并用独立 session commit；缺用户/factory 则跳过，落库失败仅日志。保存计数与结果，不是存完整对话审计。
record_text_call|把 prompt/completion 与供应商 payload 转计数，再委托 record_usage。调用阶段和模型由调用者明确传入。
UsageTimer.__init__|记录 stage、model 和 perf_counter 起点，供一次调用计时。构造时不写 SQL。
UsageTimer.latency_ms|用当前高精度时钟减起点并转毫秒。它测包装范围总耗时，不一定是供应商纯推理时间。
UsageTimer.finish|把文本、usage、成败和当前耗时传给 record_text_call。一次调用完成或失败路径使用，不能无意重复 finish 造成重复记录。
seed_model_pricing|从项目种子与当前模型补充价格，查询已有行并更新或新增。是本地配置数据，会覆盖已有种子模型价格，不是查询实时官方价格。
get_usage_summary|按用户、时间窗和可选会话聚合总量、stage/model、平均时延并结合价格估费用。未知价格为零，本地费用不是供应商账单。
""")
put("app/rag/chat_cache.py", """
sessions_key|生成按用户隔离的聊天会话列表 key。列表缓存不会把全部用户放在同一值内。
messages_key|生成按会话组织的热消息 List key。调用者要先校验会话归属，key 本身不是权限检查。
_dumps|把缓存值编码为保留中文的 JSON，非原生 JSON 对象用 str 兜底。用于存储，不保证任意对象可还原为原类型。
_loads|将 Redis 字符串解为 JSON 值。缓存入口负责捕获坏值异常并回退 SQL。
dump_message|兼容实体/字典抽出消息身份、角色、正文与时间。给消息热缓存保存可还原的 JSON 字段，不把 ORM 内部状态写入 Redis。
get_session_list|GET 并解列表，缺失/类型不对/异常均返回 None 表示 miss。空列表是合法命中，不要当故障。
set_session_list|将列表 JSON 写入 Redis 并设最少一秒 TTL，失败仅日志。SQL 事实不因缓存不可写而消失。
invalidate_session_list|删除某用户列表缓存，下次读从 SQL 重建。是失效动作，不删除会话。
get_recent_messages|LRANGE 取全部热列表，反转成旧到新；空或异常返回 None。内部 List 最新在前，外部使用时间正序。
push_message|序列化消息后 LPUSH，并 LTRIM 保留 buffer_size。这里没有设置消息 List TTL，别把会话列表 TTL 自动套到它。
rebuild_messages|清原 List，从输入正序消息取最近 N 条，逐个 LPUSH 重建最新在前结构。读回来再反转，必须保持这一组顺序约定。
delete_messages|删会话的热消息键，失败只记日志。会话 SQL 删除由 service 负责。
""")
put("app/rag/chat_history.py", """
_role_and_content|从字典或对象统一取得 role/content，缺字段用空。当前历史选择据此保留用户/助手角色，而不是先格式化为一段历史字符串。
rag_context_text|抽出非空 hit.content 并换行连接，生成预算和提示用的参考文本。不是把全部 metadata 都送模型。
build_agent_history|新主链排除已摘要 ID，保留 user/assistant 原角色，扣问题/摘要/RAG/工具预留后从新往旧取历史。单条超大时逐步缩短，legacy scratchpad<=0 自动预留 4000，不受旧热窗口限制。
""")
put("app/rag/document_parser.py", """
parse_document|按类型选择 TXT/MD 的 UTF-8 容错读取或 PDF 提取，并把读取异常转业务错误。返回纯文本，不生成向量。
_parse_pdf|使用 pypdf 逐页提取可读文本并合并。扫描图片无文字层时不会自动 OCR，空提取需由后续处理。
""")
put("app/rag/embeddings.py", """
reset_embedding_cache|清进程内 embedding LRU 缓存，测试/切换环境使用。不会清 Chroma 已持久化向量。
hash_embed_text|把文本 token 确定性映射到指定维度槽并归一化，返回浮点列表。便于无 key 测试流程，不是真实语义模型。
hash_embed_texts|逐条调用哈希嵌入并保持输入次序，返回向量列表。不能将这批结果混入另一真实模型的语义空间。
_backend_tag|构造描述注入/API/哈希后端的缓存标签。它不是所有 endpoint 参数的完整指纹。
_cache_key|组合后端标签与文本 MD5 作为缓存 key。没有 user_id，意图是复用相同文本的向量计算。
_embedding_api_key|优先 embedding 专用 key，空时复用主 LLM key。这里只选配置，不向外输出密钥。
_embedding_base_url|优先 embedding 专用 URL，空时复用主接口 URL。专用模型与主聊天模型可以不同，但必须按配置理解实际目的地。
embed_openai_compatible|POST /embeddings，传模型和批量 input，检查响应后按 index 排序返回向量。当前未接用量落库；API 错误抛出，不静默改哈希。
_embed_batch|选择注入、配置 API 或无 key 的哈希实现并返回一批向量。选择优先级由此集中控制。
embed_texts|按输入查 TTL/LRU 缓存，收集缺项分批嵌入、回填、淘汰，并按原序返回。缓存是进程内派生结果，模型换配置仍需注意已有 Chroma 的一致性。
""")
put("app/rag/hyde.py", """
build_hyde_prompt|要求模型生成像资料陈述句的假设回答以辅助召回。该文本不作为已验证事实直接回答用户。
hyde_cache_key|用模型、用户和问题 MD5 组成 Redis key。把不同用户的假设检索缓存分开。
_cache_get|尝试读 HyDE 缓存，异常或空返回 None。缓存故障不会终止检索。
_cache_set|以 TTL 写假设文本，异常忽略。返回成功不构成 SQL 事务承诺。
generate_hyde|开关允许时先查缓存，再用注入/模型生成假设并缓存；无 key/失败/空结果回原问题。主 query 还受 chat_hyde_enabled 外层开关约束。
""")
put("app/rag/llm.py", """
complete_openai_compatible|发非流式补全请求，按协议加入 thinking 字段，提取正文并记用量，HTTP 失败抛异常。分类、计划、摘要等短任务复用，由调用方决定降级。
""")
put("app/rag/memory.py", """
truncate_summary|估 Token，超额按比例截字符并尝试在较后句号处结束。近似限制，不是反复精确 tokenizer 截到绝对上限。
format_messages_for_summary|兼容消息字典/对象，带角色标签并截每条正文后拼接。摘要模型看到的是这些裁剪后的材料，不是完整原数据库。
build_summary_prompt|把已有摘要和新的较早消息装入增量融合提示，要求保留事实/偏好/待办。返回提示，不写 ChatSummary。
get_summary|按 session_id 读取至多一条里程碑摘要实体。调用方已确保会话归属，不在这里重新解析 Token。
update_summary|存在就更新摘要、覆盖 ID、token_count 并加 version，否则新增；flush/refresh 返回实体。commit 由后台包装或旧调用方负责。
_complete_summary|给调用设置 summary 阶段，优先注入并计量，否则调用兼容模型，无 key 空结果。异常交给外层容错保留旧摘要。
check_and_summarize|检查总量/新增间隔，保留最近若干条，只压缩未摘要较早消息并更新覆盖 ID。失败返回已有摘要或 None，不应吞掉已完成问答。
""")
put("app/rag/note_cards.py", """
one_line|把摘要空白压成一行并限制长度。保证工具卡片文本不会被正文换行打乱。
format_note_search_cards|把搜索结果变成包含序号、标题、note_id、摘要的固定文本，空列表给未找到说明。保留 ID 使后续读取全文能定位真实笔记。
visible_question|移除附带的笔记引用块，得到本轮真正问题，用于标题、分类和检索。原 raw 仍可保存，不是在 SQL 中删内容。
referenced_notes_prompt|识别用户附带引用并提取适合 Agent 提示的上下文，无引用返回空。引用是上下文材料，不能代替工具所有权检查。
""")
put("app/rag/rag_route.py", """
decide_retrieval|空 query 跳过，关闭门控则检索；注入优先，否则比较当前用户双库 Top-1 距离与阈值，评分失败放行。返回 RouteDecision，不直接生成回答。
""")
put("app/rag/rag_summarize.py", """
build_summarize_prompt|组合问题与切片，要求提取能回答问题的短参考。模型可答无关，不保证结果一定有用。
truncate_text|按字符上限截取，非正上限不截。作为摘要关闭/失败的本地兜底，不是 Token 截断器。
_copy_hit|复制命中字典并只替换 content，让原始命中可供 sources。浅拷贝不递归复制嵌套对象。
_complete_summary|给调用设置 rag_summary 阶段，使用注入或兼容补全，并限制真实 API 输入切片长度。无 key 返回空，外层决定截断。
_summarize_one|处理单个 hit：空内容直接副本，关开关/空返回/异常用截断，否则用摘要。当前非空且开关开就尝试，没有先判断切片足够长。
summarize_hits|对每个 hit gather 并发摘要并按输入顺序收集副本。原始 hits 不变，便于来源展示与提示内容分开。
""")
put("app/rag/retriever.py", """
set_cross_encoder|直接注入一个有 predict/compute_score 的模型并重置失败标记。测试不下载真实权重也能验证适配路径。
reset_cross_encoder|清注入模型和加载失败状态。用于测试隔离或显式重新尝试，不删除磁盘权重。
_as_float_list|把 scalar/array/list 分数规范成浮点列表并检查条数。多文档只回一个数或长度不匹配会报错，避免错位排序。
cross_encoder_scores|把 query 与每篇正文配对，优先 model.predict，再兼容 compute_score，统一校验输出。支持不同模型库接口，不把函数名写死成其中一种。
_cached_rerank_dir|优先本地路径，再通过缓存中的 config.json 找权重目录，失败 None。这样有缓存时可避免额外 Hub 探测。
_apply_hub_offline_env|记录 Hugging Face/Transformers 原离线环境值，按请求开启离线，并返回旧值。改的是进程环境，后续必须恢复。
_restore_hub_offline_env|按旧值还原或移除离线环境变量。与加载函数 finally 配对，避免影响后续别的库调用。
_load_cross_encoder|检查当前 CrossEncoder 构造签名，选择支持的 local_files_only 参数，暂设离线变量后实例化。finally 恢复环境，不能假设所有版本关键字都一样。
get_or_load_cross_encoder|返回注入/已有模型，否则按设置与线程锁懒加载，本地优先、下载由开关控制。一次失败记标记，后续回 None 避免每请求反复加载。
tokenize|英文词小写，含中文串拆单字和双字 token。给 BM25 与词重叠用，不是外部中文分词模型。
bm25_scores|用文档频率、查询词频、长度归一与 k1/b 算每篇 BM25，空输入返回零列表。分值只用于本次语料排序。
rrf_fuse|按 chunk_id 合并多路排名，对每次出现累加 1/(k+rank)，降序并写 rrf_score/score。缺 ID 的项跳过，不直接相加原始余弦和 BM25 分。
overlap_scores|计算查询 token 被每篇正文覆盖的比例，返回逐篇数值。是无模型重排降级，不是 CrossEncoder 语义判断。
_score_hits|集中选择注入打分、真实/缓存 CrossEncoder、词覆盖率。实际模型获取失败可降级，已选打分运行失败则交给外层保持原序。
rerank_hits|为 hits 写 rerank_score/score 并排序截 top_n，打分异常或条数不匹配返回原顺序切片。正常路径会修改传入 hit 字典的分数字段。
""")
put("app/rag/session_title.py", """
build_title_prompt|要求模型依据问题生成短标题且不加说明。提示里的二十字目标不等于严格程序约束，后面还要 sanitize。
fallback_title|压平问句空白并按长度取短标题，空问题返回默认新对话。没有模型也能得到可用占位。
sanitize_title|清外层引号与空白并按 max_chars 截断，清空后回 fallback。只清标题文本，不判断是否允许覆盖数据库标题。
generate_session_title|优先注入，否则用 title 角色模型；开关关、无 key、异常都回短问句。返回文字，更新资格和竞争保护在 query_service。
""")
put("app/rag/text_splitter.py", """
TextSplitter.__init__|保存并规范 chunk_size/overlap，使窗口参数可用。数值单位是字符，不是模型 Token。
TextSplitter.split|根据文本和文档类型选择 Markdown 标题分段或普通段落分段，过滤空项并统一编号，返回 TextChunk 列表。空白资料不会凭空造切片。
TextSplitter._split_markdown|先解析标题章节，再将章节正文按通用规则切片并携带 section_title。保留章节来源而不是只按固定偏移硬切整文。
TextSplitter._parse_sections|识别一至四级 Markdown 标题，收集对应正文，返回章节序列。不是完整 Markdown AST 解析器。
TextSplitter._split_generic|按空行分段，合并可容纳短段，长段交滑窗，产出文字块。相邻短段拼成的块不保证都有 overlap。
TextSplitter._window|对长字符串按 size 与 size-overlap 步长取窗口，直到尾部。重叠主要在这里产生，不能推断全部切片有相同重叠。
""")
put("app/rag/token_budget.py", """
TokenCounter.get_encoder|按编码名缓存 tokenizer，按实现处理库/编码不可用的情况。不会每次 count 都重新初始化编码器。
TokenCounter.reset_encoders|清编码器缓存，测试可以重新验证 fallback。与 embedding 缓存是完全不同的数据。
TokenCounter.count|有编码器则按 encode 长度计数，编码器加载不可用才以字符数粗估，空文本为零。返回预算整数，不直接请求模型；encode 自身异常没有在此统一捕获。
count_message|计算单条正文及消息额外开销。历史选择把这个值累加，而不是仅按 len(content)。
""")
put("app/rag/vector_store.py", """
VectorStoreService.__init__|保存 settings 与可选 Chroma client，集合尚未获取，维度检查标记为假。注入 ephemeral client 可避免测试写正式磁盘。
VectorStoreService._ensure|懒建 PersistentClient 或复用注入实例，获取知识/笔记两个 cosine collection。名字来自配置，不按每个用户另建 collection。
VectorStoreService._collection|确保初始化后根据 rag/notes 名返回对应集合。用户隔离在查询 metadata 条件，不在此函数。
VectorStoreService._check_dimension|首次有 probe 时检查非空集合已有向量维度，不匹配抛业务错误，通过后记标记。只验维度不验同维模型语义兼容；报错建议清库不意味着教程授权删除数据。
VectorStoreService.upsert_chunks|对非空 documents 批量 embedding、维度检查，再把 ID/正文/metadata/向量写指定 collection。调用者负责 metadata 的用户归属和稳定 ID。
VectorStoreService._candidate_k|放大 top_k 并应用候选上限，至少保留请求规模。候选量不等于最终返回数量。
VectorStoreService._format_hit|统一 Chroma 结果形状，补 source、document/note ID、文件标题、章节、片序和 chunk_id。后续融合靠 chunk_id，展示靠其他 metadata。
VectorStoreService._vector_search|空 collection 返回空，否则嵌入 query、按 user_id 过滤查询，余弦距离转 1-distance 并格式化。目标 count 是全集合数量，不等于该用户命中数。
VectorStoreService._bm25_search|取当前用户最多 bm25_max_docs 文本，tokenize 后计算 BM25，过滤零分并排序截取。不是数据库 FULLTEXT 那条检索路线。
VectorStoreService._maybe_rerank|无结果直接空，允许重排且总开关启用则委托 rerank_hits，否则切 top_k。该同步函数由外层 to_thread 调度较重计算。
VectorStoreService.search|单源先扩大候选向量召回，可选 BM25+RRF，然后可选重排。返回统一 hit 列表，默认 hybrid 开关不保证已开启。
VectorStoreService.compute_route_score|只做双源当前用户 Top-1 余弦距离，取最小；空问题/无用户资料返回 inf。不经过 BM25、HyDE 或重排。
VectorStoreService.search_both|并行查 rag/notes 各两倍 top_k，按配置 RRF 或直接分数排序，再用原 rerank_query 重排。召回 query 可是 HyDE，而重排保留用户原问题。
VectorStoreService.delete_document|按 document_id 字符串删除 rag collection 所有切片。内部 ID 已经来自拥有权限的 service，不重新鉴权。
VectorStoreService.delete_note|按 note_id 清 notes collection 切片。SQL 删除与恢复由笔记 service 控制。
VectorStoreService._delete_by|按 metadata 找 ID，再批量 delete 并记录数量。无匹配不报错，方便重复清理。
set_vector_store|替换全局向量服务实例，供测试隔离或生命周期清理。不是替换 SQL session。
get_vector_store|返回已初始化服务，没有则 RuntimeError 提示生命周期未完成。业务调用应在初始化之后。
init_vector_store|已有实例直接复用，否则创建服务并缓存。并不强制立即打开两个 Chroma collection。
close_vector_store|清全局服务引用。不是删除 data/chroma，也不承诺调用所有底层 client 的持久化清理 API。
""")
put("app/ai_service/chat_graph.py", """
stream_chat_graph|构造分类->ReAct/Plan 的可取消 StateGraph，用容量 128 的队列向调用者输出事件。结束/取消时回收生产任务，避免客户端断开后继续无限生成。
stream_chat_graph.classify|对可见问题调用分类器，把路由元数据和分类说明写队列，返回 route 状态。Plan 可用性同时考虑 Agent 开关和规划配置。
stream_chat_graph.forward|在 aclosing 内消费子流并逐事件放入共享队列。队列满会等待，给图输出提供背压。
stream_chat_graph.react|优先运行配置/注入的新 ReAct；无模型而有本地工具意图则旧 runner；否则输出本地参考答案。设置 agent 计量阶段，不保证任何配置下都调用真实 LLM。
stream_chat_graph.plan|转发 Plan 事件，遇 plan_fallback 返回 route=react，否则完成状态。只由 Plan 自己判定何时降级安全，不在这里无条件重跑。
stream_chat_graph.run|后台执行编译图，普通异常转 error，非取消情况下用 sentinel 通知消费者结束。取消中避免再向满队列写结束标记导致收尾卡住。
""")
put("app/ai_service/langchain_tools.py", """
json_schema_to_model|把工具 parameters 的简单属性/required 转动态 Pydantic 参数类。只支持当前简单类型映射，不是完整 JSON Schema 验证器。
spec_to_langchain_tool|按 spec.fn 优先、绑定内置函数其次找到实现，创建 args_schema 与 StructuredTool。返回 LangChain 可调用对象，尚未执行工具。
spec_to_langchain_tool._run|删除值为 None 的可选参数，让底层 Python 默认值生效，再调用同步/异步实现；不存在实现返回未知工具文字。保留外层绑定用户，模型不提供 user_id。
build_langchain_tools|为当前用户绑定注册表工具，按组解析并在只读模式排除非 parallel_safe。返回提供给模型的工具集合，而不是所有路由都开放。
""")
put("app/ai_service/models.py", """
settings_for_role|复制 Settings，只替换角色对应 llm_model；reflection/title 有指定回退链，空值复用主模型。key/base_url 不变，所以不是多供应商独立认证。
""")
put("app/ai_service/plan_execute.py", """
plan_available|综合 plan_execute_enabled 与注入流/注入计划/真实 key 判断是否能规划。返回 bool，分类器据此决定复杂问题能否真走 Plan。
build_plan_tool_list|把注册表当前工具名称/描述转规划提示清单，并加 none 分析步骤。动态工具能进入计划，不靠另一份写死白名单。
build_plan_prompt|给问题、当前时间和工具清单，要求带 depends_on 的 JSON 步骤和真实 ID 依赖。提示不是验证，返回后仍需解析检查。
parse_plan_payload|清代码围栏并解析 JSON，构造 PlanStep，拒绝未知工具/空 action，再检查依赖图。返回 ExecutionPlan；解析失败触发运行层安全降级。
topological_batches|验证正数唯一 step ID、依赖存在，然后不断取依赖已完成的节点批次。没有可执行节点时识别环，返回拓扑层而非实际同时运行安排。
_complete|临时切换用量 stage 和角色模型，在指定 deadline 内非流式补全，finally 恢复上个 stage。避免计划补全计到别的阶段。
generate_plan|给规划总调用套 plan_timeout，优先注入 PlanFn，否则模型生成并解析。只产生计划，不调用笔记写工具。
_execute_step|先发步骤开始，拼入 depends_on 的真实结果，工具步骤交步骤 ReAct；none 做分析，最后发结束摘要。出错发 error，不编造成功；step.result 保存较完整结果用于后续依赖。
_execute_batch|为一小批创建并发步骤消费任务，通过队列转发事件，sentinel 计完成数。退出时取消未完项并 gather，防止断流留下步骤后台执行。
_execute_batch.consume|消费单个步骤的事件写队列，在 finally 放该任务的结束 sentinel。消费者由此能知道所有并发步骤是否结束。
_safe_batches|按并行上限把 readonly/none 步骤分组，非 parallel_safe 写步骤各自一批。这是拓扑层之上的执行安全划分，不是单纯所有无依赖步骤全并发。
build_synthesize_prompt|按原计划次序收集各 step.result，结合用户问题/目标要求最终答案，保留笔记 ID。失败结果不能被提示为已经成功的事实。
run_plan_execute|规划、依赖批次、步骤执行、综合、自检的总流，设置整轮 deadline。tool_start 时记可能副作用，未写失败可 fallback，写后失败只报核查错误避免重放。
run_plan|选择注入 PlanStreamer 或真实总流程，并用 aclosing 转发。注入改变执行来源，不改变调用者消费事件的接口。
""")
put("app/ai_service/query_classifier.py", """
ClassificationResult.thinking_text|根据 complexity 与实际 route 生成可读分类说明，包括复杂但 Plan 不可用。不是模型隐藏推理，只是状态文案。
decide_route|complex 且可用返回 plan_execute，complex 不可用返回 plan_pending，其余 react。图把非 plan_execute 走 react，pending 不是排队实现。
_count_tool_keywords|按关键词长度优先匹配，避免搜索笔记和搜索等包含关系重复计数。返回意图种数，供多目标规则用。
rule_classify|依次检查复杂模式、长多问句、多工具、条件分支和简单模式；无法确定返回 uncertain。只做 L1，不调用模型。
_final|统一构造 ClassificationResult 并通过 decide_route 计算路线。调用者提供来源/理由，避免不同分支漏填字段。
build_classify_prompt|截问题前 500 字，给简单/复杂例子并要求 JSON。限制输入成本，但长问题尾部可能未进入 L2。
parse_classifier_payload|容错去围栏/抽 JSON，规范 complexity 和理由，非法输出回 simple。返回的是模型来源结果，不自动证明判断正确。
_llm_classify|切 classify stage，选择 classifier 角色模型与其 thinking 开关调用补全，解析结果，finally 恢复 stage。与主对话思考开关独立。
classify_query|总分类入口：关闭则简单，注入优先，L1 确定即返回，不确定且 L2/key 可用才限时模型判断。异常回 simple，注入分支用于确定性测试。
""")
put("app/ai_service/react_agent.py", """
build_react_system_prompt|拼学习助手规则、额外步骤说明、RAG reference 与用户引用笔记。纯构造，不执行资料检索或鉴权。
chunk_text|兼容字符串 content 和文本块列表，只提取正文文本。忽略不是 text 的结构化片段。
chunk_reasoning|从 additional_kwargs 等支持字段抽 reasoning 文本。提取不到返回空，不自行推测模型推理。
map_langchain_event|将模型/工具 v2 事件转 thinking/response/tool_start/tool_end，跟踪连续工具计数和耗时。超过六次仍先产 tool_start 再 error，使上层不会漏记可能写操作。
_create_chat_model|构造流式 ChatOpenAI，启用 usage callback、超时且 SDK max_retries=0；仅支持协议才附 extra_body。不会把所有兼容网关都强行传 enable_thinking。
_create_agent|首选 langchain.agents.create_agent，ImportError 时兼容 create_react_agent。返回代理对象，工具由外层已经按权限/组筛好。
_history_messages|摘要转 SystemMessage，结构化历史的 user/assistant 转对应消息，旧字符串历史则 SystemMessage。角色保留比把所有历史塞用户消息更准确。
run_langchain_react|在整轮超时内建模型/工具/agent，消费事件并累计答案；未触碰副作用时允许一次 L2 修复，末尾可 L1 自检并替换草稿。模型/工具失败发 error，不默认无限重试。
run_react|选择注入或真实 ReAct，传用户/上下文/工具分组/只读等参数，并负责关闭下游生成器。测试注入可不需要真实模型超时参数。
""")
put("app/ai_service/reflection.py", """
parse_critique_response|清围栏、解析 pass/issues，无法解析或不通过却无修改理由都视为通过。反思是增强，不因评审格式差毁掉已有答案。
build_critique_prompt|把问题、计划目标、步骤结果与草稿放入质量评审提示，要求实质问题的 JSON。截部分输入以控制长度。
build_repair_note|生成上次工具/执行失败的短附加提示，提醒修参数或换策略而非反复试。真正能否重试仍由执行器副作用判断决定。
build_refine_prompt|给旧稿与 issues，要求输出完整修订正文。返回提示，不做局部字符串补丁。
no_retry_tools|把配置逗号分隔名称转集合，空配置使用 send_email 默认。注册表 non-parallel_safe 和未知工具也会参与执行器禁止重试。
critique_answer|优先注入，否则 reflection 角色补全并解析；没 key/异常视为通过，临时 stage 最后恢复。外层 stream 还加批判 deadline。
refine_answer|把上下文与修订提示送主配置模型，thinking 跟当前主开关，临时记 reflection 阶段。异常交外层保留草稿。
stream_l1_refine|按开关、长度与模型可用性决定是否自检，等待之前先 yield checking/refining，修订失败留原稿，最后 stream_done。它输出最终值，由上层决定 response_replace。
""")
put("app/ai_service/review_tools.py", """
get_today_reviews_tool|把当前用户与 session 交给回顾 service 的文本格式化入口。只读工具，不另造复习业务逻辑。
mark_reviewed_tool|委托 service 完成 review_id 并给出文本，真正 commit 在绑定工具闭包。review_id 来自查询结果，不该由模型杜撰。
""")
put("app/ai_service/runner.py", """
match_local_tool|按固定关键词表返回首个匹配工具名，无匹配 None。是无模型的有限意图规则，不是完整自然语言理解。
should_use_agent|Agent 关闭返回 False，有注入或本地工具关键词时才选择无模型降级。图在此之前优先判断真实模型或 ReAct 替身，不能拿这条规则替代完整图路由。
run_local_tool|绑定当前用户，根据关键词选择一个工具，发 start/end/response；异常发 tool_end error 后结束。搜索传问题，其余这组本地工具用无参调用。
run_agent|优先选择注入 runner，否则执行本地关键词工具并转发事件。没有第二套 HTTP 模型工具循环；真实模型问答统一交 LangChain ReAct。
""")
put("app/ai_service/sse_slot.py", """
acquire_sse_slot|Redis INCR 按用户检查并发上限，首次设 120 秒 TTL，超限撤回本次计数；失败退本进程字典。不是可靠长连接租约，TTL 不续期。
release_sse_slot|尝试 Redis DECR，失败则减少本地计数并防负值。依赖与申请阶段一致的后端可用状态，不是持久化资源锁。
""")
put("app/ai_service/thinking.py", """
ThinkingDecision.sse_notice|只有用户要求思考但被附件/协议关闭时生成解释事件，否则 None。文案不证明视觉模型已经实现。
thinking_protocol|按显式 none/dashscope 或 auto 的 URL 字串判断协议。auto 只识别项目支持的 DashScope 形式，不对任意网关做远端能力探测。
extra_body|协议支持才返回 enable_thinking 字典，否则 None。避免向不支持扩展的网关发送非法参数。
payload_thinking_fields|把 extra_body 转普通请求体可合并字典，不支持时空字典。直接 httpx 调用和 ChatOpenAI 的字段位置不同。
resolve_agent_thinking|按附件互斥、用户开关和协议支持生成 requested/applied/reason。attachment_ids 只触发关闭，不读取实际图片。
complete_thinking_for|分类、计划、批判分别读角色配置；不支持协议或其他角色默认 False。主模型请求开关不直接传播到所有辅助角色。
agent_timeout|选择显式或默认超时，主 thinking 开时乘二。只返回秒数，真正 deadline 在执行器。
""")
put("app/ai_service/tool_registry.py", """
ToolRegistry.__init__|初始化组->名称列表与名称->ToolSpec 两个字典。只是内存注册表，不存数据库审计。
ToolRegistry.register|拒绝重名，保存 spec 并将名称追加到组。parallel_safe 等能力来自注册描述，必须由开发者正确标记。
ToolRegistry.register_group|用名称列表设置一个组，允许组织现有工具别名分组。不会自动创建缺失 ToolSpec。
ToolRegistry.get|按名称取 spec，未知返回 None。执行器把未知工具按可能有副作用保守处理。
ToolRegistry.resolve|按可选组解析工具，指定组时去重，过滤不存在 spec 的名称。返回描述列表，不绑定当前用户。
ToolRegistry.unregister|移除 spec，并从各组清除所有同名引用。测试动态注册结束需清理，避免污染后续。
ToolRegistry.bind|对已注册工具优先使用 spec.fn，否则从当前用户内置闭包取函数。没有实现的工具不加入返回映射。
ToolRegistry.groups_for|根据工具取 base+自身组，写笔记额外提供 note_read，未知返回 None。支持步骤先读真实内容再写。
""")
put("app/ai_service/tools.py", """
_clip|为工具输出按字符截长正文并加省略号。限制工具结果尺寸，不是完整上下文 Token 预算。
_resolve_category_id|按用户、活跃状态和名称找分类，空名/未找到返回 None。不同父级可同名，scalar_one_or_none 在多项命中时存在歧义边界。
bind_user_tools|为当前 user_id/session_factory 建一组闭包并返回名称映射。模型参数不会决定当前用户，每个工具自行管理需要的 session。
bind_user_tools.what_time_is_now|返回服务器本地格式化日期时间。不是从模型记忆推测时间，也不使用用户时区字段。
bind_user_tools.get_user_info_tools|独立 session 查当前用户，输出用户名、邮箱和 ID，缺失给兜底文字。不输出密码哈希。
bind_user_tools.search_notes_tool|向量查多片段，回 SQL 校验活跃/归属并按 note_id 去重；无卡片才关键词兜底。返回保留真实 ID 的搜索文本，不把向量残留直接当可访问笔记。
bind_user_tools.get_note_content_tool|按真实 note_id 读有权限正文，输出标题/标签/日期和有限长正文，业务不存在转文字。不能仅凭猜到 UUID 越权。
bind_user_tools.get_note_stats_tool|SQL 外连接分类统计当前用户活跃笔记，把未分类排末并输出文字。不会把已删除笔记计入活跃总览。
bind_user_tools.today_reviews|开独立 session 调只读回顾工具并返回文本。无写入所以不 commit 业务状态。
bind_user_tools.mark_reviewed|调用完成回顾适配器并 commit，业务或其他异常 rollback 后返回可读失败。是有副作用工具，外层不能盲目重放。
bind_user_tools.create_note_tool|解析逗号标签与分类名，组 NoteCreate，复用笔记 service 并自己 commit，返回新 ID/标题。继承提交后索引与回顾记录。
bind_user_tools.update_note_tool|仅构建模型实际提供的字段，解析标签/分类后调用笔记更新并 commit，异常 rollback。分类空/找不到可变未分类，不能误以为省略参数等于清空。
bind_user_tools.get_related_notes_tool|拿 note_title 复用 search_notes_tool 返回相关卡片。不是新增另一套向量算法。
_empty_params|返回无参数对象 Schema，并禁止额外字段用于内置工具描述。LangChain 转换器是否完整保留所有 JSON Schema 语义需另看其实现。
register_builtin_tools|若已注册关键内置工具则跳过，否则创建时间/用户/读写笔记/回顾描述，标只读 parallel_safe 并登记。导入模块即调用；这里没有注册邮件/PPT 工具。
""")
put("app/ai_service/usage_callback.py", """
ModelUsageCallback.__init__|保存模型名/阶段与按 run_id 跟踪的字典。每个模型实例回调区分工具循环中的多次推理。
ModelUsageCallback.on_chat_model_start|序列化完整 messages 批次和工具声明，按 run_id 保存提示文本与起始时间。下一轮包含的工具返回也因此进入输入估算。
ModelUsageCallback.on_llm_end|取对应起点，优先 llm_output usage，其次消息 metadata，收集正文/工具调用并记录一次计量。每次模型完成记一次，不把整轮聊天粗略合成一条。
ModelUsageCallback.on_llm_error|弹出 run_id 的提示和起点，以异常类型记失败用量与耗时。失败不因没有正常输出而完全消失。
""")
put("app/routers/user.py", """
register|接 UserRegister，查用户名、默认要求验证邮箱、消费 code、查邮箱、校验密码、写 User 并播种分类。SQL 由依赖提交；已消费验证码不随 SQL 失败恢复。
sse_token|依赖正常用户鉴权，调用 create_sse_token，返回 token 和 60 秒寿命。不是匿名签票接口。
send_code|提取 IP，检查邮件专属额度，发送验证码，成功再标冷却；普通发送异常转 502。转发头可信性由部署保证。
change_email|先消费验证码，检查目标邮箱占用，再修改当前用户 email/email_verified 并 flush。失败不会自动恢复 Redis 验证码。
login|先锁定检查再查密码，失败增加计数，成功清计数并签 access/refresh、登记白名单。有 device_id 才维护设备并按上限淘汰，不能说每次登录一定生成设备项。
refresh|校验 refresh 签名/类型/白名单，撤销旧票后签新票，有 device_id 则更新设备状态。多次 Redis 命令不是一个原子刷新脚本。
logout|拉黑当前 access，按可选 refresh/device 撤销当前用户刷新能力并删设备。不是删除 SQL 用户或全量所有 access。
get_me|从可信 user_id 查询 User，找不到 404，返回 UserInfo 公开字段。不会把密码哈希直接 dump 给客户端。
update_me|按当前用户定位，只在 bio 非 None 时更新并 flush。此入口不是任意修改账号所有字段的通用 patch。
change_password|校验原密码和新强度，替换哈希并撤销所有 refresh/设备。SQL commit 在依赖，Redis 撤销已经发生，跨存储不原子。
upload_avatar|受限读取、校验格式后写用户目录新文件，尝试删旧头像，更新 URL 并返回。磁盘动作不受 SQL rollback 控制，也不是完整图片重编码。
get_sessions|从 X-Device-Id 得当前设备标识，查询 Redis 设备列表返回。标识只用于展示 is_current，身份仍来自 Token。
revoke_session|定位用户设备，撤销其 refresh 和设备记录；若请求头标为当前设备再黑名单当前 access。其他已发 access 不自动全部撤销。
""")
put("app/routers/note_router.py", """
create_note|接 NoteCreate 和已鉴权用户，调用 service，返回新笔记 ID/标题/格式/时间。路由不手写切片/embedding，commit 由依赖完成。
list_notes|接分类、未分类、关键词与有界分页参数，委托 SQL 列表服务。它不是知识库向量搜索接口。
recycle_bin|调用笔记 service 返回当前用户软删笔记列表及保留天数，包装成功响应。仅展示，不在读取时清掉过期项。
batch_operation|接操作与 ID 集合，委托 batch_notes，包装成功/失败数量和逐项结果。不是每条独立数据库事务。
search_notes|把 query/top_k 交关键词搜索，返回结果信封。此路由走 FULLTEXT/LIKE，不调用聊天 Agent。
autocomplete|为当前用户设置 note_ai 计量上下文，调用补全并 finally 清除，返回 completion。不会自动保存正文。
write_assistant|设置/清理计量上下文，按 mode 获取写作结果。返回建议，不把 result 直接写进笔记。
auto_tag|在 note_ai 计量范围调用标签建议，返回 tags。没有更新 Note.tags 的数据库副作用。
get_note|读当前用户活跃笔记并用 NoteResponse 序列化。被软删或不属于用户都不能作为正常详情访问。
update_note|用 exclude_unset=True 提取显式字段，交 service 更新，再响应序列化。省略 category_id 与显式 null 语义不同。
move_note_to_category|把 note_id 与可空分类 ID 交 move_note，再返回更新后的 NoteResponse。只修改分类，不手动重建正文向量。
delete_note|把当前用户与 note_id 交给软删除服务，完成后返回已移入回收站说明。不是物理删除正文，仍可在保留期内恢复。
restore_note|委托恢复当前用户已删笔记并返回成功。索引恢复在事务提交后进行。
export_note_email|校验笔记归属，优先请求收件人否则用户邮箱，生成附件并发信，发送错误转业务错误。普通邮件导出已存在，不等于 Agent 发邮件工具存在。
permanent_delete_note|按配置增加专属删除额度检查，再委托物理删笔记。不可恢复，且 service 当前允许直接永久删活跃笔记。
""")
put("app/routers/category_router.py", """
category_tree|返回当前用户活跃分类树与直属笔记数。权限来自 Depends，树构建在 service。
create_category|接创建数据，service 创建后再查 get_category_dict 回显计数等字段。不是只返回未经验证的请求体。
update_category|委托修改名称/样式，再读规范分类响应。数据库事务由请求依赖统一提交。
move_category|把新 parent_id 交 service 检查环/深度并移动，再回显。路由本身不跳过服务层树规则。
delete_category|委托软删并返回子分类/笔记影响数量。删除会提升孩子、解绑笔记，不是递归全删。
recycle_bin|返回当前用户分类回收站展示数据。不会自动恢复祖先或删除子树。
restore_category|委托恢复分类及需要的已删祖先/后代，包装恢复结果。不是重建删除前所有笔记挂载。
permanent_delete_category|委托已删分类物理删除并返回影响结果。活跃孩子保护在 service，操作不可逆。
reorder_categories|接同级排序数据，交 service 验证并更新位置。一次请求完成同一组的 SQL 变更。
batch_operation|delete 分支逐个删、merge 分支统一合并；restore/permanent 分支逐条捕获 BusinessError 收集结果。不同分支容错不同，不能概括成所有批量项都失败隔离。
""")
put("app/routers/chat_router.py", """
chat_query|唯一主聊天 HTTP 入口，校验 QueryRequest 与聊天身份后返回 SSE，直接调用 query_service.stream_query。HTTP 状态成功不等于整个后续流一定成功。
list_sessions|按用户调用会话列表服务，允许短期缓存。返回会话元数据不是所有消息。
update_title|把用户改名请求交 service，设置手动保护并返回会话数据。后台标题不能再覆盖这个标记。
delete_session|校验用户归属后删除会话及缓存，返回统一响应。不是删除用户全部会话。
list_messages|按 session_id 查完整 SQL 消息列表，先经过会话权限校验。没有 Redis 20 条截断限制。
""")
put("app/routers/knowledge_router.py", """
upload_document|流开始前受限读、校验大小/扩展名/重复，随后建立独立进度生成器返回 SSE。早期错误仍是普通 HTTP 错误。
upload_document.event_generator|独立 session 消费保存文档 service 的进度，在 completed 后 commit，再发 finish；错误 rollback 并按流协议通知。文件/向量不是 SQL 回滚的一部分。
list_documents|将当前用户交文档列表 service，返回其 documents/total，当前没有分页。不会直接遍历文件目录作为权限依据。
search_documents|接查询和 top_k，直接搜索用户知识库并包装结果。没有聊天门控/摘要/Agent。
get_document|按文档 ID 和用户加载 SQL 元数据并转响应。不能猜 ID 越权读取。
delete_document|委托权限检查后的文档删除，涉及文件/向量/SQL。正常 SQL 提交由依赖完成，外部动作不原子。
""")
put("app/routers/note_template_router.py", """
_dump|把模板 ORM 转为 NoteTemplateResponse 的 JSON 形状。避免把 SQLAlchemy 内部属性直接塞响应。
create_template|校验请求并创建用户模板，序列化返回。只保存模板，不创建笔记。
list_templates|传当前用户和筛选给 service，逐项 _dump 返回。模板查询与笔记分类树无直接外键绑定。
get_template|通过有权限单项查询取得模板并返回。模板 ID 不是跨用户通行证。
update_template|提取显式更新字段，委托模板 service 并返回新状态。不影响已套用模板生成的笔记。
delete_template|委托删除当前用户模板，返回完成说明。不是删除模板曾产生的全部内容。
apply_template|读模板并委托创建笔记，返回新笔记标识与信息。回顾/向量生命周期由普通笔记创建继承。
""")
put("app/routers/review_router.py", """
get_today_reviews|获取当前用户到期复习项目并包装成功响应。只读，不在取列表时标记已完成。
mark_reviewed|接 review_id 与质量字段，调用 service 更新间隔/下次时间。质量目前存储而非自适应间隔输入。
get_review_stats|按用户请求当前回顾统计并返回。不是读取独立的完整历史打卡事件流。
""")
put("app/routers/usage_router.py", """
usage_summary|接有界 days 与可选 session_id，使用当前用户查询用量/费用聚合。未登录拒绝，跨用户数据由 service 条件隔离。
""")
put("app/routers/health.py", """
health_check|立即返回进程存活响应，使用自己的 code=200 信封。不会连接外部依赖，适合区分进程存活与业务就绪。
readiness_check|检查 SQL 和 Redis 状态，均可用 HTTP 200 否则 503。不是 SMTP、模型、Chroma 或真实检索效果探针。
""")
put("app/schemas/auth.py", """
UserRegister.validate_username|校验用户名允许字符/格式并返回规范输入或抛 ValueError。用户名是否已经占用仍需路由 SQL 查询。
UserRegister.validate_email|允许兼容的可空邮箱，并对非空值校验邮箱格式。默认注册是否必须邮箱由路由配置决定。
SendCodeRequest.validate_email|校验发送验证码目标地址格式。只验证字符串，不证明目标邮箱真实存在或归属请求者。
EmailChangeRequest.validate_email|验证改绑目标邮箱格式，后续仍需验证码和占用检查。Schema 本身不访问 Redis。
NoteExportEmailRequest.validate_to|对可选导出目标邮箱做格式检查，未给时路由回退用户邮箱。验证不发信。
PasswordChange.validate_password|对新密码字段应用项目强度规则，失败变参数校验错误。原密码是否正确还要查询用户后 bcrypt 验证。
""")
put("app/schemas/category.py", """
CategoryBatchRequest.validate_merge|在 merge 操作时要求目标分类并约束来源列表等字段关系。树环、归属和深度仍由 service 校验，不由 Schema 推断数据库状态。
""")
put("app/schemas/note.py", """
NoteBatchRequest.validate_batch|限制一次 permanent_delete 最多 50 项、restore 最多 100 项；move 分支允许 None 且不做额外检查。不能假设它强制显式提供目标分类。
""")
put("app/models/user.py", """
generate_uuid|返回 uuid4 字符串供 User 主键默认值使用。每次实际插入需要新 ID，不在模块导入时生成一个共享值。
""")
put("alembic/env.py", """
run_migrations_offline|配置 URL、metadata 与 literal_binds，在离线事务上下文运行迁移以输出 SQL。不建立真实数据库连接，但生成脚本仍需人工审查。
do_run_migrations|收到同步 connection 后配置 Alembic 并执行版本链。由异步连接的 run_sync 桥接调用。
run_async_migrations|创建无连接池迁移 engine，连接后 run_sync 调同步迁移，最后 dispose。它连接实际配置数据库，与静态文档扫描不同。
run_migrations_online|用 asyncio.run 启动在线异步迁移协程。只适合 CLI 入口，不是 HTTP 请求内随手调用的建表工具。
""")
put("tests/conftest.py", """
isolated_configuration|autouse fixture 禁止 Settings 读真实 .env 并清配置缓存，yield 后清计划/分类/反思/ReAct 注入。让本机模型配置不污染测试，不启动外网模型。
client|建临时 SQLite、fakeredis、Ephemeral Chroma 和 test Settings，覆盖依赖并提供 TestClient；结束等待后台任务、释放 engine、清注入。不是启动真实 TCP 服务或操作业务数据库。
client._create_tables|在临时 engine 上通过 metadata.create_all 建测试表，然后 dispose 以免连接跨事件循环。它不测试完整生产 Alembic 链。
client.override_session|测试版 Depends，每次独立 session，正常 commit、异常 rollback。保留事务语义才能检测 after_commit 索引时序。
""")
put("tests/test_agent_alignment.py", """
settings|生成不读 .env、无真实 key 的 Settings，允许用 kwargs 改特定测试参数。保证测试差异只来自显式配置。
test_memory_covers_unsummarized_gap_and_preserves_roles|构造长历史与摘要覆盖点，断言未摘要 30 条不被旧窗口截断，长正文保留，摘要后从正确 ID 开始。再验证转换后的 Human/AI 角色。
test_history_respects_tiny_remaining_budget|用极小剩余额度和超长单条历史，断言选中消息仍符合预算。覆盖新链不能为保留最新一条而无限超额的边界。
test_legacy_zero_reserve_still_leaves_room_for_agent_tools|把 scratchpad 配零并输入巨大历史，断言仍扣 4000 自动预留。保护旧 .env 在新 Agent 主链的兼容语义。
test_tool_loop_limit_still_reports_started_write_for_replay_guard|把连续工具次数设六再开始更新工具，断言事件先 tool_start 后 error。保证循环上限不会隐藏已开始的写操作。
test_planning_deadline_falls_back_without_executing_tools|注入卡住的规划器并设短超时，断言唯一结果为 plan_fallback。证明规划阶段没执行工具时可以安全降级。
test_planning_deadline_falls_back_without_executing_tools.stalled|睡十秒模拟规划模型无响应，短 timeout 会提前取消。不是生产延时逻辑，也不执行工具。
test_classifier_deadline_falls_back_to_react|替换 L2 分类为卡住协程并设短超时，断言 source=fallback、route=react。验证复杂路由判断失败不拖死对话。
test_classifier_deadline_falls_back_to_react.stalled|接受任意调用参数后睡十秒，以触发分类超时。用来验证调用者 deadline 而非分类模型质量。
test_plan_rejects_invalid_dependency_graph|参数化输入未知依赖、自环、重复 ID 和未注册工具，要求 ValueError。它验证结构拒绝，不执行任何笔记操作。
test_dynamic_tools_execute_and_readonly_steps_exclude_writes|临时注册 echo，验证 LangChain 可调用动态实现、只读集合不含三个写工具、无参工具 Schema 空，计划也能引用动态名。finally 注销防污染。
test_plan_step_passes_real_dependency_ids_to_agent|注入两步搜索/更新计划，检查真实 note/review ID 传入后一步，且读写步骤权限不同。防止步骤执行器自己猜 ID 或只硬调一次工具。
test_plan_step_passes_real_dependency_ids_to_agent.fake_react|第一步返回真实样例 ID，后一步断言问题内包含它们，输出 stream_done。记录 kwargs 用于检查 read_only 和工具分组。
test_plan_step_passes_real_dependency_ids_to_agent.make_plan|返回预先构造的 ExecutionPlan，省去真实规划模型。让测试集中验证依赖结果传递。
test_plan_step_passes_real_dependency_ids_to_agent.by_step|给第一步追加识别标记，再转发 fake_react 事件。用于区分步骤，不改变生产 Plan 路由。
test_plan_parallel_reads_serial_writes_and_cancellation|替换步骤执行器记录活跃集合，断言两读并发、写时无其他活跃任务，关闭流后集合清空。验证并发策略和取消回收。
test_plan_parallel_reads_serial_writes_and_cancellation.step_stream|只读/写工具开始时维护 active，写工具先断言无其他任务，短等待模拟并发，finally 清 active。这样取消也能被测试观察到。
test_plan_parallel_reads_serial_writes_and_cancellation.make_plan|返回两读两写的固定无依赖计划。专门检验 safe_batches，不检验 LLM 会如何规划。
test_plan_does_not_replay_after_write|参数化读工具/写工具开始后失败，分别要求 fallback/error，写失败不能出现 fallback。保护可能已提交的副作用不被整轮重放。
test_plan_does_not_replay_after_write.make_plan|根据参数化 tool 创建单步骤计划。固定规划形状便于只比较工具副作用分类。
test_plan_does_not_replay_after_write.failing_step|先 yield tool_start 再 error，模拟开始后未获成功结果。用于证明不能等 tool_end 才认为可能已写。
test_react_repairs_read_failure_only|参数化读、写、未知工具失败，断言只有只读允许第二次执行并清旧稿；修复提示只暴露异常类型。覆盖 ReAct L2 护栏。
test_react_repairs_read_failure_only.FakeAgent.astream_events|第一次发工具开始后抛 RuntimeError，第二次发 fixed 正文，保存 payload。重试次数由真实执行器决定，不由 fake 自己循环。
test_reflection_status_is_live_and_replaces_draft|逐次 anext 验证 checking 先于 critique 真执行，再用假 Agent 验证修订触发 response_replace 和最终 corrected。测试事件时序而非仅最后文字。
test_reflection_status_is_live_and_replaces_draft.critique|记录自己已经被调用，并返回不通过及 fix 指令。配合 checked 列表判断状态是否及时送出。
test_reflection_status_is_live_and_replaces_draft.refine|返回 corrected 固定修订稿。避免用真实模型让替换断言不确定。
test_reflection_status_is_live_and_replaces_draft.FakeAgent.astream_events|产出一块 draft 模型正文事件。反思由真实 run_langchain_react 继续执行。
ToolCallingModel.bind_tools|假模型接受工具绑定但直接返回 self。使真实 LangChain create_agent 能使用预设工具调用消息，不访问网络。
ToolCallingModel._stream|从预设 _generate 消息构建 ChatGenerationChunk，保留正文、tool_calls 和 usage_metadata。不是跳过 LangChain 的整段假 ReAct。
test_real_langchain_tool_loop_records_each_model_call|用真实 LangChain 循环配预设模型先调工具再回答，断言真实参数、两次用量、历史和工具结果进入对应输入。证明 callback 按每次模型调用计量。
test_real_langchain_tool_loop_records_each_model_call.execute|记录传入 value 并返回 tool-result。验证 StructuredTool 实际收到 real-id，不只输出装饰事件。
test_real_langchain_tool_loop_records_each_model_call.record|用列表捕获 record_text_call 的 kwargs，替代实际 SQL 用量写入。用于检查 usage 和 prompt，无数据库副作用。
test_classifier_uses_role_model_and_thinking|替换补全并配置 small-model/角色 thinking，断言分类选择计划且传入正确 model、开关和超时。与主模型设置解耦。
test_classifier_uses_role_model_and_thinking.complete|捕获 config.llm_model 与关键字参数，返回固定 complex JSON。用于验证配置传递而非模型理解能力。
test_usage_stages_do_not_leak_between_parallel_steps|两个 gather 分支分别切阶段，断言各保留自己的值且父仍 chat。防止 ContextVar 中共享字典被原地修改。
test_usage_stages_do_not_leak_between_parallel_steps.branch|设置分支 stage，主动让出事件循环后读回。让并行交错足以暴露共享状态污染。
""")
put("tests/test_notes_categories.py", """
_register_and_login|在隔离 TestClient 中注册登录，返回带 access 的 headers。fixture 关闭强制邮箱，不能照抄为默认生产注册规则。
_find|递归遍历响应 children 找指定名称，没找到 None。测试辅助树查找，不调用分类 service。
_tree|GET 分类树并取 data，减少用例重复响应拆包。错误处理由测试后续断言暴露。
test_register_seeds_template_tree|注册后断言顶级默认名称顺序、技术子项与三层节点存在。证明注册复用播种，不是前端硬编码树。
test_create_category_and_same_name_conflict|同父级创建后检查排序，再重复同名要求 409，其他父级同名允许。覆盖应用级同级唯一规则。
test_create_category_depth_limit|在已有第三层下继续创建，要求 400/INVALID_PARAMETER。验证不能只按 parent 存在就接受。
test_rename_and_soft_delete_promotes_children|先改父名再软删，断言父消失、活跃孩子变顶级。固定当前不是级联软删整树的语义。
test_move_category_rejects_cycle|将祖先移动到后代下，要求拒绝。防止分类链成环后递归/展示异常。
test_note_crud_flow|创建分类笔记，检查列表/详情，再只改置顶和 category_id=null，检查未分类过滤。验证部分更新与 MD 默认格式。
test_note_keyword_filter|创建两条不同主题笔记，列表 keyword 只命中 Redis 项。针对列表 SQL 过滤，不是向量检索效果评测。
test_note_trash_restore_permanent|按创建、软删、回收站、恢复、再永久删除顺序检查各列表。验证生命周期状态，不代表直接永久删活跃项已被禁止。
test_category_delete_unties_notes|删有笔记的分类后读笔记，断言仍存在但 category_id=None。保护笔记不被分类删除连带移除。
test_cross_user_isolation|两用户分别登录，B 对 A 笔记读/改/删都 404，各用户默认分类 ID 不同。验证用户隔离且不泄露资源存在性。
test_pinned_note_sorts_first|创建早晚两笔记后置顶早项，断言列表第一是它。覆盖排序优先级。
test_category_recycle_restore_ancestors|先删孩子后删父，再恢复孩子，检查祖先一起恢复。与先删父导致活跃孩子提升的场景不同。
test_category_permanent_delete_and_cleanup|验证手动永久删分类，再把另一已删分类时间改旧并调用清理，确认消失。不是等待真实定时器触发。
test_category_permanent_delete_and_cleanup._age_and_clean|在测试库把 deleted_at 改为十五天前并 commit，再调十四天 cleanup 提交返回数量。制造可控过期条件。
test_category_reorder_and_merge|反转完整顶级排序并检查响应，再合并阅读到学习，确认来源软删进入回收站。覆盖正常合并路径，不证明所有冲突分支。
test_note_format_txt_and_move_category|验证 txt 创建/读取、更新不能改 format、移为未分类，非法 pdf 创建 422。区分 Schema 输入约束与业务移动。
test_note_batch_and_cleanup|批量置顶/移动/删除/恢复/永久删除检查逐项结果，再人为过期一条清理。验证批量服务主要成功路径。
test_note_batch_and_cleanup._age_and_clean|把测试笔记 deleted_at 改旧，调用 cleanup_expired_notes 并提交。独立事务便于确认清理条件。
test_note_keyword_search_title_outranks_content|检查 LIKE 百分号字面匹配、标题比正文靠前及 1.0/0.5 展示分，排除已删和其他用户。SQLite 环境不证明 MySQL FULLTEXT 效果。
test_note_template_crud_apply_and_isolation|创建/列表/改名/读取模板、套用得到笔记、跨用户禁止、删除后 404。验证模板到普通笔记创建链。
test_note_ai_assist_uses_injected_fn|注入按提示返回结果的假模型，验证补全、扩写、标签接口及非法模式 422。不测试真实供应商输出质量。
test_note_ai_assist_uses_injected_fn.fake_complete|按 prompt 中补全/标签/扩写关键词返回固定文字，其他返回续写。用于观察每个入口是否构造了正确任务提示。
""")
put("tests/test_persistence_alignment.py", """
test_note_index_dispatches_after_commit_not_rollback_or_metadata_changes|替换索引为记录器，分别测试创建提交、元数据更新、标题回滚、标题提交。确认只在有效正文事实提交后派发。
test_note_index_dispatches_after_commit_not_rollback_or_metadata_changes.index|记录被索引实体的 ID/标题，替代外部 embedding 与 Chroma。用于观察后台派发次数和读到的最新内容。
test_note_index_dispatches_after_commit_not_rollback_or_metadata_changes.run|在测试事件循环执行四组事务，每次 drain 后断言索引列表。关键断言在 commit 之前也检查没有提前索引。
test_hot_cache_rebuild_preserves_chronological_order|调用内部 run 检查 30 条输入在 buffer=20 后得到 11..30 正序。防止 LPUSH/反转组合错误。
test_hot_cache_rebuild_preserves_chronological_order.run|构造递增消息，重建 Redis 热缓存后读回并精确比较 ID 顺序。不是查询正式聊天历史。
test_usage_preserves_provider_zero_counts|断言供应商 completion_tokens=0 不变成文本估算，并检查完全没 usage 的向上估算。覆盖 truthiness 导致错误计量的回归。
test_additive_chat_migration_preserves_existing_titles_and_messages|在临时 SQLite 构造旧表/旧数据，真实调用 f1 upgrade/downgrade，检查标题保护、键字段与旧正文保留。只验证该增量迁移，不运行完整生产链。
""")
put("tests/test_query_lifecycle.py", """
auth|测试注册登录，返回 headers 和 user_id，先断言注册成功。帮助后续 SQL 断言定位用户。
query|POST 主 query 并断言 HTTP 200，再从 data: 行解出事件列表。流内 error 仍可能是 HTTP 200，后续必须看 type。
test_query_rag_failure_preserves_user_message_and_final_answer|让 RAG 抛错但 fake ReAct 先草稿后替换，断言检索前已有用户消息、最终 corrected 同时出现在 done 和 SQL。覆盖先保存与替换一致性。
test_query_rag_failure_preserves_user_message_and_final_answer.failed_rag|在抛检索异常前独立查消息数量，记录用户是否先提交。避免只看响应假设持久化顺序。
test_query_rag_failure_preserves_user_message_and_final_answer.fake_react|记录传入 history，依次发 draft、response_replace corrected、stream_done。测试服务端不能把新旧稿拼在一起。
test_query_idempotency_replays_once_and_isolates_users|同用户同 key 重复只执行一次并重用助手 ID，正文冲突拒绝，其他用户同 key 可独立执行，跨会话归属拒绝。覆盖幂等范围而非工具通用 exactly-once。
test_query_idempotency_replays_once_and_isolates_users.fake|每次被调用记录一次并 yield answer。调用次数直接反映是否错误重跑 Agent。
test_inflight_duplicate_does_not_run_agent_twice|让首请求暂停在 Agent，期间提交重复 key，要求立即 error 且 Agent 一次、最终两条消息。检验在途不是等同已完成重放。
test_inflight_duplicate_does_not_run_agent_twice.fake|设置 entered 事件并等待 release，制造首轮已接收未完成窗口。释放后才生成答案。
test_inflight_duplicate_does_not_run_agent_twice.run|并发启动首流、等待 entered、调用重复流，释放首轮后检查调用数及 SQL。运行于 TestClient portal 的异步环境。
test_inflight_duplicate_does_not_run_agent_twice.run.collect|完整消费相同 QueryRequest 的服务流并返回原始 SSE 帧列表。用于对比首轮与重复请求，不经过 HTTP 路由。
test_full_sql_memory_is_not_limited_by_redis_window|预置 30 条 SQL 历史，下一轮捕获 Agent 输入并断言全部可见。验证新主链不先削成 Redis 热窗口。
test_full_sql_memory_is_not_limited_by_redis_window.seed|建立会话和 30 条交错角色消息并 commit，返回 ID。准备的是 SQL 事实，不预填 Redis。
test_full_sql_memory_is_not_limited_by_redis_window.fake|把 history 加入 captured 并返回简短答案。外层用此观察真实上下文选择。
test_slow_title_does_not_block_done_or_overwrite_manual_title|让自动标题等待，检查聊天先 done，再人工改名、释放自动任务，最终仍手动标题。验证后台延迟和条件 UPDATE 保护。
test_slow_title_does_not_block_done_or_overwrite_manual_title.slow_title|通知 started 后阻塞等待，释放才返回 automatic-title。可控制造模型慢于用户编辑的竞争。
test_slow_title_does_not_block_done_or_overwrite_manual_title.fake|只输出 answer 让聊天快速结束，耗时放在标题假函数中。隔离标题与主生成的影响。
test_slow_title_does_not_block_done_or_overwrite_manual_title.wait_started|限时等待标题任务确实开始。确保测试手动改名发生在读旧标题之后，而非靠随机 sleep。
test_slow_title_does_not_block_done_or_overwrite_manual_title.finish|释放慢标题，drain 全部任务，再 SQL 断言 title/manual 都没被覆盖。验证最终事实不只看改名接口响应。
test_titles_update_in_early_rounds_only|以第二轮和第四轮状态调用标题维护，断言只前者触发生成。测试默认早期轮次数限制。
test_titles_update_in_early_rounds_only.title|记录生成问题并直接返回问题为标题。调用列表反映是否超过轮次仍调用模型。
test_titles_update_in_early_rounds_only.run|造两条 user 消息、更新标题并核查，再加两条后再次尝试，检查没有第四轮调用。直接测后台 helper 而非完整 SSE。
test_registration_requires_verified_email_by_default|恢复强制邮箱配置，断言缺邮箱/错 code 为 400，正确 fake code 成功。防止 fixture 的兼容注册掩盖默认规则。
test_registration_requires_verified_email_by_default.verify|只接受固定 123456，替代 Redis/SMTP 验证。用于路由必填与错误路径，不验证真实发信。
test_sse_token_single_use_and_not_profile_auth|检查 60 秒 JWT、资料接口拒绝 SSE 票、聊天首次成功第二次 401、Redis 条目缺失也拒绝。验证用途限制和单次消费。
test_sse_token_single_use_and_not_profile_auth.expire|直接删一次性票的 Redis jti 条目模拟失效。不是实际等待六十秒，也不改 JWT 签名。
test_chat_graph_cancellation_closes_model_stream|注入无限流，在首 response 后关闭图，断言下游 finally 执行。防止断流后模型生成器泄漏。
test_chat_graph_cancellation_closes_model_stream.endless|持续 yield chunk 并主动让出循环，finally 记录关闭。用于观察取消传播，不会访问真实 LLM。
""")
put("tests/test_retriever_predict.py", """
_FakeSentenceTransformerCrossEncoder.__init__|保存预设分数并初始化 pairs 记录。模拟只支持 predict 的模型接口。
_FakeSentenceTransformerCrossEncoder.predict|记录收到的 query/document 对并返回预设 scores。外层测试据此确认适配调用真实发生。
test_sentence_transformers_cross_encoder_uses_predict|注入 predict 风格假模型验证重排排序与输入配对。防止只兼容 compute_score 导致 sentence-transformers 静默降级。
""")
put("tests/test_thinking.py", """
_settings|构造测试 Settings 默认无 key/60 秒超时，允许覆盖。真实 .env 由 autouse fixture 屏蔽。
_auth|隔离 client 注册登录返回 access headers。只为测试准备身份，不测试完整邮箱发送。
_read_sse|用 TestClient 消费主聊天流并合并 bytes/str 成正文，先断言 HTTP 200。具体事件语义由各用例检查。
test_resolve_agent_thinking_plain_on_off|验证无附件基本开关、applied/reason 和无需 notice。只测纯决策函数。
test_resolve_agent_thinking_attachment_mutex|验证附件即关闭、用户请求思考才发附件提示。没有测试图片理解功能。
test_complete_roles_default_off_and_independent|验证三个辅助角色默认关、分别打开生效以及 DashScope extra_body。避免把请求主开关套给全部模型。
test_agent_timeout_doubles_when_thinking|比较默认/显式超时在思考开关下倍增。测试纯数值策略，不等待真实超时。
test_thinking_protocol_auto_dashscope_vs_openai_gateway|比较不同配置 URL，要求普通兼容网关不带扩展，角色开关也受协议约束。只是本地协议判断，不访问这些地址。
test_thinking_protocol_forced_none_even_on_dashscope|显式 none 必须覆盖域名自动识别。便于部署禁用不支持的扩展行为。
test_resolve_agent_thinking_unsupported_on_gpt_gateway|请求为 true 但协议不支持时 applied=false 且有说明。requested 与 applied 应当分别保留。
test_query_thinking_applied_without_attachments|通过主接口捕获 ReAct 参数与 done 字段，断言普通支持场景应用思考。fake 代替真实模型。
test_query_thinking_applied_without_attachments.fake_react|记录 enable_thinking，输出固定思考答案与 stream_done。让接口测试只关心开关传递。
test_query_thinking_disabled_when_attachment_ids|主请求含附件 ID 时断言 ReAct 接到 false，流含附件说明和 requested=true。不是多模态测试。
test_query_thinking_disabled_when_attachment_ids.fake_react|记录应用开关并返回固定看图文案。文案是测试替身，不能作为已实现视觉模型的证据。
test_query_thinking_skipped_when_protocol_none|改 app settings 为普通网关后请求思考，断言普通模式及 unsupported 提示。验证路由使用当前 app 配置。
test_query_thinking_skipped_when_protocol_none.fake_react|捕获开关并输出普通回答。用来断言 unsupported 情况未把 true 误传下去。
""")
put("tests/test_usage.py", """
_auth|在测试 client 注册登录取得 access headers。为用量按用户归属的断言准备独立身份。
test_estimate_tokens_rounds_up|断言空、偶数字符、奇数字符的估算为 0/1/2。验证 usage 估算而非 TokenCounter 的另一套 fallback。
test_usage_summary_empty|新用户无调用时检查总数、Token、费用和分组均为空/零。不是把缺数据当 API 故障。
test_note_ai_records_usage|一次注入补全后查 summary，要求一条 note_ai 记录、输入输出正数及本地费用。验证计量链真实落测试 SQL。
test_note_ai_records_usage.fake_complete|返回固定非空补全，保证估算输出 Token 可观察。无供应商 usage，走文本估算。
test_usage_isolated_by_user|A 调一次补全后分别查 A/B，要求 A 一次 B 零次。防止聚合缺用户条件泄露用量。
test_usage_isolated_by_user.fake_complete|返回 ok 的稳定补全，触发 A 的计量。没有真实模型调用成本。
test_usage_requires_auth|不带 Token 请求 summary 要求 401。保证用量不是公开统计接口。
""")
put("tests/test_chat_routes.py", """
auth|通过测试 client 注册并登录，返回 access headers 和用户 ID。给聊天归属及实际用量写库测试准备身份，不连接正式账号服务。
query|向唯一聊天入口发送请求，确认 SSE 类型后把 data JSON 帧转成事件列表。供测试断言最终消息和工具事件，不执行额外模型调用。
test_chat_routes_have_one_query_entry|核对 OpenAPI 仅保留 query 与会话管理；旧 ask/stream 返回 404，chat_service 不再有独立问答函数。防止重复入口被重新接入。
test_chat_router_calls_query_service_directly|替换 query_service 流并验证 router 原样传工厂、用户、消息、配置。确认主链不再绕 chat_service 兼容包装。
test_chat_router_calls_query_service_directly.fake|捕获路由传入参数，输出固定 response/done 帧。只替换问答编排，不替换认证依赖，因而仍验证用户归属传递。
test_query_preserves_session_crud_and_user_isolation|通过注入回答创建会话，验证列表、完整消息、手动标题、删除及其他用户的 404。清理旧入口不能破坏会话产品功能。
test_query_preserves_session_crud_and_user_isolation.fake|输出固定 answer 事件，避免外部模型。会话创建与消息提交仍由真实 query_service 执行。
test_local_fallback_preserves_sources_and_does_not_claim_no_llm|检查本地摘录保留来源、无检索与无命中文案不同，并验证中文 SSE JSON。避免遗留文案误称全项目未接模型。
test_query_without_model_still_executes_local_tool|无模型密钥时真实调用时间工具，核对 start/end/done 的结果一致且无模型用量。删除旧 HTTP 工具循环不能破坏本地降级。
test_auxiliary_completion_still_records_provider_usage|用假的 HTTP 响应驱动真实辅助补全及用量落库，再从 summary 核对官方输入13、输出2及 title 阶段。确认移除旧流客户端没有影响非流补全。
test_auxiliary_completion_still_records_provider_usage.fake_post|检查辅助调用走非流式 chat/completions，返回含官方 usage 的固定响应。只替换 HTTP post，不跳过计时器、解析或真实数据库提交。
test_auxiliary_completion_still_records_provider_usage.complete|设置测试用户与 title 归属，调用真实补全并在 finally 清上下文。通过 client 的异步执行环境运行，避免正式模型请求。
""")

MIGRATIONS = {
    "e471331632c9": ("创建 users 和用户名索引，作为后续用户外键起点", "删除用户索引与 users 表，所有用户行会丢失"),
    "342a95208d0f": ("创建 note_categories 自引用分类表与 notes 表及关联索引", "先删除笔记再分类的相关索引和表，笔记/分类数据会丢失"),
    "b7c1d4e8f901": ("创建 knowledge_documents 元数据表、用户/MD5 索引", "删除知识文档元数据表及索引；不等于同步清本地文件或 Chroma"),
    "c8d2e5f0a123": ("创建 chat_sessions 与 chat_messages 及关联索引", "删除消息再会话的索引和表，聊天数据会丢失"),
    "d9e3f6a1b234": ("创建每会话唯一的 chat_summaries 表，保存摘要覆盖点和版本", "删除 chat_summaries，已有摘要丢失，原消息不由此函数删除"),
    "e0f4a7b2c345": ("创建 note_templates，并为 notes 建 MySQL ngram 全文索引", "删除全文索引和模板表，已有模板内容丢失"),
    "53816adf617f": ("创建 review_records，同时删除 notes 的全文索引，影响 HEAD 的关键词检索路径", "恢复 MySQL ngram 全文索引并删除 review_records，回顾数据会丢失"),
    "e2aebef3f9e7": ("为 users 增加非空 email_verified 字段；迁移未设服务端默认，已有数据部署需审查", "删除 email_verified 字段，原验证状态信息丢失"),
    "c3e9f2a7b890": ("创建 model_traces 与 model_pricing，建立用户/会话时间聚合索引", "删除模型用量与定价相关索引和表，计量历史丢失"),
    "f1a244c10001": ("增加 title_manual 并将已有非默认标题标手动，再加消息幂等字段和唯一索引；保留原正文", "删除幂等索引/字段及 title_manual；保留消息正文但失去防重和手动标题元信息"),
}

LAMBDA_NOTES = {
    "app/ai_service/chat_graph.py": [
        "分类条件边把 plan_execute 映射为 plan 节点，其他 route 映射为 react。由 StateGraph 调用，不执行模型本身。",
        "Plan 后条件边读取 state.route，选择 react 或 complete->END。它配合 plan 节点返回值实现安全降级。",
    ],
    "app/ai_service/tools.py": ["统计排序 key：未分类返回 True、其他 False，升序时未分类靠后。只改变输出顺序，不修改分类。"],
    "app/models/category.py": ["分类 ID 的延迟默认工厂，每次实际需要默认值时生成 uuid4 字符串。不能改成模块导入时只求值一次。"],
    "app/models/chat.py": ["ChatSession ID 的延迟默认工厂，每个新会话产生独立 UUID。消息 ID 则由数据库自增，不用此函数。"],
    "app/models/note.py": ["笔记 ID 的延迟默认工厂，每条新 Note 独立 UUID。没有用户权限含义，查询仍需 user_id。"],
    "app/rag/embeddings.py": ["API embedding 返回项按 index 升序排列，恢复与 input 对应关系。缺 index 时按零处理，不能把返回次序随意当输入次序。"],
    "app/rag/retriever.py": [
        "取某 chunk_id 的累计 RRF 分给 sorted，外层 reverse=True 高分优先。缺分回零，计算本身已在融合循环完成。",
        "取 rerank_score 作降序排序 key，缺值/零使用 0.0。不是重新执行模型打分。",
    ],
    "app/rag/vector_store.py": [
        "取 BM25 hit.score 作降序排列依据，空值用零。只排序当前用户已过滤的候选。",
        "hybrid 关闭时合并两源，直接按 hit.score 降序。没有 RRF 融合，这也是默认配置的可达分支。",
    ],
    "app/services/category_service.py": [
        "树响应构造中以 sort_order 升序排列同级节点。相同 sort_order 没有在此额外定义唯一性。",
        "合并分类时以 sort_order 排列要处理的项，保留已有排序意图。业务关系检查在外层 merge。",
    ],
    "app/services/query_service.py": [
        "捕获当前 factory/session/question/settings，返回标题协程供后台 task runner 稍后 await。创建 lambda 时尚未调用模型。",
        "捕获会话与配置，返回摘要维护协程供后台按 session key 串行。助手提交后登记，不让 done 等压缩完成。",
    ],
    "app/utils/auth_utils.py": [
        "设备展示按 last_used 字符串倒序排序，缺字段空串靠后。不同于上限淘汰使用的创建时间。",
        "设备上限淘汰取二元组中的 created_at，升序找最早设备。返回排序 key，不直接撤销凭证。",
    ],
    "tests/test_agent_alignment.py": [
        "动态 echo 工具的真实同步实现，原样返回 value。用于确认注册表 fn 能被 StructuredTool 调用。",
        "替换模型构造为普通占位 object，避免连接模型。此测试的模型事件由另外的 FakeAgent 提供。",
        "替换 Agent 构造为测试 FakeAgent，使第一次工具失败/第二次恢复可控。生产重试判断仍由真实执行器运行。",
        "反思测试用普通 object 代替真实模型构造。避免模型网络影响 checking/refining 时序断言。",
        "反思测试返回只生成 draft 的 FakeAgent。后续替换必须由真实反思逻辑完成。",
        "将模型工厂替换为预设 ToolCallingModel 实例。真实 LangChain 工具循环和 usage callback 仍参与执行。",
    ],
}

INJECTION_LABELS = {
    "app/ai_service/plan_execute.py": "计划流或计划生成",
    "app/ai_service/query_classifier.py": "查询分类",
    "app/ai_service/react_agent.py": "ReAct 事件流",
    "app/ai_service/reflection.py": "答案批判",
    "app/ai_service/runner.py": "本地降级 Agent 事件流",
    "app/rag/embeddings.py": "批量嵌入",
    "app/rag/hyde.py": "HyDE 假设生成",
    "app/rag/memory.py": "历史摘要生成",
    "app/rag/rag_route.py": "RAG 检索门控",
    "app/rag/rag_summarize.py": "命中片段摘要",
    "app/rag/retriever.py": "重排打分",
    "app/rag/session_title.py": "会话标题生成",
    "app/services/email_service.py": "SMTP 发送",
    "app/services/note_ai_service.py": "笔记写作补全",
}
