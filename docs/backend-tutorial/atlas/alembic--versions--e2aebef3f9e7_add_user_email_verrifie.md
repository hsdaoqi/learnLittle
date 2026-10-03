# alembic/versions/e2aebef3f9e7_add_user_email_verrifie.py

[源码](D:/Project/learnLittle/alembic/versions/e2aebef3f9e7_add_user_email_verrifie.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

数据库增量迁移：为 users 增加非空 email_verified 字段；迁移未设服务端默认，已有数据部署需审查。

## 本文件导航

- [upgrade](#fn-9c6d52d84aa3b128)
- [downgrade](#fn-46445797d29122a5)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
revision: str = 'e2aebef3f9e7'

down_revision: Union[str, Sequence[str], None] = '53816adf617f'

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None
```

<a id="fn-9c6d52d84aa3b128"></a>

## upgrade

源码：[L21](D:/Project/learnLittle/alembic/versions/e2aebef3f9e7_add_user_email_verrifie.py:21)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

为 users 增加非空 email_verified 字段；迁移未设服务端默认，已有数据部署需审查。由 Alembic 在此版本执行；不要把表定义 import 当成已经迁移。

**输入与签名**

```python
def upgrade() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
op.add_column
sa.Column
sa.Boolean
```

<a id="fn-46445797d29122a5"></a>

## downgrade

源码：[L28](D:/Project/learnLittle/alembic/versions/e2aebef3f9e7_add_user_email_verrifie.py:28)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

删除 email_verified 字段，原验证状态信息丢失。逆向结构操作有数据风险，本教程不执行。

**输入与签名**

```python
def downgrade() -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
op.drop_column
```
