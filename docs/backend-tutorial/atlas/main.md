# main.py

[源码](D:/Project/learnLittle/main.py) | [任务流程 01](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

应用装配与生命周期；路由/资源从这里接上，不包含全部业务逻辑。

## 本文件导航

- [create_app](#fn-362780824346b51c)
- [create_app.lifespan](#fn-2e089080453c71fd)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

API_PREFIX = '/api/v1'

app = create_app()
```

<a id="fn-362780824346b51c"></a>

## create_app

源码：[L35](D:/Project/learnLittle/main.py:35)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

应用组装入口，接收可选 Settings，校验生产密钥后创建 FastAPI、异常处理、中间件、业务路由和头像静态挂载。返回应用对象；这一步会创建头像目录，但数据库/Redis 的运行资源在 lifespan 中准备。

**输入与签名**

```python
def create_app(settings: Settings | None=None) -> FastAPI
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return app
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_settings
app_settings.validate_security
FastAPI
register_exception_handlers
app.add_middleware
app.include_router
Path
avatar_root.mkdir
app.mount
StaticFiles
str
```

<a id="fn-2e089080453c71fd"></a>

## create_app.lifespan

源码：[L40](D:/Project/learnLittle/main.py:40)；任务：[第 01 章](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md)。

ASGI 启停上下文：没有注入 factory 才创建 engine，初始化 Redis/向量/用量，播种定价并按条件开清理任务。yield 后按顺序等待后台任务、关闭各资源，只 dispose 自己创建的 engine；不要把构造 app 与执行这段生命周期混淆。

**输入与签名**

```python
async def lifespan(app: FastAPI) -> AsyncIterator[None]
```

装饰器/挂载：

```python
@asynccontextmanager
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
yield None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
hasattr
create_database_engine
create_session_factory
redis_client.init_redis
vector_store_module.init_vector_store
usage_service.set_session_factory
app.state.db_session_factory
usage_service.seed_model_pricing
db.commit
logger.warning
init_scheduler
drain_background_tasks
shutdown_scheduler
vector_store_module.close_vector_store
redis_client.close_redis
engine.dispose
```
