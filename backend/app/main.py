import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

# 修复 Railway 日志级别：uvicorn 默认输出到 stderr，Railway 把 stderr 标为 error
# 将 uvicorn 的日志重定向到 stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s",
    stream=sys.stdout,
    force=True,
)
for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    logging.getLogger(name).handlers = [logging.StreamHandler(sys.stdout)]
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .config import settings
from .database import engine, Base, AsyncSession
from .routes import (
    auth_router, classes_router, students_router,
    badges_router, leaderboard_router, rules_router, admin_router,
)
from .utils.security import SecurityHeadersMiddleware
from .utils.exceptions import (
    integrity_error_handler, operational_error_handler,
    programming_error_handler, generic_error_handler,
)
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError

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

    # 自动迁移：确保 expires_at 列存在
    from sqlalchemy import text
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ DEFAULT NULL"))
        print("[OK] Migration: expires_at column ensured")
    except Exception as e:
        print(f"[SKIP] Migration check: {e}")

    # 通过环境变量初始化管理员（一次性使用后删除该变量）
    init_user = os.environ.get("INIT_ADMIN_USER")
    init_pass = os.environ.get("INIT_ADMIN_PASS")
    if init_user and init_pass:
        from .utils.auth import hash_password
        from sqlalchemy import text
        async with AsyncSession(engine) as session:
            result = await session.execute(
                text("SELECT id FROM users WHERE username = :u"), {"u": init_user}
            )
            existing = result.scalar()
            pw_hash = hash_password(init_pass)
            if existing:
                await session.execute(
                    text("UPDATE users SET password_hash = :p WHERE username = :u"),
                    {"p": pw_hash, "u": init_user}
                )
                print(f"[OK] Admin user '{init_user}' password updated")
            else:
                await session.execute(
                    text("INSERT INTO users (username, password_hash, display_name) VALUES (:u, :p, :d)"),
                    {"u": init_user, "p": pw_hash, "d": "管理员"}
                )
                print(f"[OK] Admin user '{init_user}' created")
            await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_tables()
    yield
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

# 安全响应头
app.add_middleware(SecurityHeadersMiddleware)

# 全局异常处理器（隐藏数据库错误细节）
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(OperationalError, operational_error_handler)
app.add_exception_handler(ProgrammingError, programming_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# 注册 API 路由
app.include_router(auth_router)
app.include_router(classes_router)
app.include_router(students_router)
app.include_router(badges_router)
app.include_router(leaderboard_router)
app.include_router(rules_router)
app.include_router(admin_router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


# 管理后台独立页面
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
ADMIN_STATIC_DIR = os.path.join(TEMPLATES_DIR, "static")

if os.path.isdir(ADMIN_STATIC_DIR):
    app.mount("/admin-assets", StaticFiles(directory=ADMIN_STATIC_DIR), name="admin-assets")


@app.get("/admin-panel", response_class=HTMLResponse)
async def admin_panel():
    html_path = os.path.join(TEMPLATES_DIR, "admin.html")
    if os.path.exists(html_path):
        return HTMLResponse(content=open(html_path, encoding="utf-8").read())
    return HTMLResponse(content="<h1>管理后台页面未找到</h1>", status_code=404)


# 静态文件服务（前端）- 统一走 catch-all 以支持 gzip 预压缩
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.isdir(STATIC_DIR):

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str, request: Request):
        """前端 SPA 路由兜底：非 API 路径都返回 index.html；支持 .gz 预压缩"""
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            # 如果浏览器支持 gzip 且存在 .gz 文件，优先返回压缩版本
            accept = request.headers.get("accept-encoding", "")
            gz_path = file_path + ".gz"
            if "gzip" in accept and os.path.isfile(gz_path):
                import mimetypes
                ct, _ = mimetypes.guess_type(file_path)
                return FileResponse(gz_path, media_type=ct, headers={"Content-Encoding": "gzip", "Vary": "Accept-Encoding", "Cache-Control": "public, max-age=31536000, immutable"})
            return FileResponse(file_path, headers={"Cache-Control": "public, max-age=31536000, immutable"})
        # index.html 不缓存，确保总是最新
        return FileResponse(os.path.join(STATIC_DIR, "index.html"), headers={"Cache-Control": "no-cache"})
