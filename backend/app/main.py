from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .config import settings
from .database import engine, Base
from .routes import (
    auth_router, classes_router, students_router,
    badges_router, leaderboard_router, rules_router,
)
from .admin import setup_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Database tables ready")
    yield
    # 关闭时清理
    await engine.dispose()
    print("[OK] App shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Session 中间件（管理后台需要）
app.add_middleware(SessionMiddleware, secret_key="session-secret-key-change-me")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(auth_router)
app.include_router(classes_router)
app.include_router(students_router)
app.include_router(badges_router)
app.include_router(leaderboard_router)
app.include_router(rules_router)

# 注册管理后台
setup_admin(app)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
