# app/db/database.py

[源码](D:/Project/learnLittle/app/db/database.py) | [任务流程 01](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

SQL URL、engine、session 与普通请求事务所有权。

## 本文件导航

- [build_database_url](#fn-5efc76efe7c75957)
- [create_database_engine](#fn-9b23d25c48c943e8)
- [create_session_factory](#fn-dc41b5faa8a9412a)
- [get_db_session](#fn-f4c24f21f88f0c6a)
- [check_database](#fn-7bdc5f2aa2e632bc)
<a id="fn-5efc76efe7c75957"></a>

## build_database_url

源码：[L18](D:/Project/learnLittle/app/db/database.py:18)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

用 SQLAlchemy URL.create 把配置拼成 mysql+aiomysql URL，正确表达密码特殊字符。返回结构化 URL，不连接数据库，也不要把含密码的渲染结果写入公开日志。

**输入与签名**

```python
def build_database_url(settings: Settings) -> URL
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return URL.create(drivername='mysql+aiomysql', username=settings.mysql_user, password=settings.mysql_password, host=settings.mysql_host, port=settings.mysql_port, database=settings.mysql_database, query={'charset': 'utf8mb4'})
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
URL.create
```

<a id="fn-9b23d25c48c943e8"></a>

## create_database_engine

源码：[L31](D:/Project/learnLittle/app/db/database.py:31)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

从 settings 创建异步 engine，开启连接检查与 1800 秒回收。engine 是连接资源管理器，不等于一次业务事务；最终由生命周期 dispose。

**输入与签名**

```python
def create_database_engine(settings: Settings) -> AsyncEngine
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return create_async_engine(build_database_url(settings), pool_pre_ping=True, pool_recycle=1800)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
create_async_engine
build_database_url
```

<a id="fn-dc41b5faa8a9412a"></a>

## create_session_factory

源码：[L39](D:/Project/learnLittle/app/db/database.py:39)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

创建绑定 engine 的 async_sessionmaker，expire_on_commit=False 使已加载属性提交后仍可读。返回会话工厂，不是共享一个会话给所有请求。

**输入与签名**

```python
def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
async_sessionmaker
```

<a id="fn-f4c24f21f88f0c6a"></a>

## get_db_session

源码：[L47](D:/Project/learnLittle/app/db/database.py:47)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

FastAPI 依赖用 yield 暂借独立 AsyncSession，路由正常结束后 commit，异常 rollback 后继续抛出。普通 service 的 flush 不提交，靠这一层完成事务；流生成器和工具另开自己的会话。

**输入与签名**

```python
async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield session
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
session_factory
session.commit
session.rollback
```

<a id="fn-7bdc5f2aa2e632bc"></a>

## check_database

源码：[L64](D:/Project/learnLittle/app/db/database.py:64)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

在两秒内开连接执行 SELECT 1，成功 True，SQL/超时/系统连接异常 False。只做数据库探针，不执行迁移。

**输入与签名**

```python
async def check_database(engine: AsyncEngine) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return True
return False
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
asyncio.timeout
engine.connect
connection.execute
text
```
