# app/utils/auth_utils.py

[源码](D:/Project/learnLittle/app/utils/auth_utils.py) | [任务流程 02](D:/Project/learnLittle/docs/backend-tutorial/02-account.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

密码、JWT、Redis 安全状态、短期聊天票和设备会话；顶部旧注释不代表设备功能缺失。

## 本文件导航

- [hash_password](#fn-0b73ebf9c2b07d2c)
- [verify_password](#fn-11e9d891c3a7701c)
- [validate_password_strength](#fn-51d1ed98afe93d7c)
- [_create_token](#fn-5cd4a76c5faf14fe)
- [create_access_token](#fn-22f4f9a65c99e1d1)
- [create_refresh_token](#fn-57a23dfd8c4c4e0b)
- [decode_token](#fn-b11aa6a67ce0ffa6)
- [_attempts_key](#fn-838ffb5e8b059d2b)
- [check_login_attempts](#fn-8d35fd2d8050e40d)
- [record_login_failure](#fn-ed89c8b20ec7ac48)
- [clear_login_attempts](#fn-fed325924e40f253)
- [_refresh_key](#fn-afe91ab23b7505cc)
- [_refresh_ttl_seconds](#fn-ccabbb4a89d871de)
- [store_refresh_token](#fn-e64d53bef1f02a5e)
- [verify_refresh_token](#fn-e9169d195f2ed55e)
- [revoke_refresh_token](#fn-40007bef15f1796f)
- [revoke_all_refresh_tokens](#fn-1f513e547190c5cf)
- [_blacklist_key](#fn-b8f094db8c2159cb)
- [blacklist_access_token](#fn-31512e27c453549b)
- [is_token_blacklisted](#fn-a7780e391404ca50)
- [get_current_token_payload](#fn-4dcb1a4b3331d27a)
- [get_current_user_id](#fn-544c283f52af2b8c)
- [create_sse_token](#fn-b66dc598c8e1ceb2)
- [get_chat_user_id](#fn-c06f5b4116da761c)
- [remaining_ttl_seconds](#fn-06f2576e322d7fd5)
- [_session_key](#fn-b35c1400683087e5)
- [_sessions_set_key](#fn-19de68f46e9dedb7)
- [parse_device_name](#fn-7d390c6a40f175f9)
- [_client_ip](#fn-82ae8b64abf5569f)
- [store_device_session](#fn-d65b5c9460cefbbe)
- [get_device_session](#fn-0d24f2ed608e535f)
- [update_device_session](#fn-2a4c6fe8928b0034)
- [delete_device_session](#fn-671a952d52a7aee1)
- [list_user_sessions](#fn-5956d1fdeef6c162)
- [list_user_sessions.<lambda@420:22>](#fn-d0c38c1db2b512da)
- [enforce_session_limit](#fn-f041151bc2564d9a)
- [enforce_session_limit.<lambda@435:19>](#fn-690bdfeb8009fcd4)
- [_clear_all_device_sessions](#fn-694b4df95272c775)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
MAX_LOGIN_ATTEMPTS = 5

LOCKOUT_DURATION_SECONDS = 900
```

<a id="fn-0b73ebf9c2b07d2c"></a>

## hash_password

源码：[L36](D:/Project/learnLittle/app/utils/auth_utils.py:36)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

对明文 UTF-8 密码使用 bcrypt 自动盐生成哈希字符串。返回值可落 User.password，不能由此还原原密码。

**输入与签名**

```python
def hash_password(password: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode
bcrypt.hashpw
password.encode
bcrypt.gensalt
```

<a id="fn-11e9d891c3a7701c"></a>

## verify_password

源码：[L41](D:/Project/learnLittle/app/utils/auth_utils.py:41)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

比较明文与 bcrypt 哈希，格式非法的 ValueError 视为不匹配。调用者据此处理失败计数，本函数不查用户、不修改 Redis。

**输入与签名**

```python
def verify_password(plain_password: str, hashed_password: str) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
return False
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
bcrypt.checkpw
plain_password.encode
hashed_password.encode
```

<a id="fn-51d1ed98afe93d7c"></a>

## validate_password_strength

源码：[L51](D:/Project/learnLittle/app/utils/auth_utils.py:51)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

检查至少八位，同时有字母和数字，返回布尔值与失败原因。它只是当前项目策略，不是所有强密码条件的证明。

**输入与签名**

```python
def validate_password_strength(password: str) -> tuple[bool, str]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return (False, '密码长度至少 8 位')
return (False, '密码必须包含字母')
return (False, '密码必须包含数字')
return (True, '')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
len
any
c.isalpha
c.isdigit
```

<a id="fn-5cd4a76c5faf14fe"></a>

## _create_token

源码：[L65](D:/Project/learnLittle/app/utils/auth_utils.py:65)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

按用户、type 和寿命创建带 sub/iat/exp/jti 的签名 JWT，配置决定算法和密钥。返回字符串，白名单登记由调用者另做。

**输入与签名**

```python
def _create_token(user_id: str, token_type: str, lifetime: timedelta) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
datetime.now
str
uuid.uuid4
jwt.encode
```

<a id="fn-22f4f9a65c99e1d1"></a>

## create_access_token

源码：[L79](D:/Project/learnLittle/app/utils/auth_utils.py:79)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

以 access 类型和分钟寿命调用底层签发器。短期访问身份检查还需黑名单，不是只要签名对就永远可用。

**输入与签名**

```python
def create_access_token(user_id: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _create_token(user_id, 'access', timedelta(minutes=settings.access_token_expire_minutes))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
_create_token
timedelta
```

<a id="fn-57a23dfd8c4c4e0b"></a>

## create_refresh_token

源码：[L87](D:/Project/learnLittle/app/utils/auth_utils.py:87)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

生成 refresh JWT 并解码取 jti，返回二元组供路由登记白名单。签发本身不使该 refresh 自动进入 Redis。

**输入与签名**

```python
def create_refresh_token(user_id: str) -> tuple[str, str]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return (token, decode_token(token)['jti'])
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
_create_token
timedelta
decode_token
```

<a id="fn-b11aa6a67ce0ffa6"></a>

## decode_token

源码：[L97](D:/Project/learnLittle/app/utils/auth_utils.py:97)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

用配置算法验证 JWT 与过期时间，分别把过期和非法转换为 401 业务错误。这里不判断 access/refresh/sse 业务类型，也不检查白名单。

**输入与签名**

```python
def decode_token(token: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
jwt.decode
BusinessError
```

<a id="fn-838ffb5e8b059d2b"></a>

## _attempts_key

源码：[L113](D:/Project/learnLittle/app/utils/auth_utils.py:113)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

把用户名编码进登录失败计数键。锁定是用户名级状态，不是当前浏览器私有计数。

**输入与签名**

```python
def _attempts_key(username: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'login_attempts:{username}'
```

<a id="fn-8d35fd2d8050e40d"></a>

## check_login_attempts

源码：[L117](D:/Project/learnLittle/app/utils/auth_utils.py:117)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

读取失败次数，达到五次即抛锁定错误，路由会在查密码前调用。正确密码也不能绕过仍有效的计数窗口。

**输入与签名**

```python
async def check_login_attempts(username: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().get
get_redis
_attempts_key
int
BusinessError
```

<a id="fn-ed89c8b20ec7ac48"></a>

## record_login_failure

源码：[L124](D:/Project/learnLittle/app/utils/auth_utils.py:124)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

INCR 用户失败计数，第一次失败设置 900 秒 TTL。后续失败不在此每次重新开始整个窗口。

**输入与签名**

```python
async def record_login_failure(username: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
redis.incr
_attempts_key
redis.expire
```

<a id="fn-fed325924e40f253"></a>

## clear_login_attempts

源码：[L132](D:/Project/learnLittle/app/utils/auth_utils.py:132)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

登录成功后删除用户名失败计数。只清此项，不撤销其他设备或其他安全状态。

**输入与签名**

```python
async def clear_login_attempts(username: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().delete
get_redis
_attempts_key
```

<a id="fn-afe91ab23b7505cc"></a>

## _refresh_key

源码：[L140](D:/Project/learnLittle/app/utils/auth_utils.py:140)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

把 user_id 与 refresh jti 组成白名单键。不同用户、不同 refresh 各有独立记录。

**输入与签名**

```python
def _refresh_key(user_id: str, jti: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'refresh_token:{user_id}:{jti}'
```

<a id="fn-ccabbb4a89d871de"></a>

## _refresh_ttl_seconds

源码：[L144](D:/Project/learnLittle/app/utils/auth_utils.py:144)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

将配置中的 refresh 天数换算成秒。白名单与设备状态使用这个 TTL，而不是 access 的分钟寿命。

**输入与签名**

```python
def _refresh_ttl_seconds() -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return get_settings().refresh_token_expire_days * 86400
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
```

<a id="fn-e64d53bef1f02a5e"></a>

## store_refresh_token

源码：[L148](D:/Project/learnLittle/app/utils/auth_utils.py:148)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

以 TTL 写入 refresh 白名单，值为存在性标记。只有登记的票才能通过刷新路由的后续检查。

**输入与签名**

```python
async def store_refresh_token(user_id: str, jti: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().setex
get_redis
_refresh_key
_refresh_ttl_seconds
```

<a id="fn-e9169d195f2ed55e"></a>

## verify_refresh_token

源码：[L153](D:/Project/learnLittle/app/utils/auth_utils.py:153)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

读取指定用户/jti 白名单是否存在并返回 bool。JWT 签名和类型需在调用它之前另行验证。

**输入与签名**

```python
async def verify_refresh_token(user_id: str, jti: str) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return bool(await get_redis().get(_refresh_key(user_id, jti)))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
bool
get_redis().get
get_redis
_refresh_key
```

<a id="fn-40007bef15f1796f"></a>

## revoke_refresh_token

源码：[L158](D:/Project/learnLittle/app/utils/auth_utils.py:158)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

删除单枚 refresh 白名单，轮换/注销时调用。不会自动删除对应 access 黑名单之外的所有访问凭证。

**输入与签名**

```python
async def revoke_refresh_token(user_id: str, jti: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().delete
get_redis
_refresh_key
```

<a id="fn-1f513e547190c5cf"></a>

## revoke_all_refresh_tokens

源码：[L163](D:/Project/learnLittle/app/utils/auth_utils.py:163)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

SCAN 当前用户所有 refresh 键并删除，再清理设备会话。是撤销刷新能力，不是枚举所有已发 access 并拉黑。

**输入与签名**

```python
async def revoke_all_refresh_tokens(user_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
redis.scan
redis.delete
_clear_all_device_sessions
```

<a id="fn-b8f094db8c2159cb"></a>

## _blacklist_key

源码：[L181](D:/Project/learnLittle/app/utils/auth_utils.py:181)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

以 access jti 组成黑名单键。和按 user_id 组织的 refresh 白名单用途相反。

**输入与签名**

```python
def _blacklist_key(jti: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'token_blacklist:{jti}'
```

<a id="fn-31512e27c453549b"></a>

## blacklist_access_token

源码：[L185](D:/Project/learnLittle/app/utils/auth_utils.py:185)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

剩余寿命大于零时写黑名单并设置剩余 TTL，已过期则不再写。只撤销传入 jti 的 access。

**输入与签名**

```python
async def blacklist_access_token(jti: str, remaining_ttl_seconds: int) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().setex
get_redis
_blacklist_key
max
```

<a id="fn-a7780e391404ca50"></a>

## is_token_blacklisted

源码：[L192](D:/Project/learnLittle/app/utils/auth_utils.py:192)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

查询 access jti 是否在黑名单，返回布尔值。不存在表示没有被此机制撤销，不表示 Token 的其他条件都合法。

**输入与签名**

```python
async def is_token_blacklisted(jti: str) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return bool(await get_redis().get(_blacklist_key(jti)))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
bool
get_redis().get
get_redis
_blacklist_key
```

<a id="fn-4dcb1a4b3331d27a"></a>

## get_current_token_payload

源码：[L200](D:/Project/learnLittle/app/utils/auth_utils.py:200)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

解析 Authorization 的 Bearer 格式，校验签名/过期/access 类型/黑名单，返回完整 payload。是普通受保护接口共用的 Depends。

**输入与签名**

```python
async def get_current_token_payload(authorization: str | None=Header(default=None)) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return payload
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Header
BusinessError
authorization.split
len
parts[0].lower
decode_token
payload.get
is_token_blacklisted
```

<a id="fn-544c283f52af2b8c"></a>

## get_current_user_id

源码：[L235](D:/Project/learnLittle/app/utils/auth_utils.py:235)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

从已验证 payload 取 sub，缺失抛 401，返回可信用户 ID。业务查询用这个 ID 做所有权过滤。

**输入与签名**

```python
async def get_current_user_id(payload: dict=Depends(get_current_token_payload)) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return user_id
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
payload.get
BusinessError
```

<a id="fn-b66dc598c8e1ceb2"></a>

## create_sse_token

源码：[L245](D:/Project/learnLittle/app/utils/auth_utils.py:245)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

签发 type=sse、60 秒 JWT，并将其 jti->用户写入 Redis。只有聊天鉴权依赖消费它，不是普通用户资料凭证。

**输入与签名**

```python
async def create_sse_token(user_id: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return token
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_create_token
timedelta
decode_token
get_redis().setex
get_redis
```

<a id="fn-c06f5b4116da761c"></a>

## get_chat_user_id

源码：[L252](D:/Project/learnLittle/app/utils/auth_utils.py:252)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

允许正常 access，或对 sse JWT 用 Redis GETDEL 单次消费并比对 owner。重复使用或 Redis 条目失效即拒绝；不会因它叫 SSE 就从任意 URL 参数读 token。

**输入与签名**

```python
async def get_chat_user_id(authorization: str | None=Header(default=None)) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return payload['sub']
return owner
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Header
(authorization or '').split
len
parts[0].lower
BusinessError
decode_token
payload.get
get_current_token_payload
get_redis().getdel
get_redis
```

<a id="fn-06f2576e322d7fd5"></a>

## remaining_ttl_seconds

源码：[L269](D:/Project/learnLittle/app/utils/auth_utils.py:269)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

用 payload.exp 减当前时间得到剩余秒数，供 access 黑名单设置过期。可能为非正数，写入函数会处理。

**输入与签名**

```python
def remaining_ttl_seconds(payload: dict) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return int(payload['exp'] - time.time())
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
int
time.time
```

<a id="fn-b35c1400683087e5"></a>

## _session_key

源码：[L277](D:/Project/learnLittle/app/utils/auth_utils.py:277)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

组合用户和 device_id 为设备 Hash 的键。设备 ID 与 refresh jti 分开，设备 Hash 内保存当前 refresh jti。

**输入与签名**

```python
def _session_key(user_id: str, device_id: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'session:{user_id}:{device_id}'
```

<a id="fn-19de68f46e9dedb7"></a>

## _sessions_set_key

源码：[L281](D:/Project/learnLittle/app/utils/auth_utils.py:281)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

生成用户设备 ID 集合的键，用于列举与限制设备数。集合成员过期不会自动随独立 Hash 消失，列表函数会清残留。

**输入与签名**

```python
def _sessions_set_key(user_id: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'user_sessions:{user_id}'
```

<a id="fn-7d390c6a40f175f9"></a>

## parse_device_name

源码：[L285](D:/Project/learnLittle/app/utils/auth_utils.py:285)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

按 User-Agent 字串识别系统/浏览器并拼可读名称，未知值返回兜底。是简单启发式，不是可信设备指纹。

**输入与签名**

```python
def parse_device_name(user_agent: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 'Unknown Device'
return f'{browser} / {os_name}'
```

<a id="fn-82ae8b64abf5569f"></a>

## _client_ip

源码：[L315](D:/Project/learnLittle/app/utils/auth_utils.py:315)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

优先读 X-Forwarded-For 首项，回退 request.client.host，无请求返回空。反向代理头是否可信需由部署边界约束。

**输入与签名**

```python
def _client_ip(request: Request | None) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ''
return forwarded
return request.client.host if request.client else ''
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
request.headers.get('X-Forwarded-For', '').split(',')[0].strip
request.headers.get('X-Forwarded-For', '').split
request.headers.get
```

<a id="fn-d65b5c9460cefbbe"></a>

## store_device_session

源码：[L324](D:/Project/learnLittle/app/utils/auth_utils.py:324)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

写设备 Hash 的 jti、名称、IP、UA、时间并刷新 TTL，同时加入用户设备集合。同设备已有 created_at 会保留，不把每次登录都算新设备创建。

**输入与签名**

```python
async def store_device_session(user_id: str, device_id: str, jti: str, device_name: str | None=None, request: Request | None=None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
datetime.now(timezone.utc).isoformat
datetime.now
request.headers.get
parse_device_name
_session_key
_refresh_ttl_seconds
redis.hget
_client_ip
session_data.items
redis.hset
redis.expire
redis.sadd
_sessions_set_key
```

<a id="fn-0d24f2ed608e535f"></a>

## get_device_session

源码：[L356](D:/Project/learnLittle/app/utils/auth_utils.py:356)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

读取单设备 Hash 并输出允许的字段，缺失返回 None。它本身不校验 JWT，由路由传入可信 user_id。

**输入与签名**

```python
async def get_device_session(user_id: str, device_id: str) -> dict | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
return {'jti': data.get('jti', ''), 'device_name': data.get('device_name', ''), 'ip': data.get('ip', ''), 'user_agent': data.get('user_agent', ''), 'created_at': data.get('created_at', ''), 'last_used': data.get('last_used', '')}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().hgetall
get_redis
_session_key
data.get
```

<a id="fn-2a4c6fe8928b0034"></a>

## update_device_session

源码：[L370](D:/Project/learnLittle/app/utils/auth_utils.py:370)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

已有设备才更新新 refresh jti、last_used/IP，并刷新 Hash 和集合 TTL。不存在则不创建新的设备记录。

**输入与签名**

```python
async def update_device_session(user_id: str, device_id: str, new_jti: str, request: Request | None=None) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
_session_key
redis.exists
datetime.now(timezone.utc).isoformat
datetime.now
_refresh_ttl_seconds
redis.hset
_client_ip
redis.expire
_sessions_set_key
```

<a id="fn-671a952d52a7aee1"></a>

## delete_device_session

源码：[L392](D:/Project/learnLittle/app/utils/auth_utils.py:392)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

删除单设备 Hash 与用户集合成员。撤销 refresh 是调用者的配套动作，不能仅删设备展示就以为刷新票也撤销。

**输入与签名**

```python
async def delete_device_session(user_id: str, device_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
redis.delete
_session_key
redis.srem
_sessions_set_key
```

<a id="fn-5956d1fdeef6c162"></a>

## list_user_sessions

源码：[L398](D:/Project/learnLittle/app/utils/auth_utils.py:398)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

遍历用户设备集合，删掉 Hash 已过期的成员，标出 current_device_id，按最近使用倒序返回。输出不暴露 refresh jti。

**输入与签名**

```python
async def list_user_sessions(user_id: str, current_device_id: str | None=None) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return sessions
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
redis.smembers
_sessions_set_key
redis.hgetall
_session_key
redis.srem
sessions.append
data.get
bool
sessions.sort
```

<a id="fn-d0c38c1db2b512da"></a>

## list_user_sessions.<lambda@420:22>

源码：[L420](D:/Project/learnLittle/app/utils/auth_utils.py:420)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

设备展示按 last_used 字符串倒序排序，缺字段空串靠后。不同于上限淘汰使用的创建时间。

**输入与签名**

```python
lambda item: item.get("last_used", "")
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 item.get('last_used', '')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
item.get
```

<a id="fn-f041151bc2564d9a"></a>

## enforce_session_limit

源码：[L424](D:/Project/learnLittle/app/utils/auth_utils.py:424)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

超限时按 created_at 升序找到最旧设备，撤销其 refresh 并删 Hash/集合成员。不是按 last_used 做 LRU。

**输入与签名**

```python
async def enforce_session_limit(user_id: str, max_sessions: int=5) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
redis.smembers
_sessions_set_key
len
redis.hget
_session_key
timed.append
timed.sort
redis.delete
_refresh_key
redis.srem
```

<a id="fn-690bdfeb8009fcd4"></a>

## enforce_session_limit.<lambda@435:19>

源码：[L435](D:/Project/learnLittle/app/utils/auth_utils.py:435)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

设备上限淘汰取二元组中的 created_at，升序找最早设备。返回排序 key，不直接撤销凭证。

**输入与签名**

```python
lambda item: item[1]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 item[1]
```

<a id="fn-694b4df95272c775"></a>

## _clear_all_device_sessions

源码：[L445](D:/Project/learnLittle/app/utils/auth_utils.py:445)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

删当前用户所有设备 Hash，最后删设备集合。由全量 refresh 撤销联动调用，不涉及 SQL 用户记录。

**输入与签名**

```python
async def _clear_all_device_sessions(user_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
redis.smembers
_sessions_set_key
redis.delete
_session_key
```
