# app/rag/chat_cache.py

[源码](D:/Project/learnLittle/app/rag/chat_cache.py) | [任务流程 08](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

会话列表短 TTL、近期消息 List；不是新 Agent 的唯一记忆。

## 本文件导航

- [sessions_key](#fn-a20862baf8c8bc32)
- [messages_key](#fn-688d0d95d99a8ea5)
- [_dumps](#fn-748470551d253d2c)
- [_loads](#fn-4600989f4390306e)
- [dump_message](#fn-9eb052546e5dc636)
- [get_session_list](#fn-0b8c2c2073e084d9)
- [set_session_list](#fn-806c55595cd3868d)
- [invalidate_session_list](#fn-52cacb1b0eb37708)
- [get_recent_messages](#fn-e7afee0922d35b75)
- [push_message](#fn-fa4319afdea3aa59)
- [rebuild_messages](#fn-ead03261544176d6)
- [delete_messages](#fn-c388b6761cca61c1)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
logger = logging.getLogger(__name__)

DEFAULT_BUFFER_SIZE = 20

DEFAULT_SESSION_LIST_TTL = 300
```

<a id="fn-a20862baf8c8bc32"></a>

## sessions_key

源码：[L25](D:/Project/learnLittle/app/rag/chat_cache.py:25)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

生成按用户隔离的聊天会话列表 key。列表缓存不会把全部用户放在同一值内。

**输入与签名**

```python
def sessions_key(user_id: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'chat:sessions:{user_id}'
```

<a id="fn-688d0d95d99a8ea5"></a>

## messages_key

源码：[L29](D:/Project/learnLittle/app/rag/chat_cache.py:29)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

生成按会话组织的热消息 List key。调用者要先校验会话归属，key 本身不是权限检查。

**输入与签名**

```python
def messages_key(session_id: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return f'chat:msgs:{session_id}'
```

<a id="fn-748470551d253d2c"></a>

## _dumps

源码：[L33](D:/Project/learnLittle/app/rag/chat_cache.py:33)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

把缓存值编码为保留中文的 JSON，非原生 JSON 对象用 str 兜底。用于存储，不保证任意对象可还原为原类型。

**输入与签名**

```python
def _dumps(value: Any) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return json.dumps(value, ensure_ascii=False, default=str)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
json.dumps
```

<a id="fn-4600989f4390306e"></a>

## _loads

源码：[L37](D:/Project/learnLittle/app/rag/chat_cache.py:37)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

将 Redis 字符串解为 JSON 值。缓存入口负责捕获坏值异常并回退 SQL。

**输入与签名**

```python
def _loads(raw: str) -> Any
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return json.loads(raw)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
json.loads
```

<a id="fn-9eb052546e5dc636"></a>

## dump_message

源码：[L41](D:/Project/learnLittle/app/rag/chat_cache.py:41)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

兼容实体/字典抽出消息身份、角色、正文与时间。给消息热缓存保存可还原的 JSON 字段，不把 ORM 内部状态写入 Redis。

**输入与签名**

```python
def dump_message(message: Any) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'id': message.get('id'), 'session_id': message.get('session_id'), 'role': message.get('role'), 'content': message.get('content'), 'created_at': message.get('created_at')}
return {'id': message.id, 'session_id': message.session_id, 'role': message.role, 'content': message.content, 'created_at': created.isoformat() if isinstance(created, datetime) else created}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
getattr
isinstance
message.get
created.isoformat
```

<a id="fn-0b8c2c2073e084d9"></a>

## get_session_list

源码：[L60](D:/Project/learnLittle/app/rag/chat_cache.py:60)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

GET 并解列表，缺失/类型不对/异常均返回 None 表示 miss。空列表是合法命中，不要当故障。

**输入与签名**

```python
async def get_session_list(user_id: str) -> list[dict] | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
return data if isinstance(data, list) else None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().get
get_redis
sessions_key
_loads
isinstance
logger.debug
```

<a id="fn-806c55595cd3868d"></a>

## set_session_list

源码：[L74](D:/Project/learnLittle/app/rag/chat_cache.py:74)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

将列表 JSON 写入 Redis 并设最少一秒 TTL，失败仅日志。SQL 事实不因缓存不可写而消失。

**输入与签名**

```python
async def set_session_list(user_id: str, sessions: list[dict], ttl: int=DEFAULT_SESSION_LIST_TTL) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().set
get_redis
sessions_key
_dumps
max
logger.warning
```

<a id="fn-52cacb1b0eb37708"></a>

## invalidate_session_list

源码：[L85](D:/Project/learnLittle/app/rag/chat_cache.py:85)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

删除某用户列表缓存，下次读从 SQL 重建。是失效动作，不删除会话。

**输入与签名**

```python
async def invalidate_session_list(user_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().delete
get_redis
sessions_key
logger.debug
```

<a id="fn-e7afee0922d35b75"></a>

## get_recent_messages

源码：[L94](D:/Project/learnLittle/app/rag/chat_cache.py:94)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

LRANGE 取全部热列表，反转成旧到新；空或异常返回 None。内部 List 最新在前，外部使用时间正序。

**输入与签名**

```python
async def get_recent_messages(session_id: str) -> list[dict] | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
return messages
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().lrange
get_redis
messages_key
_loads
messages.reverse
logger.debug
```

<a id="fn-fa4319afdea3aa59"></a>

## push_message

源码：[L110](D:/Project/learnLittle/app/rag/chat_cache.py:110)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

序列化消息后 LPUSH，并 LTRIM 保留 buffer_size。这里没有设置消息 List TTL，别把会话列表 TTL 自动套到它。

**输入与签名**

```python
async def push_message(session_id: str, message: Any, buffer_size: int=DEFAULT_BUFFER_SIZE) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
messages_key
redis.lpush
_dumps
dump_message
redis.ltrim
max
logger.warning
```

<a id="fn-ead03261544176d6"></a>

## rebuild_messages

源码：[L126](D:/Project/learnLittle/app/rag/chat_cache.py:126)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

清原 List，从输入正序消息取最近 N 条，逐个 LPUSH 重建最新在前结构。读回来再反转，必须保持这一组顺序约定。

**输入与签名**

```python
async def rebuild_messages(session_id: str, messages: list[Any], buffer_size: int=DEFAULT_BUFFER_SIZE) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis
messages_key
redis.delete
list
max
redis.lpush
_dumps
dump_message
logger.warning
```

<a id="fn-c388b6761cca61c1"></a>

## delete_messages

源码：[L145](D:/Project/learnLittle/app/rag/chat_cache.py:145)；任务：[第 08 章](D:/Project/learnLittle/docs/backend-tutorial/08-memory.md)。

删会话的热消息键，失败只记日志。会话 SQL 删除由 service 负责。

**输入与签名**

```python
async def delete_messages(session_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
get_redis().delete
get_redis
messages_key
logger.debug
```
