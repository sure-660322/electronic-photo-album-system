"""FastAPI 应用入口：路由挂载、统一错误结构与启动准备。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .errors import register_error_handlers
from .routers import albums, auth, categories, photos
from .services.storage import LocalPhotoStorage


@asynccontextmanager
async def lifespan(app: FastAPI):
    LocalPhotoStorage().ensure_root()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="电子相册系统 API", version="0.1.0", lifespan=lifespan)
    register_error_handlers(app)

    app.include_router(auth.router, prefix="/api")
    app.include_router(categories.router, prefix="/api")
    app.include_router(albums.router, prefix="/api")
    app.include_router(photos.router, prefix="/api")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
