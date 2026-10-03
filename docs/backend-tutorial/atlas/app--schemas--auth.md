# app/schemas/auth.py

[源码](D:/Project/learnLittle/app/schemas/auth.py) | [任务流程 02](D:/Project/learnLittle/docs/backend-tutorial/02-account.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

注册/登录/刷新/资料/邮件请求和公开响应的数据契约。

## 本文件导航

- [UserRegister.validate_username](#fn-fb95b8b60af9f02b)
- [UserRegister.validate_email](#fn-4c1823fb0101661b)
- [SendCodeRequest.validate_email](#fn-7f7a334d081c4a48)
- [EmailChangeRequest.validate_email](#fn-b5590cf74c42fb03)
- [NoteExportEmailRequest.validate_to](#fn-e0023914d6844d37)
- [PasswordChange.validate_password](#fn-afd774fb093ae732)

## 类与字段

### UserRegister

Pydantic 数据契约，声明 username、password、email、verification_code。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L15](D:/Project/learnLittle/app/schemas/auth.py:15)。父类：`BaseModel`。

```python
username: str = Field(min_length=3, max_length=50, description='用户名')

password: str = Field(min_length=8, max_length=128, description='密码')

email: str | None = Field(default=None, max_length=255, description='注册邮箱（默认必须与验证码一起提供）')

verification_code: str | None = Field(default=None, min_length=6, max_length=6)
```

### SendCodeRequest

Pydantic 数据契约，声明 email。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L40](D:/Project/learnLittle/app/schemas/auth.py:40)。父类：`BaseModel`。

```python
email: str = Field(description='邮箱地址')
```

### EmailChangeRequest

Pydantic 数据契约，声明 email、verification_code。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L51](D:/Project/learnLittle/app/schemas/auth.py:51)。父类：`BaseModel`。

```python
email: str

verification_code: str = Field(min_length=6, max_length=6)
```

### NoteExportEmailRequest

Pydantic 数据契约，声明 to、format。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L63](D:/Project/learnLittle/app/schemas/auth.py:63)。父类：`BaseModel`。

```python
to: str | None = Field(default=None, description='收件人；空则用当前用户邮箱')

format: str = Field(default='md', pattern='^(md|txt)$')
```

### UserLogin

Pydantic 数据契约，声明 username、password、device_id、device_name。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L75](D:/Project/learnLittle/app/schemas/auth.py:75)。父类：`BaseModel`。

```python
username: str = Field(description='用户名')

password: str = Field(description='密码')

device_id: str | None = Field(default=None, max_length=64, description='设备唯一标识')

device_name: str | None = Field(default=None, max_length=100, description='设备可读名称')
```

### TokenResponse

Pydantic 数据契约，声明 access_token、refresh_token、token_type、expires_in、device_id。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L88](D:/Project/learnLittle/app/schemas/auth.py:88)。父类：`BaseModel`。

```python
access_token: str = Field(description='Access Token（JWT）')

refresh_token: str = Field(description='Refresh Token（JWT）')

token_type: str = Field(default='bearer', description='Token 类型')

expires_in: int = Field(description='Access Token 有效期（秒）')

device_id: str | None = Field(default=None, description='回传设备标识')
```

### RefreshTokenRequest

Pydantic 数据契约，声明 refresh_token、device_id。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L98](D:/Project/learnLittle/app/schemas/auth.py:98)。父类：`BaseModel`。

```python
refresh_token: str = Field(description='Refresh Token')

device_id: str | None = Field(default=None, max_length=64)
```

### LogoutRequest

Pydantic 数据契约，声明 refresh_token、device_id。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L105](D:/Project/learnLittle/app/schemas/auth.py:105)。父类：`BaseModel`。

```python
refresh_token: str | None = Field(default=None, description='当前设备的 Refresh Token')

device_id: str | None = Field(default=None, max_length=64)
```

### UserUpdate

Pydantic 数据契约，声明 bio。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L114](D:/Project/learnLittle/app/schemas/auth.py:114)。父类：`BaseModel`。

```python
model_config = {'extra': 'forbid'}

bio: str | None = Field(default=None, max_length=500)
```

### PasswordChange

Pydantic 数据契约，声明 old_password、new_password。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L121](D:/Project/learnLittle/app/schemas/auth.py:121)。父类：`BaseModel`。

```python
old_password: str

new_password: str = Field(min_length=8, max_length=128)
```

### SessionInfo

Pydantic 数据契约，声明 device_id、device_name、ip、created_at、last_used、is_current。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L135](D:/Project/learnLittle/app/schemas/auth.py:135)。父类：`BaseModel`。

```python
device_id: str

device_name: str | None = None

ip: str | None = None

created_at: str | None = None

last_used: str | None = None

is_current: bool = False
```

### UserInfo

Pydantic 数据契约，声明 uuid、username、email、email_verified、avatar、bio、status、created_at。下面 Field/类型声明给出必填、默认和范围；from_attributes 表示可从 ORM 读属性。未声明的业务所有权/数据库关系仍由 service 校验。

声明位置：[L144](D:/Project/learnLittle/app/schemas/auth.py:144)。父类：`BaseModel`。

```python
uuid: str

username: str

email: str | None = None

email_verified: bool = False

avatar: str | None = None

bio: str | None = None

status: str

created_at: datetime

model_config = {'from_attributes': True}
```


## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
_EMAIL_RE = re.compile('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
```

<a id="fn-fb95b8b60af9f02b"></a>

## UserRegister.validate_username

源码：[L27](D:/Project/learnLittle/app/schemas/auth.py:27)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

校验用户名允许字符/格式并返回规范输入或抛 ValueError。用户名是否已经占用仍需路由 SQL 查询。

**输入与签名**

```python
def validate_username(cls, v: str) -> str
```

装饰器/挂载：

```python
@field_validator('username')
@classmethod
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return v
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
v.replace('_', '').isalnum
v.replace
ValueError
field_validator
```

<a id="fn-4c1823fb0101661b"></a>

## UserRegister.validate_email

源码：[L34](D:/Project/learnLittle/app/schemas/auth.py:34)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

允许兼容的可空邮箱，并对非空值校验邮箱格式。默认注册是否必须邮箱由路由配置决定。

**输入与签名**

```python
def validate_email(cls, v: str | None) -> str | None
```

装饰器/挂载：

```python
@field_validator('email')
@classmethod
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return v
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_EMAIL_RE.match
ValueError
field_validator
```

<a id="fn-7f7a334d081c4a48"></a>

## SendCodeRequest.validate_email

源码：[L45](D:/Project/learnLittle/app/schemas/auth.py:45)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

校验发送验证码目标地址格式。只验证字符串，不证明目标邮箱真实存在或归属请求者。

**输入与签名**

```python
def validate_email(cls, v: str) -> str
```

装饰器/挂载：

```python
@field_validator('email')
@classmethod
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return v
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_EMAIL_RE.match
ValueError
field_validator
```

<a id="fn-b5590cf74c42fb03"></a>

## EmailChangeRequest.validate_email

源码：[L57](D:/Project/learnLittle/app/schemas/auth.py:57)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

验证改绑目标邮箱格式，后续仍需验证码和占用检查。Schema 本身不访问 Redis。

**输入与签名**

```python
def validate_email(cls, v: str) -> str
```

装饰器/挂载：

```python
@field_validator('email')
@classmethod
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return v
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_EMAIL_RE.match
ValueError
field_validator
```

<a id="fn-e0023914d6844d37"></a>

## NoteExportEmailRequest.validate_to

源码：[L69](D:/Project/learnLittle/app/schemas/auth.py:69)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

对可选导出目标邮箱做格式检查，未给时路由回退用户邮箱。验证不发信。

**输入与签名**

```python
def validate_to(cls, v: str | None) -> str | None
```

装饰器/挂载：

```python
@field_validator('to')
@classmethod
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return v
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_EMAIL_RE.match
ValueError
field_validator
```

<a id="fn-afd774fb093ae732"></a>

## PasswordChange.validate_password

源码：[L127](D:/Project/learnLittle/app/schemas/auth.py:127)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

对新密码字段应用项目强度规则，失败变参数校验错误。原密码是否正确还要查询用户后 bcrypt 验证。

**输入与签名**

```python
def validate_password(cls, v: str) -> str
```

装饰器/挂载：

```python
@field_validator('new_password')
@classmethod
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return v
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
any
c.isalpha
ValueError
c.isdigit
field_validator
```
