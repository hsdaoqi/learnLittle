"""add model_traces and model_pricing

Revision ID: c3e9f2a7b890
Revises: e2aebef3f9e7
Create Date: 2026-09-28 18:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3e9f2a7b890"
down_revision: Union[str, Sequence[str], None] = "e2aebef3f9e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "model_traces",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("request_id", sa.String(length=32), nullable=True),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("session_id", sa.String(length=36), nullable=True),
        sa.Column("stage", sa.String(length=20), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_model_traces_request_id"), "model_traces", ["request_id"])
    op.create_index("idx_traces_user_created", "model_traces", ["user_id", "created_at"])
    op.create_index("idx_traces_session_created", "model_traces", ["session_id", "created_at"])

    op.create_table(
        "model_pricing",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("input_price_per_1k", sa.Float(), nullable=False),
        sa.Column("output_price_per_1k", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model"),
    )


def downgrade() -> None:
    op.drop_table("model_pricing")
    op.drop_index("idx_traces_session_created", table_name="model_traces")
    op.drop_index("idx_traces_user_created", table_name="model_traces")
    op.drop_index(op.f("ix_model_traces_request_id"), table_name="model_traces")
    op.drop_table("model_traces")
