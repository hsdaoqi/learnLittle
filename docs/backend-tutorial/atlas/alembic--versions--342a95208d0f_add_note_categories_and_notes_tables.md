# alembic/versions/342a95208d0f_add_note_categories_and_notes_tables.py

[源码](D:/Project/learnLittle/alembic/versions/342a95208d0f_add_note_categories_and_notes_tables.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

数据库增量迁移：创建 note_categories 自引用分类表与 notes 表及关联索引。

## 本文件导航

- [upgrade](#fn-d996d320306ea61e)
- [downgrade](#fn-498d798fc0effc3d)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
revision: str = '342a95208d0f'

down_revision: Union[str, Sequence[str], None] = 'e471331632c9'

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None
```

<a id="fn-d996d320306ea61e"></a>

## upgrade

源码：[L21](D:/Project/learnLittle/alembic/versions/342a95208d0f_add_note_categories_and_notes_tables.py:21)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

创建 note_categories 自引用分类表与 notes 表及关联索引。由 Alembic 在此版本执行；不要把表定义 import 当成已经迁移。

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
sa.Integer
sa.DateTime
sa.text
sa.ForeignKeyConstraint
sa.PrimaryKeyConstraint
op.create_index
op.f
sa.Text
sa.JSON
sa.Boolean
```

<a id="fn-498d798fc0effc3d"></a>

## downgrade

源码：[L62](D:/Project/learnLittle/alembic/versions/342a95208d0f_add_note_categories_and_notes_tables.py:62)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

先删除笔记再分类的相关索引和表，笔记/分类数据会丢失。逆向结构操作有数据风险，本教程不执行。

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
