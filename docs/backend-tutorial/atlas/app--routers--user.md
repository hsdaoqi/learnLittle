# app/routers/user.py

[源码](D:/Project/learnLittle/app/routers/user.py) | [任务流程 02](D:/Project/learnLittle/docs/backend-tutorial/02-account.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

账号认证与资料 HTTP 适配，默认注册要求邮箱验证。

## 本文件导航

- [register](#fn-055e10095f6c6377)
- [sse_token](#fn-754fd0917a4882d4)
- [send_code](#fn-f92630632b419276)
- [change_email](#fn-c3a7d518aa93af3d)
- [login](#fn-0995dd769c8acc91)
- [refresh](#fn-dcc0c3ea776b3bb2)
- [logout](#fn-1b426c9bfccaff81)
- [get_me](#fn-2c89475cedc720a2)
- [update_me](#fn-1ec4503f57802edd)
- [change_password](#fn-aa59e0f3412eb8b0)
- [upload_avatar](#fn-92065cee4250a61c)
- [get_sessions](#fn-be6403fddecb6466)
- [revoke_session](#fn-5d7879c7c61b02af)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

router = APIRouter()
```

<a id="fn-055e10095f6c6377"></a>

## register

源码：[L87](D:/Project/learnLittle/app/routers/user.py:87)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

接 UserRegister，查用户名、默认要求验证邮箱、消费 code、查邮箱、校验密码、写 User 并播种分类。SQL 由依赖提交；已消费验证码不随 SQL 失败恢复。

**输入与签名**

```python
async def register(data: UserRegister, request: Request, db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/auth/register', summary='用户注册')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'user_id': user.uuid, 'username': user.username})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
db.execute
select(User).where
select
result.scalar_one_or_none
BusinessError
email_service.verify_code
validate_password_strength
User
str
uuid.uuid4
hash_password
db.add
db.flush
seed_template_tree
success_response
router.post
```

<a id="fn-754fd0917a4882d4"></a>

## sse_token

源码：[L137](D:/Project/learnLittle/app/routers/user.py:137)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

依赖正常用户鉴权，调用 create_sse_token，返回 token 和 60 秒寿命。不是匿名签票接口。

**输入与签名**

```python
async def sse_token(user_id: str=Depends(get_current_user_id))
```

装饰器/挂载：

```python
@router.post('/auth/sse-token', summary='获取一次性 SSE 短期 Token')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'token': token, 'expires_in': 60})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
create_sse_token
success_response
router.post
```

<a id="fn-f92630632b419276"></a>

## send_code

源码：[L145](D:/Project/learnLittle/app/routers/user.py:145)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

提取 IP，检查邮件专属额度，发送验证码，成功再标冷却；普通发送异常转 502。转发头可信性由部署保证。

**输入与签名**

```python
async def send_code(data: SendCodeRequest, request: Request)
```

装饰器/挂载：

```python
@router.post('/auth/send-code', summary='发送邮箱验证码')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='验证码已发送')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
request.headers.get('X-Forwarded-For', '').split(',')[0].strip
request.headers.get('X-Forwarded-For', '').split
request.headers.get
request.headers.get('X-Real-IP', '').strip
email_service.enforce_send_code_limits
email_service.send_verification_code
BusinessError
email_service.mark_send_code_cooldown
success_response
router.post
```

<a id="fn-c3a7d518aa93af3d"></a>

## change_email

源码：[L163](D:/Project/learnLittle/app/routers/user.py:163)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

先消费验证码，检查目标邮箱占用，再修改当前用户 email/email_verified 并 flush。失败不会自动恢复 Redis 验证码。

**输入与签名**

```python
async def change_email(data: EmailChangeRequest, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/user/change-email', summary='修改/绑定邮箱')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='邮箱修改成功')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
email_service.verify_code
BusinessError
(await db.execute(select(User).where(User.email == data.email))).scalar_one_or_none
db.execute
select(User).where
select
(await db.execute(select(User).where(User.uuid == user_id))).scalar_one_or_none
db.flush
success_response
router.post
```

<a id="fn-0995dd769c8acc91"></a>

## login

源码：[L187](D:/Project/learnLittle/app/routers/user.py:187)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

先锁定检查再查密码，失败增加计数，成功清计数并签 access/refresh、登记白名单。有 device_id 才维护设备并按上限淘汰，不能说每次登录一定生成设备项。

**输入与签名**

```python
async def login(data: UserLogin, request: Request, db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/auth/login', summary='用户登录')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=TokenResponse(access_token=create_access_token(user.uuid), refresh_token=refresh_token, token_type='bearer', expires_in=settings.access_token_expire_minutes * 60, device_id=data.device_id).model_dump())
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
check_login_attempts
db.execute
select(User).where
select
result.scalar_one_or_none
verify_password
record_login_failure
BusinessError
clear_login_attempts
get_device_session
existing.get
revoke_refresh_token
create_refresh_token
store_refresh_token
get_settings
store_device_session
enforce_session_limit
success_response
TokenResponse(access_token=create_access_token(user.uuid), refresh_token=refresh_token, token_type='bearer', expires_in=settings.access_token_expire_minutes * 60, device_id=data.device_id).model_dump
TokenResponse
create_access_token
router.post
```

<a id="fn-dcc0c3ea776b3bb2"></a>

## refresh

源码：[L233](D:/Project/learnLittle/app/routers/user.py:233)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

校验 refresh 签名/类型/白名单，撤销旧票后签新票，有 device_id 则更新设备状态。多次 Redis 命令不是一个原子刷新脚本。

**输入与签名**

```python
async def refresh(data: RefreshTokenRequest, request: Request)
```

装饰器/挂载：

```python
@router.post('/auth/refresh', summary='刷新 Access Token')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=TokenResponse(access_token=create_access_token(user_id), refresh_token=new_refresh_token, token_type='bearer', expires_in=settings.access_token_expire_minutes * 60, device_id=data.device_id).model_dump())
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
decode_token
payload.get
BusinessError
verify_refresh_token
revoke_refresh_token
create_refresh_token
store_refresh_token
update_device_session
get_settings
success_response
TokenResponse(access_token=create_access_token(user_id), refresh_token=new_refresh_token, token_type='bearer', expires_in=settings.access_token_expire_minutes * 60, device_id=data.device_id).model_dump
TokenResponse
create_access_token
router.post
```

<a id="fn-1b426c9bfccaff81"></a>

## logout

源码：[L272](D:/Project/learnLittle/app/routers/user.py:272)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

拉黑当前 access，按可选 refresh/device 撤销当前用户刷新能力并删设备。不是删除 SQL 用户或全量所有 access。

**输入与签名**

```python
async def logout(data: LogoutRequest, payload: dict=Depends(get_current_token_payload))
```

装饰器/挂载：

```python
@router.post('/auth/logout', summary='用户登出')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'refresh_tokens_revoked': revoked})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
payload.get
blacklist_access_token
remaining_ttl_seconds
decode_token
refresh_payload.get
verify_refresh_token
revoke_refresh_token
get_device_session
session.get
delete_device_session
success_response
router.post
```

<a id="fn-2c89475cedc720a2"></a>

## get_me

源码：[L307](D:/Project/learnLittle/app/routers/user.py:307)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

从可信 user_id 查询 User，找不到 404，返回 UserInfo 公开字段。不会把密码哈希直接 dump 给客户端。

**输入与签名**

```python
async def get_me(user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/user/me', summary='获取当前用户信息')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=UserInfo.model_validate(user).model_dump(mode='json'))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
db.execute
select(User).where
select
result.scalar_one_or_none
BusinessError
success_response
UserInfo.model_validate(user).model_dump
UserInfo.model_validate
router.get
```

<a id="fn-1ec4503f57802edd"></a>

## update_me

源码：[L321](D:/Project/learnLittle/app/routers/user.py:321)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

按当前用户定位，只在 bio 非 None 时更新并 flush。此入口不是任意修改账号所有字段的通用 patch。

**输入与签名**

```python
async def update_me(data: UserUpdate, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.put('/user/me', summary='更新个人资料')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='更新成功')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
(await db.execute(select(User).where(User.uuid == user_id))).scalar_one_or_none
db.execute
select(User).where
select
BusinessError
db.flush
success_response
router.put
```

<a id="fn-aa59e0f3412eb8b0"></a>

## change_password

源码：[L338](D:/Project/learnLittle/app/routers/user.py:338)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

校验原密码和新强度，替换哈希并撤销所有 refresh/设备。SQL commit 在依赖，Redis 撤销已经发生，跨存储不原子。

**输入与签名**

```python
async def change_password(data: PasswordChange, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/user/me/password', summary='修改密码')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='密码修改成功')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
(await db.execute(select(User).where(User.uuid == user_id))).scalar_one_or_none
db.execute
select(User).where
select
BusinessError
verify_password
validate_password_strength
hash_password
db.flush
revoke_all_refresh_tokens
success_response
router.post
```

<a id="fn-92065cee4250a61c"></a>

## upload_avatar

源码：[L362](D:/Project/learnLittle/app/routers/user.py:362)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

受限读取、校验格式后写用户目录新文件，尝试删旧头像，更新 URL 并返回。磁盘动作不受 SQL rollback 控制，也不是完整图片重编码。

**输入与签名**

```python
async def upload_avatar(request: Request, file: UploadFile=File(...), user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/file/avatar', summary='上传头像')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'avatar_url': avatar_url, 'filename': stored_name})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
File
Depends
read_upload_limited
validate_avatar_file
len
Path
ensure_dir
str
int
datetime.now().timestamp
datetime.now
file_path.write_bytes
(await db.execute(select(User).where(User.uuid == user_id))).scalar_one_or_none
db.execute
select(User).where
select
old_path.exists
old_path.is_file
old_path.unlink
logger.warning
db.flush
success_response
router.post
```

<a id="fn-be6403fddecb6466"></a>

## get_sessions

源码：[L403](D:/Project/learnLittle/app/routers/user.py:403)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

从 X-Device-Id 得当前设备标识，查询 Redis 设备列表返回。标识只用于展示 is_current，身份仍来自 Token。

**输入与签名**

```python
async def get_sessions(request: Request, user_id: str=Depends(get_current_user_id))
```

装饰器/挂载：

```python
@router.get('/auth/sessions', summary='查看活跃设备')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'sessions': sessions})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
request.headers.get
list_user_sessions
success_response
router.get
```

<a id="fn-5d7879c7c61b02af"></a>

## revoke_session

源码：[L413](D:/Project/learnLittle/app/routers/user.py:413)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

定位用户设备，撤销其 refresh 和设备记录；若请求头标为当前设备再黑名单当前 access。其他已发 access 不自动全部撤销。

**输入与签名**

```python
async def revoke_session(device_id: str, request: Request, user_id: str=Depends(get_current_user_id), payload: dict=Depends(get_current_token_payload))
```

装饰器/挂载：

```python
@router.delete('/auth/sessions/{device_id}', summary='撤销设备会话')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='当前会话已注销')
return success_response(message='会话已撤销')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
get_device_session
BusinessError
session.get
revoke_refresh_token
delete_device_session
request.headers.get
blacklist_access_token
payload.get
remaining_ttl_seconds
success_response
router.delete
```
