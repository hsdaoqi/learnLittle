"""Track manual titles and scoped message idempotency."""

from alembic import op
import sqlalchemy as sa

revision = "f1a244c10001"
down_revision = "c3e9f2a7b890"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("chat_sessions", sa.Column(
        "title_manual", sa.Boolean(), nullable=False, server_default=sa.text("0")
    ))
    # Existing non-default titles may be user-authored; preserve them.
    op.execute(sa.text("UPDATE chat_sessions SET title_manual = 1 WHERE title <> '新对话'"))
    op.add_column("chat_messages", sa.Column("idempotency_key", sa.String(64), nullable=True))
    op.create_index("uq_chat_message_idempotency", "chat_messages", ["idempotency_key"], unique=True)


def downgrade():
    op.drop_index("uq_chat_message_idempotency", table_name="chat_messages")
    op.drop_column("chat_messages", "idempotency_key")
    op.drop_column("chat_sessions", "title_manual")
