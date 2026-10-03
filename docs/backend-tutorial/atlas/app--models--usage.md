# app/models/usage.py

[源码](D:/Project/learnLittle/app/models/usage.py) | [任务流程 09](D:/Project/learnLittle/docs/backend-tutorial/09-operations.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

model_traces 与 model_pricing 数据结构，不是独立工具审计表。

## 本文件导航

本文件没有显式函数；请看下方结构声明，不计作遗漏。

## 类与字段

### ModelTrace

一次模型调用的归属、阶段、模型、Token、耗时及成败；没有完整工具参数审计。

声明位置：[L21](D:/Project/learnLittle/app/models/usage.py:21)。父类：`Base`。

```python
__tablename__ = 'model_traces'

id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, 'sqlite'), primary_key=True, autoincrement=True)

request_id: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)

user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

stage: Mapped[str | None] = mapped_column(String(20), nullable=True)

model: Mapped[str | None] = mapped_column(String(100), nullable=True)

prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

success: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=True)

error: Mapped[str | None] = mapped_column(Text, nullable=True)

created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

__table_args__ = (Index('idx_traces_user_created', 'user_id', 'created_at'), Index('idx_traces_session_created', 'session_id', 'created_at'))
```

### ModelPricing

本地每千 Token 输入/输出价格与币种；不是实时官方定价。

声明位置：[L50](D:/Project/learnLittle/app/models/usage.py:50)。父类：`Base`。

```python
__tablename__ = 'model_pricing'

id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

model: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

input_price_per_1k: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

output_price_per_1k: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

currency: Mapped[str] = mapped_column(String(10), nullable=False, default='CNY')

updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
```
