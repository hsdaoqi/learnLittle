"""测试夹具。

用文件级 SQLite（aiosqlite）替代 MySQL、fakeredis 替代 Redis、
Chroma EphemeralClient 替代持久化向量库，跑真实路由逻辑。
"""

import chromadb
import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import Settings
from app.db import redis_client as redis_module
from app.db.database import get_db_session
from app.models.base import Base
from app.rag.embeddings import reset_embedding_cache, set_embed_fn
from app.rag.hyde import set_hyde_fn
from app.rag.memory import set_summary_fn
from app.rag.rag_route import set_route_fn
from app.rag.rag_summarize import set_summarize_fn
from app.services.note_ai_service import set_note_ai_fn
from app.ai_service.react_agent import set_react_streamer
from app.rag.retriever import reset_cross_encoder, set_rerank_fn
from app.rag.vector_store import VectorStoreService, close_vector_store, set_vector_store
from main import create_app


@pytest.fixture(autouse=True)
def isolated_configuration(monkeypatch):
    from app.config import get_settings
    from app.ai_service.plan_execute import set_plan_fn, set_plan_streamer
    from app.ai_service.query_classifier import set_classifier_fn
    from app.ai_service.reflection import set_critique_fn

    monkeypatch.setitem(Settings.model_config, "env_file", None)
    get_settings.cache_clear()
    yield
    set_plan_fn(None)
    set_plan_streamer(None)
    set_classifier_fn(None)
    set_critique_fn(None)
    set_react_streamer(None)
    get_settings.cache_clear()


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path.as_posix()}")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    redis_module.set_redis(fakeredis.aioredis.FakeRedis(decode_responses=True))

    settings = Settings(
        _env_file=None,
        app_env="test",
        upload_dir=str(tmp_path / "uploads"),
        avatar_dir=str(tmp_path / "avatars"),
        chroma_persist_dir=str(tmp_path / "chroma"),
        llm_api_key="",
        embedding_api_key="",
        rate_limit_enabled=False,
        registration_require_email=False,
    )
    set_vector_store(VectorStoreService(settings, client=chromadb.EphemeralClient()))
    app = create_app(settings)
    app.state.db_session_factory = session_factory

    import asyncio

    async def _create_tables():
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        await engine.dispose()

    asyncio.run(_create_tables())
    from app.services.usage_service import set_session_factory as set_usage_session_factory

    set_usage_session_factory(session_factory)

    async def override_session():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_session

    try:
        with TestClient(app) as test_client:
            try:
                yield test_client
            finally:
                from app.core.task_runner import drain_background_tasks

                test_client.portal.call(drain_background_tasks)
                test_client.portal.call(engine.dispose)
    finally:
        close_vector_store()
        set_embed_fn(None)
        set_rerank_fn(None)
        reset_cross_encoder()
        set_hyde_fn(None)
        set_route_fn(None)
        set_summary_fn(None)
        set_summarize_fn(None)
        set_note_ai_fn(None)
        set_react_streamer(None)
        reset_embedding_cache()
        from app.services.usage_service import clear_trace_context, set_session_factory

        clear_trace_context()
        set_session_factory(None)
