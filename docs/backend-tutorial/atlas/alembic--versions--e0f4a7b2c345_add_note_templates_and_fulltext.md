# alembic/versions/e0f4a7b2c345_add_note_templates_and_fulltext.py

[源码](D:/Project/learnLittle/alembic/versions/e0f4a7b2c345_add_note_templates_and_fulltext.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

数据库增量迁移：创建 note_templates，并为 notes 建 MySQL ngram 全文索引。

## 本文件导航

- [upgrade](#fn-34824e6e6c991e51)
- [downgrade](#fn-019a7a69ad2ee7c8)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
revision: str = 'e0f4a7b2c345'

down_revision: Union[str, Sequence[str], None] = 'd9e3f6a1b234'

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None
```

<a id="fn-34824e6e6c991e51"></a>

## upgrade

源码：[L21](D:/Project/learnLittle/alembic/versions/e0f4a7b2c345_add_note_templates_and_fulltext.py:21)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

创建 note_templates，并为 notes 建 MySQL ngram 全文索引。由 Alembic 在此版本执行；不要把表定义 import 当成已经迁移。

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
sa.Integer
sa.String
sa.JSON
sa.DateTime
sa.text
sa.ForeignKeyConstraint
sa.PrimaryKeyConstraint
op.create_index
op.f
op.get_bind
op.execute
```

<a id="fn-019a7a69ad2ee7c8"></a>

## downgrade

源码：[L45](D:/Project/learnLittle/alembic/versions/e0f4a7b2c345_add_note_templates_and_fulltext.py:45)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

删除全文索引和模板表，已有模板内容丢失。逆向结构操作有数据风险，本教程不执行。

**输入与签名**

```python
def downgrade() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
op.get_bind
op.execute
op.drop_index
op.f
op.drop_table
```
