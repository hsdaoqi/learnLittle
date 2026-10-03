# alembic/versions/c3e9f2a7b890_add_model_traces_and_pricing.py

[源码](D:/Project/learnLittle/alembic/versions/c3e9f2a7b890_add_model_traces_and_pricing.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

数据库增量迁移：创建 model_traces 与 model_pricing，建立用户/会话时间聚合索引。

## 本文件导航

- [upgrade](#fn-a5774736f51dbb6c)
- [downgrade](#fn-a4a12276f942ab74)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
revision: str = 'c3e9f2a7b890'

down_revision: Union[str, Sequence[str], None] = 'e2aebef3f9e7'

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None
```

<a id="fn-a5774736f51dbb6c"></a>

## upgrade

源码：[L20](D:/Project/learnLittle/alembic/versions/c3e9f2a7b890_add_model_traces_and_pricing.py:20)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

创建 model_traces 与 model_pricing，建立用户/会话时间聚合索引。由 Alembic 在此版本执行；不要把表定义 import 当成已经迁移。

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
sa.BigInteger
sa.String
sa.Integer
sa.Boolean
sa.Text
sa.DateTime
sa.text
sa.PrimaryKeyConstraint
op.create_index
op.f
sa.Float
sa.UniqueConstraint
```

<a id="fn-a4a12276f942ab74"></a>

## downgrade

源码：[L55](D:/Project/learnLittle/alembic/versions/c3e9f2a7b890_add_model_traces_and_pricing.py:55)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

删除模型用量与定价相关索引和表，计量历史丢失。逆向结构操作有数据风险，本教程不执行。

**输入与签名**

```python
def downgrade() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
op.drop_table
op.drop_index
op.f
```
