# alembic/versions/c8d2e5f0a123_add_chat_sessions_and_messages.py

[源码](D:/Project/learnLittle/alembic/versions/c8d2e5f0a123_add_chat_sessions_and_messages.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

数据库增量迁移：创建 chat_sessions 与 chat_messages 及关联索引。

## 本文件导航

- [upgrade](#fn-75e78d58a32ea4ee)
- [downgrade](#fn-a3945c471120c476)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
revision: str = 'c8d2e5f0a123'

down_revision: Union[str, Sequence[str], None] = 'b7c1d4e8f901'

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None
```

<a id="fn-75e78d58a32ea4ee"></a>

## upgrade

源码：[L20](D:/Project/learnLittle/alembic/versions/c8d2e5f0a123_add_chat_sessions_and_messages.py:20)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

创建 chat_sessions 与 chat_messages 及关联索引。由 Alembic 在此版本执行；不要把表定义 import 当成已经迁移。

**输入与签名**

```python
def upgrade() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
op.create_table
sa.Column
sa.String
sa.DateTime
sa.text
sa.ForeignKeyConstraint
sa.PrimaryKeyConstraint
op.create_index
op.f
sa.Integer
sa.Text
```

<a id="fn-a3945c471120c476"></a>

## downgrade

源码：[L45](D:/Project/learnLittle/alembic/versions/c8d2e5f0a123_add_chat_sessions_and_messages.py:45)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

删除消息再会话的索引和表，聊天数据会丢失。逆向结构操作有数据风险，本教程不执行。

**输入与签名**

```python
def downgrade() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
op.drop_index
op.f
op.drop_table
```
