import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text

from app.core.task_runner import drain_background_tasks
from app.schemas.note import NoteCreate
from app.services import note_service
from app.services.usage_service import parse_usage


def test_note_index_dispatches_after_commit_not_rollback_or_metadata_changes(client, monkeypatch):
    from app.models.user import User

    factory = client.app.state.db_session_factory
    indexed = []

    async def index(note):
        indexed.append((note.id, note.title))

    monkeypatch.setattr(note_service, "_try_index", index)

    async def run():
        async with factory() as db:
            db.add(User(uuid="index-user", username="index-user", password="unused"))
            await db.commit()
            note = await note_service.create_note(db, "index-user", NoteCreate(title="first", content="body"))
            note_id = note.id
            assert not indexed
            await db.commit()
        await drain_background_tasks()
        assert indexed == [(note_id, "first")]
        async with factory() as db:
            await note_service.update_note(db, "index-user", note_id, {"is_pinned": True, "tags": ["tag"]})
            await db.commit()
        await drain_background_tasks()
        assert len(indexed) == 1
        async with factory() as db:
            await note_service.update_note(db, "index-user", note_id, {"title": "rolled-back"})
            await db.rollback()
        await drain_background_tasks()
        assert len(indexed) == 1
        async with factory() as db:
            await note_service.update_note(db, "index-user", note_id, {"title": "committed"})
            await db.commit()
        await drain_background_tasks()
        assert indexed[-1] == (note_id, "committed")

    client.portal.call(run)


def test_hot_cache_rebuild_preserves_chronological_order(client):
    from app.rag.chat_cache import get_recent_messages, rebuild_messages

    async def run():
        rows = [{"id": i, "role": "user", "content": str(i)} for i in range(1, 31)]
        await rebuild_messages("test-cache", rows, buffer_size=20)
        result = await get_recent_messages("test-cache")
        assert [row["id"] for row in result] == list(range(11, 31))

    client.portal.call(run)


def test_usage_preserves_provider_zero_counts():
    assert parse_usage({"usage": {"prompt_tokens": 7, "completion_tokens": 0}}, "long prompt", "tool") == (7, 0, 7)
    assert parse_usage(None, "abc", "ab") == (2, 1, 3)


def test_additive_chat_migration_preserves_existing_titles_and_messages(tmp_path):
    path = Path(__file__).parents[1] / "alembic/versions/f1a244c10001_chat_lifecycle.py"
    spec = importlib.util.spec_from_file_location("chat_migration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    engine = create_engine(f"sqlite:///{tmp_path / 'migration.db'}")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE chat_sessions (id VARCHAR(36) PRIMARY KEY, title VARCHAR(200) NOT NULL)"))
        connection.execute(text("CREATE TABLE chat_messages (id INTEGER PRIMARY KEY, content TEXT NOT NULL)"))
        connection.execute(text("INSERT INTO chat_sessions VALUES ('one', '新对话'), ('two', 'existing title')"))
        connection.execute(text("INSERT INTO chat_messages VALUES (1, 'existing message')"))
        module.op = Operations(MigrationContext.configure(connection))
        module.upgrade()
        assert connection.execute(text("SELECT id, title_manual FROM chat_sessions ORDER BY id")).all() == [
            ("one", 0), ("two", 1),
        ]
        assert connection.scalar(text("SELECT content FROM chat_messages")) == "existing message"
        assert "idempotency_key" in {column["name"] for column in inspect(connection).get_columns("chat_messages")}
        module.downgrade()
        assert connection.scalar(text("SELECT content FROM chat_messages")) == "existing message"
        assert "title_manual" not in {column["name"] for column in inspect(connection).get_columns("chat_sessions")}
    engine.dispose()
