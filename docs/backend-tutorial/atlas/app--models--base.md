# app/models/base.py

[源码](D:/Project/learnLittle/app/models/base.py) | [任务流程 01](D:/Project/learnLittle/docs/backend-tutorial/01-structure.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

全体 ORM 的声明式 Base，向 Alembic 暴露 metadata。

## 本文件导航

本文件没有显式函数；请看下方结构声明，不计作遗漏。

## 类与字段

### Base

ORM 共享声明式基类，Base.metadata 收集表结构；本身没有业务字段或显式函数。

声明位置：[L10](D:/Project/learnLittle/app/models/base.py:10)。父类：`DeclarativeBase`。
