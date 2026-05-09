import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .routes import (
    auth_router, classes_router, students_router,
    badges_router, leaderboard_router, rules_router,
)

# 是否在 Vercel 上运行
IS_VERCEL = os.environ.get("VERCEL") == "1"

# 表是否已初始化
_tables_created = False


async def ensure_tables():
    """确保数据库表已创建（幂等）"""
    global _tables_created
    if _tables_created:
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _tables_created = True
    print("[OK] Database tables ready")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_tables()
    yield
    if not IS_VERCEL:
        await engine.dispose()
        print("[OK] App shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

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

# 管理后台（仅本地模式下启用，Vercel serverless 不支持静态资源）
if not IS_VERCEL:
    try:
        from starlette.middleware.sessions import SessionMiddleware
        app.add_middleware(SessionMiddleware, secret_key="session-secret-key-change-me")
        from .admin import setup_admin
        setup_admin(app)
    except Exception as e:
        print(f"[WARN] Admin panel disabled: {e}")


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
