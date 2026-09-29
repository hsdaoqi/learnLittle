"""add note_templates table and notes fulltext index

Revision ID: e0f4a7b2c345
Revises: d9e3f6a1b234
Create Date: 2026-09-23 16:00:00.000000

note_templates：用户自定义笔记骨架。
ft_notes_title_content：MySQL ngram 全文索引；SQLite / 不支持 ngram 的环境跳过。
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
revision: str = "e0f4a7b2c345"
down_revision: Union[str, Sequence[str], None] = "d9e3f6a1b234"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "note_templates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("content_structure", sa.JSON(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.uuid"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_note_templates_user_id"), "note_templates", ["user_id"], unique=False)

    bind = op.get_bind()
    if bind.dialect.name == "mysql":
        op.execute(
            "ALTER TABLE notes ADD FULLTEXT INDEX ft_notes_title_content "
            "(title, content) WITH PARSER ngram"
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "mysql":
        op.execute("ALTER TABLE notes DROP INDEX ft_notes_title_content")
    op.drop_index(op.f("ix_note_templates_user_id"), table_name="note_templates")
    op.drop_table("note_templates")
