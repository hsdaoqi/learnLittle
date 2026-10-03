# 登录流程逐行讲解

这份讲解针对 `D:\Project\learnLittle` 在 2026-10-02 的实际代码，以后端为主，前端只用于说明请求怎么来、结果怎么用。不是原项目的理论流程，也不是 SMTP 邮箱登录。

这里的“登录”是用户名和密码登录：

```text
POST /api/v1/auth/login
```

代码入口：[user.py](D:/Project/learnLittle/app/routers/user.py:186)。

## 1. 先记住登录到底在做什么

登录不是简单地“把页面跳到首页”，而是完成两件事：

1. 验证这次输入的用户名和密码能否对应一个用户。
2. 验证成功后，发给客户端后续请求可以使用的身份凭证。

第一件事靠 MySQL 用户记录和 bcrypt 密码校验完成。

第二件事靠 JWT Token、Redis 凭证登记和设备会话记录完成。

因为登录请求结束后，下次“获取笔记”的 HTTP 请求本身不会自动记得刚才是谁登录，所以前端要在后续请求里携带凭证，后端再验凭证。

三个数据存储的分工：

| 位置 | 存什么 | 为什么放这里 |
| :--- | :--- | :--- |
| MySQL | 用户 UUID、用户名、密码哈希、资料 | 长期保存账号数据 |
| Redis | 登录失败次数、Refresh 白名单、Access 黑名单、设备会话 | 方便计数、快速查找、自动过期和撤销 |
| 浏览器 localStorage | 当前前端保存的 Token、用户信息、设备 ID | 页面刷新后仍能恢复前端状态 |

注意：localStorage 中的用户信息只是前端显示数据，不是后端判断权限的依据。

## 2. 一张调用图

```text
点击登录
  LoginPage.handleSubmit()
    authApi.login()
      getDeviceId() / getDeviceName()
      request() / Axios 请求拦截器
        POST /api/v1/auth/login
          RateLimitMiddleware.dispatch()
          FastAPI 解析 UserLogin，准备 get_db_session()
          login()
            check_login_attempts()
            db.execute(select(User)...)
            result.scalar_one_or_none()
            verify_password()
              失败：record_login_failure() -> BusinessError
              成功：clear_login_attempts()
            get_device_session()
            revoke_refresh_token()，如果同设备旧凭证存在
            create_refresh_token()
              _create_token()
              decode_token()
            store_refresh_token()
            get_settings()
            store_device_session()
            enforce_session_limit()
            create_access_token()
              _create_token()
            TokenResponse.model_dump()
            success_response()
          数据库依赖退出，提交/关闭会话
      request() 取出响应的 data
    setTokens()
    authApi.me()
      get_current_user_id()
        get_current_token_payload()
          decode_token()
          is_token_blacklisted()
      get_me()
    setUser()
    navigate('/')
```

图中的调用是条件调用。例如密码错误不会继续创建 Token；不传 `device_id` 时不会登记设备。

## 3. 请求进入后端前发生什么

### 3.1 LoginPage.handleSubmit()

位置：[LoginPage.tsx](D:/Project/learnLittle/front/src/pages/LoginPage.tsx:17)。

关键代码：

```tsx
e.preventDefault()
setError('')
setLoading(true)

const tokens = await authApi.login({ username, password })
useAuthStore.getState().setTokens(tokens.access_token, tokens.refresh_token)
useAuthStore.getState().setUser(await authApi.me())
navigate('/', { replace: true })
```

`e.preventDefault()` 阻止浏览器按原生表单方式提交并刷新整个页面。这里用 JavaScript 发请求。

`setError('')` 清除上次错误，`setLoading(true)` 让按钮显示登录中并禁用，避免用户连续点击。

`await authApi.login(...)` 等待后端返回，不是“等待跳转”，而是等待 HTTP 请求的结果。

`setTokens()` 先保存凭证，然后才能带凭证调用 `authApi.me()`。

`authApi.me()` 获取用户资料，因为登录接口只返回 Token，并没有返回完整资料。

`navigate('/', { replace: true })` 进入首页，并替换当前历史记录，减少按返回键又回到这次登录页的情况。

`catch` 显示错误；`finally` 无论成功失败都会执行 `setLoading(false)`，恢复按钮状态。

一个实际边界：Token 保存成功后，如果 `/user/me` 请求失败，这段代码会显示登录失败，但没有主动清除刚保存的 Token。不能把整个前端过程理解成一个能自动回滚的事务。

### 3.2 authApi.login()

位置：[auth.ts](D:/Project/learnLittle/front/src/api/auth.ts:41)。

它补上设备信息后调用通用 `request()`：

```ts
{
  username,
  password,
  device_id: getDeviceId(),
  device_name: getDeviceName()
}
```

`...data` 是把原先的用户名和密码字段展开到这个对象中。

`getDeviceId()`：从 localStorage 读已有 ID；没有则 `crypto.randomUUID()` 生成并保存。

`getDeviceName()`：根据浏览器 User-Agent 字符串，拼出类似 `Chrome / Windows` 的可读名称。

位置：[device.ts](D:/Project/learnLittle/front/src/api/device.ts:3)。

这不是硬件序列号，也不是可信的设备身份证明，只是当前浏览器存储环境的标识。清理 localStorage、使用不同浏览器或不同浏览器配置，都可能出现新的设备 ID。

### 3.3 request() 和请求拦截器

位置：[client.ts](D:/Project/learnLittle/front/src/api/client.ts:14)。

Axios 的 `baseURL` 是 `/api/v1`，因此 `/auth/login` 实际变成 `/api/v1/auth/login`。

请求拦截器会：

1. 如果已经有 Access Token，添加 `Authorization: Bearer <token>`。
2. 添加 `X-Device-Id` 请求头。

这里要区分两件事：登录函数读取的是请求体中的 `data.device_id`；其他接口可能通过请求头判断当前设备。请求头不是登录函数这行参数的来源。

登录接口本身不要求事先有 Access Token，否则新用户就永远无法登录。

`request<TokenPair>` 是前端 TypeScript 的类型标注，让编辑器知道返回值有哪些字段；它不是额外的运行时身份验证。

开发代理配置：[vite.config.ts](D:/Project/learnLittle/front/vite.config.ts:5)。开发时 `/api` 会代理到后端 `127.0.0.1:8001`；生产环境是否使用同样路径，要看实际部署的反向代理。

## 4. 请求怎么找到 login()

后端不是根据 Python 函数名来猜哪个接口。

路由通过这行登记：

```python
@router.post("/auth/login", summary="用户登录")
```

它表示：这个路由接收 HTTP POST，路径是 `/auth/login`。

主程序又把整个用户路由挂到 `/api/v1`：

```python
app.include_router(user_router, prefix=API_PREFIX, tags=["User & Auth"])
```

位置：[main.py](D:/Project/learnLittle/main.py:77)。

所以最终地址是：

```text
/api/v1 + /auth/login = /api/v1/auth/login
```

`summary` 和 `tags` 主要用于接口文档展示，不参与密码判断。

## 5. 到达 login() 前还有一道限流

位置：[rate_limit.py](D:/Project/learnLittle/app/core/rate_limit.py:116)。

`RateLimitMiddleware.dispatch()` 在路由之前检查请求频率。当前本地配置是开启限流，窗口 60 秒，全局额度 100 次；认证路径的代码额度是每窗口 5 次。

其相关函数：

| 函数 | 做什么 |
| :--- | :--- |
| `identity_for()` | 能解出有效 Access Token 时用用户 ID，否则使用 `anon:<直连 IP>` |
| `endpoint_limit_for()` | 从路径前缀规则选最长匹配；登录命中 `/api/v1/auth` 的额度 5 |
| `_hit()` | Redis `INCR` 加一，第一次时设置过期时间 |
| `check_rate_limit()` | 先检查全局次数，再检查当前请求路径的次数 |

这是固定时间窗口，不是“任意连续 60 秒最多 5 次”。而且计数键包含实际路径，登录和刷新分别有自己的路径计数。

它限制的是请求次数，包括密码正确的请求。

后面 `check_login_attempts()` 限制的是某用户名的密码失败次数。这两层不是同一个功能。

限流的身份提取也不是正式认证：它不负责检查 Access 黑名单，真正保护业务数据的认证依赖后面还会校验。

## 6. 看懂 login() 的三个参数

```python
async def login(
    data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
):
```

### 6.1 async 和 await

`async def` 定义可以异步执行的函数。

`await` 等待数据库或 Redis 等异步操作完成。在等待网络结果时，事件循环可以处理其他工作。

它不是把同一次登录的步骤自动并行执行。比如查用户完成后才校验密码，签发 Refresh 后才登记。

还要注意：`verify_password()` 是同步 bcrypt 调用，没有 `await`，当前代码会在事件循环线程里执行这个 CPU 操作。不能因为外层是 `async def`，就认为里面所有操作都是非阻塞的。

### 6.2 data: UserLogin

位置：[auth.py](D:/Project/learnLittle/app/schemas/auth.py:75)。

`UserLogin` 是请求数据结构，包含：

| 字段 | 必填吗 | 当前限制 |
| :--- | :--- | :--- |
| `username` | 是 | 字符串 |
| `password` | 是 | 字符串 |
| `device_id` | 否 | 默认 None，最长 64 字符 |
| `device_name` | 否 | 默认 None，最长 100 字符 |

FastAPI 根据这份结构，把请求 JSON 校验、转换成 `UserLogin` 对象，再供函数使用。

因此 `data.username` 就是用户提交的用户名。

当前登录 Schema 没有注册 Schema 的用户名格式和密码强度限制。不要把注册的字段约束自动套到登录上。

缺少必填字段、字段类型不符合要求或设备字段超长，会通过参数校验异常返回 HTTP 422，通常还没有执行到登录正文。

### 6.3 request: Request

这是 HTTP 请求对象，不是用户名密码对象。

它用于取请求头、User-Agent、客户端地址，以及 `request.app.state` 中的共享资源。

登录流程里主要把它传给 `store_device_session()`，保存设备相关信息。

### 6.4 db = Depends(get_db_session)

意思是：“执行这个路由需要数据库会话，请框架先通过 `get_db_session()` 准备好，再传给我。”

这叫依赖注入，不是客户端在 JSON 里传一个数据库对象。

位置：[database.py](D:/Project/learnLittle/app/db/database.py:47)。

`get_db_session()` 的过程：

```python
session_factory = request.app.state.db_session_factory
async with session_factory() as session:
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
```

`yield session` 把会话交给路由使用；依赖退出时，正常完成则提交，异常则回滚，最后关闭/归还资源。

数据库连接工厂在应用生命周期中准备，不是每次请求重新搭建一整套数据库连接池。

登录只读用户表，没有在 MySQL 新增“登录成功”记录。但它仍复用同一个会话管理模式。

重要：这个事务只覆盖 SQL。Redis 计数、白名单和设备写入不属于它，SQL 回滚不会自动撤销 Redis 操作。

## 7. 第一步：检查账号是否已被失败次数锁住

```python
await check_login_attempts(data.username)
```

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:117)。

内部核心：

```python
attempts = await get_redis().get(_attempts_key(username))
if attempts and int(attempts) >= MAX_LOGIN_ATTEMPTS:
    raise BusinessError(code=ErrorCode.ACCOUNT_LOCKED, http_status=403)
```

`get_redis()` 获取应用已初始化的共享 Redis 客户端，不是每次创建新的 Redis 服务器。

`_attempts_key(username)` 只负责拼一个键：

```text
login_attempts:alice
```

Redis 保存的计数字符串会被 `int()` 转成整数。没有记录意味着目前没有累计失败记录。

`MAX_LOGIN_ATTEMPTS` 是 5，因此计数达到 5 后，下一次进入这里就直接拒绝。

为什么放在密码校验前：已经被锁的账号不应该继续进行一次次密码尝试，也节省后面的查询和哈希校验。

实际效果：锁住之后，即便输入正确密码，也会先被这里拒绝。

## 8. 第二步：去 MySQL 找这个用户

```python
result = await db.execute(select(User).where(User.username == data.username))
user = result.scalar_one_or_none()
```

位置：[user.py](D:/Project/learnLittle/app/routers/user.py:193)。

逐段拆开：

| 片段 | 含义 |
| :--- | :--- |
| `User` | SQLAlchemy ORM 模型，对应 `users` 表 |
| `select(User)` | 构造查询用户记录的 SQL 语句 |
| `.where(...)` | 加筛选条件，只找输入的用户名 |
| `db.execute(...)` | 在这个数据库会话里执行查询 |
| `result` | 数据库查询结果容器，还不是直接的用户对象 |
| `.scalar_one_or_none()` | 取唯一的 ORM 用户对象；没查到时返回 None |

可以近似理解成：

```sql
SELECT * FROM users WHERE username = :username;
```

这里用 ORM 条件表达式传参数，不是把用户输入直接拼进 SQL 文本。

位置：[User 模型](D:/Project/learnLittle/app/models/user.py:21)。

`username` 有唯一约束和索引：唯一约束防止同名账号，索引支持按用户名查找。因此这里预期至多一个用户；如果数据异常出现多个结果，`scalar_one_or_none()` 不是随便拿第一个，而是会报错。

`user.uuid` 是账号的内部标识，`user.username` 是登录名，`user.password` 虽然字段叫 password，实际保存的是注册时生成的 bcrypt 哈希。

注意：这里按用户名查，不按邮箱查。填写邮箱不意味着可以用邮箱登录。

## 9. 第三步：判断用户存在且密码正确

```python
if not user or not verify_password(data.password, user.password):
    await record_login_failure(data.username)
    raise BusinessError(code=ErrorCode.PASSWORD_ERROR, http_status=401)
```

这里的 `or` 有短路逻辑。

如果 `user` 是 None，`not user` 已经成立，Python 不会再访问 `user.password`，因此不会因为用户不存在而访问空对象。

如果找到了用户，才执行 `verify_password()`。

为什么用户名不存在和密码错误都返回“用户名或密码错误”：避免通过不同提示直接告诉请求者某个用户名是否存在。

但不要夸大：当前用户不存在时跳过 bcrypt，两条路径的执行时间可能不同，因此这不是完整的时间侧信道防护。

### 9.1 verify_password()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:41)。

```python
return bcrypt.checkpw(
    plain_password.encode("utf-8"),
    hashed_password.encode("utf-8"),
)
```

输入是两个东西：这次提交的明文密码、数据库里已经保存的密码哈希。

`encode("utf-8")` 把 Python 字符串转换为 bytes，因为 bcrypt 接口使用字节数据。

`bcrypt.checkpw()` 利用已保存哈希中的参数和盐进行验证，返回 True 或 False。

不是把数据库密码解密出来，再跟输入密码比较。

如果保存的哈希格式不合法，当前函数捕获 `ValueError`，返回 False，把它视为校验失败。

### 9.2 为什么注册时要 hash_password()

它不是登录中直接调用的函数，但理解密码验证必须知道密码最初怎么保存。

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:36)。

```python
return bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt(),
).decode("utf-8")
```

`gensalt()` 生成盐；`hashpw()` 计算哈希；`decode()` 把结果转回字符串，方便写入数据库。

不同盐会让相同密码生成不同哈希，不能简单比较两次独立 `hash_password()` 的字符串是否相同来判断密码。

密码哈希用来验证，JWT 则用来代表登录后的身份，这两件事不要混在一起。

### 9.3 record_login_failure()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:124)。

```python
count = await redis.incr(_attempts_key(username))
if count == 1:
    await redis.expire(_attempts_key(username), 900)
```

`INCR`：计数加一；键不存在时按零开始，因此第一次失败得到 1。

`EXPIRE`：设置键的生存期，900 秒也就是 15 分钟。到期 Redis 自动删除计数。

为什么用 Redis：不用在用户表里为每次错误密码都更新账号记录，也不用自己写定时清理任务。

一个经常看错的细节：

```text
10:00 第一次失败，计数过期时间设为 10:15
10:08 第五次失败，计数变为 5，过期时间仍是 10:15
10:09 再次登录，直接被拒绝
10:15 计数到期，才可以继续尝试
```

所以实际是“首次失败起 15 分钟的计数窗口，计数到 5 后在剩余窗口内锁住”，不是“第五次失败以后重新锁完整 15 分钟”。

第五次失败本身仍走“密码错误”响应；下一次请求才在 `check_login_attempts()` 中得到“账户已锁定”。

计数增加和首次设置 TTL 是两条 Redis 命令，不是一个整体原子事务。这里是当前实现，不应当讲成完全没有并发/中断边界的方案。

## 10. 第四步：密码正确，清除失败次数

```python
await clear_login_attempts(data.username)
```

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:132)。

内部就是删除：

```text
login_attempts:<username>
```

这样之前输了两次错误密码、随后正确登录，不会把旧失败次数继续留到下一次。

此时只是“密码校验成功”，不是完整登录流程已经结束。后面的 Redis 登记如果失败，整个接口仍可能报错，而这里的计数已经清除了。

## 11. 第五步：同一设备旧 Refresh Token 作废

```python
if data.device_id:
    existing = await get_device_session(user.uuid, data.device_id)
    if existing and existing.get("jti"):
        await revoke_refresh_token(user.uuid, existing["jti"])
```

### 11.1 get_device_session()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:356)。

通过 Redis Hash 读取：

```text
session:<用户 UUID>:<设备 ID>
```

`_session_key()` 只是拼键；`HGETALL` 获取这个 Hash 中的所有字段。

不存在时返回 None；存在时整理为字典，其中 `jti` 是这个设备当前关联的 Refresh Token ID。

### 11.2 revoke_refresh_token()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:158)。

`_refresh_key(user_id, jti)` 拼出：

```text
refresh_token:<用户 UUID>:<Refresh JTI>
```

`revoke_refresh_token()` 删除这个白名单键。

为什么这么做：同一浏览器重复登录，不应每次都留下一个永远并行有效的旧续期凭证。用新 Refresh 替换旧 Refresh，维持该设备的当前续期关系。

注意，它只撤销这里找到的旧 Refresh Token，不会把所有旧 Access Token 立即拉黑。

为什么设备 ID 可选：这个接口也允许不带设备信息的客户端登录。代价是这些登录不会进入设备会话记录和设备数量限制，但 Refresh 仍会登记白名单。

## 12. 第六步：生成 Refresh Token

```python
refresh_token, refresh_jti = create_refresh_token(user.uuid)
```

这是 Python 的元组解包：函数返回两个值，分别放进两个变量。

### 12.1 create_refresh_token()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:87)。

过程：

```text
get_settings()
  -> 取得有效期配置
_create_token(user_id, "refresh", timedelta(days=...))
  -> 生成 JWT 字符串
decode_token(token)
  -> 取出其中的 jti
return token, jti
```

它会解码刚生成的 Token，是因为 `_create_token()` 只返回字符串，没有同时返回生成的 JTI。不是在登录时校验用户提供的旧 Refresh。

### 12.2 get_settings()

位置：[config.py](D:/Project/learnLittle/app/config.py:192)。

`Settings` 从环境变量和 `.env` 读取配置，`@lru_cache` 让 `get_settings()` 在同一进程内复用已解析对象。

所以多次调用它一般不是反复读磁盘。

当前本地有效值已经检查过：Access 30 分钟，Refresh 7 天，最多 5 个已登记设备，JWT 算法 HS256。修改 `.env` 后，运行进程的缓存不会自动因为文件修改而失效，需要重新加载相应进程。

### 12.3 _create_token()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:65)。

核心内容：

```python
now = datetime.now(timezone.utc)
payload = {
    "sub": user_id,
    "iat": now,
    "exp": now + lifetime,
    "jti": str(uuid.uuid4()),
    "type": token_type,
}
return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
```

逐字段解释：

| 字段 | 含义 | 为什么需要 |
| :--- | :--- | :--- |
| `sub` | 用户 UUID | 后续请求知道这份凭证属于谁 |
| `iat` | 签发时间 | 表示什么时候生成 |
| `exp` | 过期时间 | 超过时间不能继续使用 |
| `jti` | 这份 Token 的唯一 ID | 单独登记、轮换或撤销一份凭证 |
| `type` | access / refresh | 防止把续期凭证直接当业务访问凭证 |

用户 UUID 和 JTI 不一样：同一用户每次签发 Token，`sub` 相同，但 `jti` 不同。

`jwt_secret` 是服务器签名密钥，不会返回前端，也不是用户密码。

这里的 JWT 是签名凭证，不是加密容器；不能认为把敏感信息放进 payload 就会变成不可见。当前 payload 没有存密码。

`datetime.now(timezone.utc)` 使用带时区的 UTC，避免用各机器本地时间表达有效期。

### 12.4 decode_token()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:97)。

`jwt.decode()` 在这里不只是拆字符串，还使用配置密钥和允许的算法验证签名及有效期。

过期 -> `TOKEN_EXPIRED`，业务码 40101。

其他无效 Token -> `TOKEN_INVALID`，业务码 40102。

两者 HTTP 状态都是 401，但前端会按业务码决定是否尝试刷新。这就是为什么不能把所有 401 都当成“密码错误”。

## 13. 为什么要 Access + Refresh 两个 Token

| Token | 当前有效期 | 在哪里用 |
| :--- | :--- | :--- |
| Access Token | 30 分钟 | 获取资料、读取笔记等需要身份的业务请求 |
| Refresh Token | 7 天 | `/auth/refresh` 换取新 Access 和新 Refresh |

可以先这样理解：

- Access 是短期访问凭证。
- Refresh 是更长期的续期凭证，不能直接用于普通业务接口。

只用一个 7 天访问凭证，泄露后访问权限可能持续很久；只用一个 30 分钟凭证且没有续期机制，用户又需要频繁输入密码。

双 Token 是在访问期限和登录体验之间做分工，不意味着凭证泄露后自动安全。当前前端把两种 Token 都保存在 localStorage，前端脚本安全仍然重要。

## 14. 第七步：把 Refresh JTI 登记进白名单

```python
await store_refresh_token(user.uuid, refresh_jti)
```

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:148)。

实际调用：

```python
await redis.setex(
    _refresh_key(user_id, jti),
    _refresh_ttl_seconds(),
    "1",
)
```

`SETEX` 同时设置值和过期时间。

`_refresh_ttl_seconds()` 把配置的天数乘以 86400，当前 7 天是 604800 秒。

Redis 不保存完整 Refresh JWT，而是用“用户 ID + JTI”登记一个标记 `"1"`，表示这份续期凭证目前有效。

为什么签了 JWT 还要白名单：

```text
JWT 签名和有效期正确
  并且
Redis 白名单记录仍存在
  才允许刷新
```

只靠签名和有效期，没法通过删除某个 Redis 记录来立即禁止这个 Refresh 继续续期。白名单让注销、改密码、设备撤销和轮换可以主动取消它。

相关函数 `verify_refresh_token()` 读取这个键并转成布尔值，不负责 JWT 签名验证；刷新接口必须先 `decode_token()`，再查白名单。

## 15. 第八步：写设备会话

```python
if data.device_id:
    await store_device_session(
        user.uuid,
        data.device_id,
        refresh_jti,
        device_name=data.device_name,
        request=request,
    )
```

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:324)。

`store_device_session()` 做这些事：

1. `get_redis()` 获取客户端，生成当前 UTC 时间字符串。
2. 从请求头取 User-Agent。
3. 如果客户端没给设备名称，通过 `parse_device_name()` 生成名称。
4. `_session_key()` 构造设备 Hash 键。
5. `_refresh_ttl_seconds()` 得到会话过期时长。
6. `HGET created_at` 读取旧创建时间，重复登录时保留它。
7. 用多个 `HSET` 写设备字段。
8. `EXPIRE` 设置设备 Hash 过期时间。
9. `SADD` 把设备 ID 放进用户的设备集合。
10. 给集合也设置过期时间。

设备 Hash 示例，值仅为示意：

```text
session:user-A:browser-A
  jti         -> refresh-JTI-A
  device_name -> Chrome / Windows
  ip          -> 127.0.0.1
  user_agent  -> 浏览器 User-Agent
  created_at  -> 第一次建立该设备记录的时间
  last_used   -> 本次登录时间
```

设备集合：

```text
user_sessions:user-A
  browser-A
  browser-B
```

为什么同时用 Hash 和 Set：

Hash 保存一个设备的字段；Set 保存这个用户有哪些设备 ID，方便列设备和限制数量，而不是每次扫描所有用户的所有设备键。

`_sessions_set_key()` 只是构造 `user_sessions:<user_id>`。

### 15.1 parse_device_name()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:285)。

根据 User-Agent 中的关键词判断操作系统、浏览器，拼出可读名称；没有足够信息则使用 Unknown。

这个名称只用于展示，不是安全认证。当前前端通常已经传了名称，后端只在未传时兜底。

### 15.2 _client_ip()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:315)。

优先取 `X-Forwarded-For` 第一个地址，没有则取 `request.client.host`，没有请求则返回空字符串。

这是为了反向代理场景下记录客户端地址。但当前函数本身没有验证转发头来源是否可信，部署时不能任由外部请求伪造转发头并当作可信来源。

登录的这个 IP 记录和限流身份使用的 IP 逻辑不同，不要认为二者用了同一套地址解析。

### 15.3 created_at 和 last_used 为什么两个时间

`created_at` 表示当前记录最初建立的时间；`last_used` 表示最近登录或刷新时的时间。

重复登录时前者保留、后者更新。

当前不是每次读取笔记都会更新设备 `last_used`，别把它解释成“设备所有活动的实时最近时间”。

## 16. 第九步：检查设备数量上限

```python
await enforce_session_limit(user.uuid, settings.max_device_sessions)
```

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:424)。

过程：

```text
SMEMBERS 取得这个用户所有设备 ID
  -> 数量未超过上限：直接返回
  -> 超过上限：读取各设备 created_at
  -> 按创建时间从旧到新排序
  -> 删除超过数量的最旧设备
     删除其 Refresh 白名单
     删除其设备 Hash
     从设备 Set 移除设备 ID
```

当前上限是 5 个登记设备。

为什么放在设备写入后：先把这次登录计入集合，再判断新的总数是否超限。

为什么撤销旧 Refresh：不能只把旧设备从展示列表删掉，却让它继续一直续期。

但当前撤销的是 Refresh，不是全部 Access。因此旧设备已有且没有进入黑名单的 Access Token，可能继续访问到它自然过期。

排序依据是 `created_at`，不是 `last_used`。所以“最早登录过的设备”与“最近最少使用的设备”不是一回事；重复登录保留创建时间，也可能影响哪个设备被淘汰。

这里是多条 Redis 命令组成的流程，不是一次原子操作；并发登录时不能把设备数量限制描述成严格无竞争的保证。

## 17. 第十步：生成 Access Token，封装返回

```python
return success_response(
    data=TokenResponse(
        access_token=create_access_token(user.uuid),
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        device_id=data.device_id,
    ).model_dump()
)
```

### 17.1 create_access_token()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:79)。

读取配置，调用 `_create_token(user_id, "access", timedelta(minutes=30))`。

同样包含用户 ID、签发/过期时间、独立 JTI 和类型，但用途、有效期与 Refresh 不同。

登录时不把新 Access 登记到 Refresh 白名单。它后续通过签名、有效期、类型和 Access 黑名单校验。

### 17.2 TokenResponse

位置：[auth.py](D:/Project/learnLittle/app/schemas/auth.py:88)。

这是后端响应数据的 Pydantic 模型，不是数据库表。

构造它可以统一登录和刷新接口返回的数据结构，避免随手返回不同字段名。

`model_dump()` 把 Pydantic 对象转成 Python 字典，供 JSON 响应使用。

`expires_in` 的单位是秒，所以分钟数乘以 60。当前是 1800 秒。

`token_type="bearer"` 表示后续按 Bearer 方式携带访问凭证；它不是 JWT payload 中 `type="access"` 的同一个字段。

### 17.3 success_response()

位置：[success_response.py](D:/Project/learnLittle/app/core/success_response.py:12)。

返回统一外层：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "access_token": "<省略>",
    "refresh_token": "<省略>",
    "token_type": "bearer",
    "expires_in": 1800,
    "device_id": "<浏览器设备 ID>"
  },
  "request_id": "<本次响应标识>"
}
```

`code=0` 是业务成功，不是 HTTP 状态码。这个正常响应的 HTTP 状态是 200。

`request_id` 不指定时自动生成 UUID；在这里它只是响应标识，不等于已经贯穿所有入口、日志和下游调用的完整链路追踪。

## 18. 错误是怎么一路回到页面的

例如密码错误：

```python
raise BusinessError(code=ErrorCode.PASSWORD_ERROR, http_status=401)
```

这不是“返回一个普通变量”，而是抛出异常，立即中断后面的正常流程。

`BusinessError` 保存业务码、默认/自定义消息、详情和 HTTP 状态。

位置：[failed_response.py](D:/Project/learnLittle/app/core/failed_response.py:95)。

`register_exception_handlers()` 中的 `business_error_handler()` 接住它，用 `failed_response()` 生成 JSON，按异常指定的 HTTP 状态返回。

位置：[exception_handlers.py](D:/Project/learnLittle/app/core/exception_handlers.py:21)。

典型结果：

```json
{
  "code": 40103,
  "message": "用户名或密码错误",
  "detail": null,
  "request_id": "<省略>"
}
```

前端 Axios 响应拦截器把它转换为 `ApiError`，登录页面 `catch` 读取 `err.message` 显示。

常见分支：

| 原因 | HTTP 状态 | 业务码 | 发生位置 |
| :--- | :--- | :--- | :--- |
| 参数校验失败 | 422 | 40002 | FastAPI/Pydantic 校验和异常处理器 |
| 请求太频繁 | 429 | 42901 / 42902 | 限流中间件 |
| 用户不存在或密码错误 | 401 | 40103 | `login()` |
| 累计失败锁定 | 403 | 40104 | `check_login_attempts()` |
| 数据库、Redis 等未预期故障 | 通常 500 | 50001 | 通用异常处理器 |

业务码的数字前缀不一定等于实际 HTTP 状态。例如锁定业务码是 40104，但 HTTP 状态是 403。

前端 `request()` 成功时返回外层的 `data`，所以登录页拿到的是 `tokens.access_token`，不是 `tokens.data.access_token`。

## 19. 登录成功后，后端怎么知道后续请求是谁

前端 `setTokens()` 把 Token 存到 Zustand 状态，由 persist 中间件写入 `learnlittle-auth` localStorage。

位置：[useAuthStore.ts](D:/Project/learnLittle/front/src/stores/useAuthStore.ts:28)。

后续调用：

```text
GET /api/v1/user/me
Authorization: Bearer <Access Token>
```

路由 `get_me()` 依赖 `get_current_user_id()`：

```python
user_id: str = Depends(get_current_user_id)
```

位置：[user.py](D:/Project/learnLittle/app/routers/user.py:306)。

### 19.1 get_current_token_payload()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:200)。

检查顺序：

```text
有没有 Authorization
  -> 格式是否是 Bearer + Token
  -> decode_token() 验签名和有效期
  -> payload.type 必须是 access
  -> is_token_blacklisted(jti) 确认没被撤销
  -> 返回 payload
```

因此拿 Refresh Token 去普通业务接口，即使 JWT 签名有效，也会因为类型错误被拒绝。

`is_token_blacklisted()` 读取 `token_blacklist:<jti>` 判断是否被注销；`_blacklist_key()` 只负责拼键。

### 19.2 get_current_user_id()

位置：[auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py:235)。

依赖前面已经校验过的 payload，从 `sub` 取得用户 UUID；没有 `sub` 则拒绝。

业务路由不用每次都复制 Bearer 解析和验签逻辑，直接获取用户 ID，再限制只能访问该用户的数据。

### 19.3 get_me()

用用户 UUID 查 MySQL；找不到返回用户不存在，否则用 `UserInfo` 从 ORM 对象构造返回数据。

`UserInfo` 没有密码字段，因此不会把 `user.password` 哈希随资料一起返回。

前端保存资料后才跳首页。前端 `RequireAuth` 只是检查是否保存着 Access Token，不会完成后端那一整套验证；页面能打开不表示后端已经确认凭证有效。

## 20. Access 过期后的续期流程

这不是 `login()` 每次都会执行的步骤，而是理解为什么登录返回 Refresh 所需的后续流程。

前端响应拦截器遇到 HTTP 401 且业务码 40101，会调用 `tryRefresh()`。

位置：[client.ts](D:/Project/learnLittle/front/src/api/client.ts:30)。

`tryRefresh()`：

1. 读取保存的 Refresh。
2. 使用独立的 `axios.post()` 请求 `/api/v1/auth/refresh`。
3. 成功时保存新的 Access 和 Refresh。
4. 失败时清空登录态并回登录页。
5. 原请求最多自动重放一次，由 `_retried` 避免无限刷新重试。

为什么用 `refreshing` 保存一个共享 Promise：多个请求同时发现 Access 过期时，尽量共用同一次刷新，避免在当前页面中同时拿同一份 Refresh 轮换多次。

这只是同一 JavaScript 运行环境内的协调，不自动解决多个浏览器标签页之间的刷新竞争。

后端 `refresh()`：

```text
decode_token(refresh)
  -> 类型必须 refresh
  -> sub 和 jti 必须存在
  -> verify_refresh_token() 查白名单
  -> revoke_refresh_token() 撤销旧 Refresh
  -> create_refresh_token() 生成新 Refresh
  -> store_refresh_token() 登记新 Refresh
  -> update_device_session() 更新设备 JTI / 最近使用时间 / IP / TTL
  -> create_access_token() 生成新 Access
  -> 返回
```

位置：[user.py](D:/Project/learnLittle/app/routers/user.py:232)。

`update_device_session()` 只更新已有设备记录，不会在记录缺失时创建新记录。

为什么轮换：每次续期后旧 Refresh 都不再能通过白名单校验，而不是同一份 7 天凭证反复无限使用。

但当前白名单“检查再删除”是分开的命令，不是原子消费，也没有在这里实现完整的令牌家族重用检测。不要把它说成彻底消除所有凭证重放。

每次刷新签发的新 Refresh 又有配置的 7 天有效期；这里没有另设从首次登录开始不可延长的总会话期限。

## 21. 为什么有 Refresh 白名单，又有 Access 黑名单

二者方向不同：

- Refresh：必须在白名单里才允许续期。
- Access：签名、有效期、类型正确，并且不在黑名单里，才允许访问。

`logout()` 会把当前 Access 的 JTI 放进黑名单，并撤销当前 Refresh，删除设备会话。

`blacklist_access_token()` 用 `remaining_ttl_seconds()` 计算的剩余有效期设置 Redis TTL。

这样 Access 自然过期后就不必永久保留黑名单记录。

`remaining_ttl_seconds()` 是 `payload["exp"] - time.time()` 转成整数秒，不会重新给 Token 延期。

改密码使用 `revoke_all_refresh_tokens()`：扫描并删除该用户所有 Refresh 白名单，然后 `_clear_all_device_sessions()` 删除设备记录。当前不是把该用户所有已签发 Access 都立即拉黑，所以已有 Access 仍可能可用到自然过期。

这些函数不属于一次正常 `login()` 的执行步骤，但解释了登录创建的数据后续怎么被撤销。

## 22. 设计目的和当前实现边界，要分开看

这部分不是让你现在重写项目，而是避免把注释当成完整保证。

| 设计目的 | 当前代码真正做到的事 |
| :--- | :--- |
| 阻止重复猜密码 | 按用户名计数，首次失败设置 15 分钟窗口；锁定存在被他人触发的可能 |
| 相同错误提示隐藏账号存在性 | 文案一致，但不存在用户时不执行 bcrypt，耗时路径不同 |
| 管理设备 | 按浏览器提供的 device_id 记录，不是可靠硬件认证；不传可跳过登记 |
| 最多 5 个设备 | 限制已登记集合，按 created_at 淘汰，多命令非原子 |
| 踢掉旧设备 | 删除设备记录和 Refresh，未统一立即撤销旧 Access |
| 有用户状态字段 | `login()` 目前没检查 `user.status`，也没检查邮箱已验证才允许登录 |
| SQL 事务保护登录 | 只保护 SQL 会话，不覆盖 Redis 登记和凭证撤销 |
| 异步接口提高等待期吞吐 | Redis/SQL 使用 await，但 bcrypt 校验当前为同步执行 |
| Token 自动续期 | 当前页面共享刷新 Promise，不能自动解决所有跨标签页/后端并发竞争 |
| 登录态持久化方便刷新页面 | localStorage 不是 HttpOnly Cookie；不能把其存储内容当后端可信状态 |

另外，`auth_utils.py` 顶部有“设备会话管理暂未实现”的旧说明，但下面已经有实现。阅读时以实际函数和调用为准，不能据此认为当前没有设备管理。

## 23. 用一个例子串起来

假设有用户 `alice`，数据库中：

```text
uuid = user-A
username = alice
password = <bcrypt 哈希，不是明文>
```

她在设备 `browser-A` 输入正确密码。

成功过程：

```text
1. 请求频率没有超限。
2. FastAPI 把 JSON 转成 UserLogin，准备数据库会话。
3. Redis 的 login_attempts:alice 不存在，允许尝试。
4. MySQL 查到 alice。
5. bcrypt 校验通过。
6. 删除 alice 的旧失败计数。
7. 若 browser-A 原先有 Refresh，删除那份旧白名单。
8. 生成 Refresh：sub=user-A，jti=refresh-JTI-new，type=refresh。
9. Redis 写 refresh_token:user-A:refresh-JTI-new -> 1。
10. 写 session:user-A:browser-A，并把 browser-A 加入设备集合。
11. 设备总数没有超过 5，无需淘汰。
12. 生成 Access：sub=user-A，jti=access-JTI-new，type=access。
13. 返回两份 Token，Access 有效期 1800 秒。
14. 前端保存 Token，携带 Access 请求 /user/me。
15. 后端验 Access，取出 user-A，返回资料。
16. 前端保存资料，进入首页。
```

密码错误时：

```text
查到用户
  -> bcrypt 返回 False
  -> Redis 失败次数 +1
  -> 抛出用户名或密码错误
  -> 不生成 Token，不写本次设备会话，不跳首页
```

锁定时：

```text
check_login_attempts() 发现计数 >= 5
  -> 直接抛出锁定异常
  -> 根本不查用户、不比较密码
```

## 24. 所有相关自定义函数速查

这里只列登录及其直接配套流程，不把整个项目其他功能混进来。

| 函数 | 作用 | 属于哪段 |
| :--- | :--- | :--- |
| `create_app()` / `lifespan()` | 登记路由、初始化数据库工厂和 Redis | 应用准备 |
| `create_database_engine()` | 创建异步数据库引擎和连接池配置 | 应用准备 |
| `build_database_url()` | 用结构化配置构造数据库地址 | 应用准备 |
| `create_session_factory()` | 创建会话工厂 | 应用准备 |
| `init_redis()` / `create_redis_client()` | 建 Redis 客户端并确认连通 | 应用准备 |
| `RateLimitMiddleware.dispatch()` | 请求进入路由前的限流 | 登录入口 |
| `identity_for()` | 选择计数身份 | 限流 |
| `endpoint_limit_for()` | 选择路径额度 | 限流 |
| `check_rate_limit()` / `_hit()` | 增加并检查计数 | 限流 |
| `get_db_session()` | 给本次请求提供 SQL 会话并处理退出 | 依赖 |
| `login()` | 串起用户名密码验证和凭证签发 | 主流程 |
| `check_login_attempts()` / `_attempts_key()` | 读账号失败计数并判断锁定 | 密码验证前 |
| `verify_password()` | 输入密码对照保存哈希 | 密码验证 |
| `hash_password()` | 注册/改密码时生成保存用哈希 | 密码前置知识 |
| `record_login_failure()` | 错误次数增加、首次设 TTL | 失败路径 |
| `clear_login_attempts()` | 删除旧错误次数 | 成功路径 |
| `get_device_session()` / `_session_key()` | 获取同设备旧会话 | 设备轮换 |
| `revoke_refresh_token()` / `_refresh_key()` | 删除指定续期凭证白名单 | 设备轮换/刷新 |
| `create_refresh_token()` | 签发 Refresh 并返回 JTI | 凭证生成 |
| `_create_token()` | 构造 payload 并签名 | 凭证生成 |
| `get_settings()` | 缓存和提供配置 | 多处 |
| `decode_token()` | 验签、检查有效期并返回 payload | 多处 |
| `store_refresh_token()` / `_refresh_ttl_seconds()` | 保存续期白名单并设置 TTL | 登记 |
| `store_device_session()` / `_sessions_set_key()` | 写设备字段和设备集合 | 登记 |
| `parse_device_name()` / `_client_ip()` | 设备名兜底、地址记录 | 登记辅助 |
| `enforce_session_limit()` | 超限淘汰最早创建的登记设备 | 设备上限 |
| `create_access_token()` | 签发短期访问凭证 | 返回前 |
| `success_response()` | 包装统一成功响应 | 返回 |
| `BusinessError.__init__()` | 定义业务异常内容 | 失败路径 |
| `business_error_handler()` / `failed_response()` | 转换异常为 HTTP JSON | 失败路径 |
| `validation_error_handler()` | 转换参数校验异常 | 参数失败 |
| `general_exception_handler()` | 未预期错误兜底，不返回堆栈 | 系统失败 |
| `get_current_token_payload()` | 校验后续请求的 Access | 登录后 |
| `get_current_user_id()` | 从已校验 payload 取得用户 ID | 登录后 |
| `is_token_blacklisted()` / `_blacklist_key()` | 检查 Access 撤销记录 | 登录后 |
| `get_me()` | 按当前用户 ID 返回安全的资料结构 | 登录后 |
| `refresh()` / `verify_refresh_token()` | 检查续期条件并轮换凭证 | 续期 |
| `update_device_session()` | 续期后更新现有设备记录 | 续期 |
| `logout()` / `blacklist_access_token()` | 注销当前 Access，撤销 Refresh | 退出 |
| `remaining_ttl_seconds()` | 计算 Access 剩余秒数 | 退出辅助 |
| `delete_device_session()` | 删除 Hash 和集合成员 | 退出/撤销设备 |
| `revoke_all_refresh_tokens()` / `_clear_all_device_sessions()` | 清掉用户全部续期凭证和设备记录 | 改密码 |
| `handleSubmit()` / `authApi.login()` / `request()` | 前端提交请求、解包响应 | 前端边界 |
| `getDeviceId()` / `getDeviceName()` | 提供设备标识和名称 | 前端边界 |
| `setTokens()` / `setUser()` / `clear()` | 管理前端登录状态 | 前端边界 |
| `tryRefresh()` | 前端共用续期请求、更新 Token | 前端续期 |

## 25. 推荐你对着代码这样读

第一次只读 [login()](D:/Project/learnLittle/app/routers/user.py:187)，把它理解成四个阶段：

```text
验账号密码 -> 处理旧设备凭证 -> 创建并登记新凭证 -> 返回
```

第二次只读 [verify_password()](D:/Project/learnLittle/app/utils/auth_utils.py:41) 和失败计数那三函数，理解登录怎么成功或失败。

第三次读 [_create_token()](D:/Project/learnLittle/app/utils/auth_utils.py:65) 和 Refresh 白名单，理解凭证为什么需要服务端状态。

第四次读设备会话，再读 [get_current_user_id()](D:/Project/learnLittle/app/utils/auth_utils.py:235)，理解登录后的接口如何确定用户。

最后读刷新和退出，不要第一遍就把它们和正常登录步骤混在一起。

你只要先记住这句话，就能抓住主线：

**登录时用用户名密码证明自己，登录后用 Access 访问业务，Access 过期用 Refresh 续期，Redis 决定哪些凭证已被撤销。**
