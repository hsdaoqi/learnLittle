# alembic/versions/e471331632c9_initial_users_table.py

[源码](D:/Project/learnLittle/alembic/versions/e471331632c9_initial_users_table.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

数据库增量迁移：创建 users 和用户名索引，作为后续用户外键起点。

## 本文件导航

- [upgrade](#fn-6e3d238b6fcf44e4)
- [downgrade](#fn-cd5a316b42e9ccee)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
revision: str = 'e471331632c9'

down_revision: Union[str, Sequence[str], None] = None

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None
```

<a id="fn-6e3d238b6fcf44e4"></a>

## upgrade

源码：[L21](D:/Project/learnLittle/alembic/versions/e471331632c9_initial_users_table.py:21)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

创建 users 和用户名索引，作为后续用户外键起点。由 Alembic 在此版本执行；不要把表定义 import 当成已经迁移。

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
sa.Text
sa.DateTime
sa.text
sa.PrimaryKeyConstraint
sa.UniqueConstraint
op.create_index
op.f
```

<a id="fn-cd5a316b42e9ccee"></a>

## downgrade

源码：[L41](D:/Project/learnLittle/alembic/versions/e471331632c9_initial_users_table.py:41)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

删除用户索引与 users 表，所有用户行会丢失。逆向结构操作有数据风险，本教程不执行。

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
