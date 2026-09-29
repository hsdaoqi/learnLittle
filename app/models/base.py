"""SQLAlchemy 基础模型定义。

所有 ORM 模型共享同一个 Base，使用 SQLAlchemy 2.0 声明式写法。
Alembic 的 target_metadata 也来自这里的 Base.metadata。
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 ORM 模型的公共声明式基类。"""
