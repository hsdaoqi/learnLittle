# app/services/email_service.py

[源码](D:/Project/learnLittle/app/services/email_service.py) | [任务流程 04](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

SMTP MIME 发送、验证码 Redis 状态与附件构造；发信不是 SQL 事务。

## 本文件导航

- [set_send_email_fn](#fn-99f2ebf4414b57d5)
- [get_send_email_fn](#fn-83772b51f1d3272f)
- [smtp_available](#fn-c8333eb71fa0a927)
- [generate_code](#fn-6917dd579958c2d1)
- [_build_message](#fn-44a5e4e953af25e7)
- [send_email](#fn-2dd17be9bf5372e9)
- [_render_verification_html](#fn-a4d5988506f53b1e)
- [send_verification_code](#fn-45ce5d8fd28c0d12)
- [verify_code](#fn-2561815d17feb58d)
- [enforce_send_code_limits](#fn-01c82dba52154590)
- [mark_send_code_cooldown](#fn-e2b42599721569a9)
- [note_attachment](#fn-77b39f1875277f8c)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

CODE_TTL = 300

MAX_CODE_ATTEMPTS = 5

ERROR_COUNT_TTL = 900

COOLDOWN_SECONDS = 60

IP_HOURLY_LIMIT = 10

SendFn = Callable[..., Awaitable[None]]

_injected: SendFn | None = None

TEMPLATE_PATH = Path(__file__).resolve().parent.parent.parent / 'templates' / 'email' / 'verification_code.html'
```

<a id="fn-99f2ebf4414b57d5"></a>

## set_send_email_fn

源码：[L44](D:/Project/learnLittle/app/services/email_service.py:44)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

替换SMTP 发送的模块级注入槽 `_injected`，赋值为传入函数；None 表示撤销注入。setter 本身不执行被注入函数，实际调用者再优先选它；测试结束需清理，避免跨用例残留。

**输入与签名**

```python
def set_send_email_fn(fn: SendFn | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

<a id="fn-83772b51f1d3272f"></a>

## get_send_email_fn

源码：[L49](D:/Project/learnLittle/app/services/email_service.py:49)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

返回SMTP 发送当前的注入函数 `_injected` 或 None，不调用它。调用方用它判断模型/替身是否可用；返回 None 不必然表示功能关闭，还可能继续选真实 API 或本地兜底。

**输入与签名**

```python
def get_send_email_fn() -> SendFn | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _injected
```

<a id="fn-c8333eb71fa0a927"></a>

## smtp_available

源码：[L53](D:/Project/learnLittle/app/services/email_service.py:53)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

有注入发信函数即 True，否则检查 SMTP host/username/password。配置齐不表示连接成功，也不保证真实依赖安装齐。

**输入与签名**

```python
def smtp_available(settings: Settings | None=None) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return True
return bool(settings.smtp_host and settings.smtp_username and settings.smtp_password)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
bool
```

<a id="fn-6917dd579958c2d1"></a>

## generate_code

源码：[L62](D:/Project/learnLittle/app/services/email_service.py:62)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

产生六位数字验证码。实现使用 random.randint，教程不把它称为密码学安全随机数。

**输入与签名**

```python
def generate_code() -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'{random.randint(0, 999999):06d}'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
random.randint
```

<a id="fn-44a5e4e953af25e7"></a>

## _build_message

源码：[L66](D:/Project/learnLittle/app/services/email_service.py:66)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

用 MIMEMultipart 构造文本/可选 HTML/附件层级，设置发件人与收件人等头。返回 MIME 对象，实际网络发送在 send_email。

**输入与签名**

```python
def _build_message(*, settings: Settings, to: str, subject: str, body: str, html: str | None=None, attachments: list[dict] | None=None) -> MIMEMultipart
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return msg
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
bool
MIMEMultipart
alt.attach
MIMEText
msg.attach
formataddr
str
Header
att.get
mime.partition
isinstance
data.decode
MIMEApplication
part.add_header
```

<a id="fn-2dd17be9bf5372e9"></a>

## send_email

源码：[L111](D:/Project/learnLittle/app/services/email_service.py:111)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

优先使用测试注入，否则根据设置通过 aiosmtplib 发 SMTP 邮件；连接类错误按代码重试，认证失败不重试。邮件一旦发送不能靠 SQL rollback 撤回。

**输入与签名**

```python
async def send_email(to: str, subject: str, body: str, *, html: str | None=None, attachments: list[dict] | None=None, settings: Settings | None=None, retries: int=2, backoff: float=2.0) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
_injected
smtp_available
BusinessError
_build_message
range
aiosmtplib.SMTP
smtp.login
smtp.send_message
logger.info
logger.error
logger.warning
asyncio.sleep
```

<a id="fn-a4d5988506f53b1e"></a>

## _render_verification_html

源码：[L175](D:/Project/learnLittle/app/services/email_service.py:175)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

读取验证码邮件模板并替换指定占位符，提供邮件 HTML。不是执行完整模板语言；找不到模板时按代码兜底。

**输入与签名**

```python
def _render_verification_html(code: str, settings: Settings) -> str | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
return template.replace('{{app_name}}', settings.smtp_from_name or settings.app_name).replace('{{code}}', code).replace('{{expire_minutes}}', str(CODE_TTL // 60))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
TEMPLATE_PATH.read_text
template.replace('{{app_name}}', settings.smtp_from_name or settings.app_name).replace('{{code}}', code).replace
template.replace('{{app_name}}', settings.smtp_from_name or settings.app_name).replace
template.replace
str
```

<a id="fn-45ce5d8fd28c0d12"></a>

## send_verification_code

源码：[L187](D:/Project/learnLittle/app/services/email_service.py:187)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

先检查 SMTP 可用，生成 code 并写 Redis 300 秒 TTL，再渲染和发送邮件，返回 code。发送失败时这个已写验证码不会在本函数自动撤回。

**输入与签名**

```python
async def send_verification_code(to: str, settings: Settings | None=None) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return code
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
smtp_available
BusinessError
generate_code
get_redis
redis.set
_render_verification_html
send_email
```

<a id="fn-2561815d17feb58d"></a>

## verify_code

源码：[L205](D:/Project/learnLittle/app/services/email_service.py:205)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

比较 Redis 验证码，正确即消费并清错误计数；错误累计并在阈值后删 code。返回 bool，不替用户完成注册或改邮箱。

**输入与签名**

```python
async def verify_code(email: str, code: str) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return False
return True
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
redis.get
redis.incr
redis.expire
redis.delete
logger.warning
```

<a id="fn-01c82dba52154590"></a>

## enforce_send_code_limits

源码：[L223](D:/Project/learnLittle/app/services/email_service.py:223)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

检查邮箱发送冷却和 IP 小时额度，超限抛 BusinessError。是发送验证码专属约束，不等于普通路由限流。

**输入与签名**

```python
async def enforce_send_code_limits(email: str, client_ip: str | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
redis.exists
redis.ttl
BusinessError
max
datetime.now().strftime
datetime.now
redis.incr
redis.expire
```

<a id="fn-e2b42599721569a9"></a>

## mark_send_code_cooldown

源码：[L250](D:/Project/learnLittle/app/services/email_service.py:250)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

发送成功后给邮箱设置短期冷却标记。分离这个动作使失败发送不会被当作成功冷却。

**输入与签名**

```python
async def mark_send_code_cooldown(email: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().set
get_redis
```

<a id="fn-77b39f1875277f8c"></a>

## note_attachment

源码：[L254](D:/Project/learnLittle/app/services/email_service.py:254)；任务：[第 04 章](D:/Project/learnLittle/docs/backend-tutorial/04-learning.md)。

按请求 format 把笔记标题正文编码为邮件附件，返回文件名/内容/类型数据。只组附件，不发信、不改笔记。

**输入与签名**

```python
def note_attachment(title: str, content: str, fmt: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'filename': f'{safe}.txt', 'data': content.encode('utf-8'), 'mime': 'text/plain'}
return {'filename': f'{safe}.md', 'data': content.encode('utf-8'), 'mime': 'text/markdown'}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
''.join((ch if ch.isalnum() or ch in '._- ' else '_' for ch in title)).strip
''.join
ch.isalnum
content.encode
```
