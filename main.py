import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import Settings, get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.rate_limit import RateLimitMiddleware
from app.core.scheduler import init_scheduler, shutdown_scheduler
from app.db import redis_client
from app.db.database import create_database_engine, create_session_factory
from app.rag import vector_store as vector_store_module
from app.routers.category_router import router as category_router
from app.routers.chat_router import router as chat_router
from app.routers.health import router as health_router
from app.routers.knowledge_router import router as knowledge_router
from app.routers.note_router import router as note_router
from app.routers.note_template_router import router as note_template_router
from app.routers.review_router import router as review_router
from app.routers.usage_router import router as usage_router
from app.routers.user import router as user_router
from app.services import usage_service

logger = logging.getLogger(__name__)

# 业务路由统一挂在这个前缀下；健康检查等探针保持在根路径
API_PREFIX = "/api/v1"


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings: Settings = settings or get_settings()
    app_settings.validate_security()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        owns_engine = not hasattr(app.state, "db_session_factory")
        if owns_engine:
            engine = create_database_engine(app_settings)
            app.state.db_engine = engine
            app.state.db_session_factory = create_session_factory(engine=engine)
        else:
            engine = None
        await redis_client.init_redis(app_settings)
        vector_store_module.init_vector_store(app_settings)
        usage_service.set_session_factory(app.state.db_session_factory)
        try:
            async with app.state.db_session_factory() as db:
                await usage_service.seed_model_pricing(db, app_settings)
                await db.commit()
        except Exception:
            logger.warning("模型定价种子失败，费用将记为 0", exc_info=True)
        if not app_settings.api_reload and app_settings.app_env != "test":
            init_scheduler()
        yield
        usage_service.set_session_factory(None)
        shutdown_scheduler()
        vector_store_module.close_vector_store()
        await redis_client.close_redis()
        if engine is not None:
            await engine.dispose()

    app = FastAPI(
        title=app_settings.app_name,
        version=app_settings.app_version,
        lifespan=lifespan,
    )
    app.state.settings = app_settings
    register_exception_handlers(app)
    app.add_middleware(RateLimitMiddleware)
    app.include_router(health_router)
    app.include_router(user_router, prefix=API_PREFIX, tags=["User & Auth"])
    app.include_router(category_router, prefix=API_PREFIX, tags=["Category"])
    app.include_router(note_router, prefix=API_PREFIX, tags=["Note"])
    app.include_router(note_template_router, prefix=API_PREFIX, tags=["Note Template"])
    app.include_router(review_router, prefix=API_PREFIX, tags=["Review"])
    app.include_router(knowledge_router, prefix=API_PREFIX, tags=["Knowledge"])
    app.include_router(chat_router, prefix=API_PREFIX, tags=["Chat"])
    app.include_router(usage_router, prefix=API_PREFIX, tags=["Usage"])

    avatar_root = Path(app_settings.avatar_dir)
    avatar_root.mkdir(parents=True, exist_ok=True)
    app.mount(
        "/static/avatars", StaticFiles(directory=str(avatar_root)), name="avatars"
    )
    return app


app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
