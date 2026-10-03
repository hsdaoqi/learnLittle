# 02 完成注册、登录和设备撤销

阅读主线：[user.py](D:/Project/learnLittle/app/routers/user.py) -> [auth_utils.py](D:/Project/learnLittle/app/utils/auth_utils.py) / [email_service.py](D:/Project/learnLittle/app/services/email_service.py)。Schema 在 [auth.py](D:/Project/learnLittle/app/schemas/auth.py)。

## 任务 A：注册一个用户

1. 请求验证码经过邮箱格式校验与发送频率检查。`enforce_send_code_limits` 检查邮箱冷却及 IP 小时计数，`send_verification_code` 生成六位数字，先写 Redis，再渲染模板、通过 `send_email` 发送；成功后路由记录冷却。发送失败不自动撤回已写验证码。
2. `register` 先检查用户名重复，按默认配置要求邮箱和 code，再 `verify_code` 校验并消费验证码，继续检查邮箱重复、密码强度。
3. `hash_password` 生成带盐 bcrypt 哈希。SQL 存哈希，不存原始密码。
4. 加入 User，flush 后取得身份，再 `seed_template_tree` 递归播种默认分类。
5. 注册路由正常结束后，用户与默认分类一起由请求事务提交。

验证码有效期 300 秒，错误累计五次后删除，错误计数有效期 900 秒；邮箱冷却 60 秒，每 IP 每小时最多十次的检查与普通中间件限流是不同层。生成器当前使用 `random.randint`，不是密码学随机数生成器。

**重要顺序**：验证码消费发生在所有后续校验完成之前。后续注册失败不意味着验证码会随 SQL rollback 自动恢复，因为它在 Redis。

`UserRegister.email` 可空是兼容字段设计，不能推断默认注册允许不填邮箱；路由默认 `registration_require_email=True`。

## 任务 B：登录并继续使用

```text
login
  -> check_login_attempts
  -> 查询用户 -> verify_password
  -> 失败：record_login_failure -> 业务错误
  -> 成功：clear_login_attempts
  -> create_access_token / create_refresh_token
  -> store_refresh_token（白名单）
  -> store_device_session / enforce_session_limit
```

Access Token 是短期访问凭证；Refresh Token 是换发凭证。JWT payload 带 `sub`、`iat`、`exp`、`jti`、`type`。`jti` 是每枚 Token 的编号，不是用户 ID。

登录连续失败五次会在锁定窗口内拒绝继续登录，正确密码也不能绕过这个前置检查。不要把它和 HTTP 429 频率限制混为一谈。

访问资料时，`get_current_token_payload` 按 Bearer 格式、JWT 签名/过期、access 类型、黑名单顺序验证，`get_current_user_id` 提取 `sub`。JWT 解码不是简单 Base64 读取。

`refresh` 校验 refresh 类型与白名单，撤销旧 refresh，签发新 access/refresh，更新设备的 jti 和最后使用时间。它不是用同一枚 refresh 无限换 access。

## 任务 C：注销、改密、撤销设备

- `logout` 将当前 access 的 jti 放入黑名单，TTL 是剩余有效期，同时撤销相应 refresh/设备状态。
- `change_password` 校验原密码和新密码，更新哈希，撤销刷新能力；不能把这描述成所有历史 access 立即统一失效。
- `get_sessions` 从 Redis 用户设备集合读取各 Hash，清掉已经过期的成员，以 last_used 排序。
- `revoke_session` 删除指定设备状态并撤销其 refresh；当前设备可额外处理当前 access。
- `enforce_session_limit` 按 created_at 淘汰最旧设备，不是按 last_used 淘汰。

设备数上限不等于用户数上限。登录传入 `device_id` 才会维护设备记录。`device_id` 也不是 access jti。Redis Hash 保存设备名称、IP、User-Agent、创建与最近使用时间等。当前 `_client_ip` 会读取转发头，部署时不能把任意客户端伪造的代理头当作可信来源。

## 任务 D：改资料、头像与邮箱

`get_me/update_me` 查询并更新当前 SQL 用户。`upload_avatar` 先用受限读取避免无限吃内存，再检查大小、扩展名和 magic bytes，使用服务端生成的文件名落盘，更新 avatar 字段，静态路径由 main 挂载。

magic bytes 检查是格式初筛，不是完整图像解码、恶意内容扫描或图片重编码。旧文件清理和 SQL 更新也不是跨介质事务。

`change_email` 复用邮箱验证，检查占用后更新 email 和验证状态。验证码模板通过占位符替换生成，不是完整 Jinja 模板引擎。

## 任务 E：换一张只用于聊天的票

`sse_token` 让已登录用户换取 60 秒、type=sse 的 Token，同时把 jti 写入 Redis。`get_chat_user_id` 用 `GETDEL` 原子消费这张一次性票；正常 access 仍能通过聊天鉴权。

这张票不是普通资料接口的通行证。它通过 `Authorization: Bearer ...` 使用，不代表所有 URL 查询参数都可传 Token。失败后重复用同一张票也会失败，应区分凭证一次性与消息幂等。

**练习**：一个设备被踢掉后，为什么它原有的 access 仍可能短时间有效？因为 refresh 白名单与 access 黑名单是两套检查，撤销前者不会自动枚举后者。
