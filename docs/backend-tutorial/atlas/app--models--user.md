# app/models/user.py

[源码](D:/Project/learnLittle/app/models/user.py) | [任务流程 02](D:/Project/learnLittle/docs/backend-tutorial/02-account.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

users 表的凭据、资料与状态；uuid 是其他业务表的归属外键。

## 本文件导航

- [generate_uuid](#fn-4ffffe18ae0b532e)
- [User.__repr__](#fn-132d874089c0f078)

## 类与字段

### User

账户事实。password 为哈希，status 是字段；存在这个字段不等于每条鉴权路径都重新查询状态。

声明位置：[L21](D:/Project/learnLittle/app/models/user.py:21)。父类：`Base`。

```python
__tablename__ = 'users'

uuid: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)

username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

password: Mapped[str] = mapped_column(String(255), nullable=False)

avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)

bio: Mapped[str | None] = mapped_column(Text, nullable=True)

status: Mapped[str] = mapped_column(String(20), server_default='active', nullable=False)

created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```

<a id="fn-4ffffe18ae0b532e"></a>

## generate_uuid

源码：[L17](D:/Project/learnLittle/app/models/user.py:17)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

返回 uuid4 字符串供 User 主键默认值使用。每次实际插入需要新 ID，不在模块导入时生成一个共享值。

**输入与签名**

```python
def generate_uuid() -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return str(uuid.uuid4())
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
str
uuid.uuid4
```

<a id="fn-132d874089c0f078"></a>

## User.__repr__

源码：[L45](D:/Project/learnLittle/app/models/user.py:45)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

User 的调试字符串表示，返回 `f'<User(id={self.uuid}, username={self.username})>'`。用于日志/交互查看，不是 API Schema 序列化，也不查询或提交数据库。

**输入与签名**

```python
def __repr__(self) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'<User(id={self.uuid}, username={self.username})>'
```
