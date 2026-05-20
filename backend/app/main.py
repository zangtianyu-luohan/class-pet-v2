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

    from sqlalchemy import text
    # 检测数据库类型：PostgreSQL vs SQLite
    is_sqlite = str(engine.url).startswith("sqlite")

    async def _col_exists(conn, table, column):
        """检查列是否已存在（跨数据库兼容）"""
        if is_sqlite:
            result = await conn.execute(text(f"PRAGMA table_info({table})"))
            return any(row[1] == column for row in result.fetchall())
        else:
            result = await conn.execute(text(
                f"SELECT EXISTS (SELECT 1 FROM information_schema.columns "
                f"WHERE table_name='{table}' AND column_name='{column}')"
            ))
            return result.scalar()

    async def _add_column(conn, table, column, col_def):
        """添加列（如果不存在）"""
        if not await _col_exists(conn, table, column):
            await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}"))
            print(f"[OK] Migration: added {column} to {table}")
        else:
            print(f"[OK] Migration: {column} already exists in {table}")

    async def _drop_column(conn, table, column):
        """删除列（如果存在）"""
        if await _col_exists(conn, table, column):
            await conn.execute(text(f"ALTER TABLE {table} DROP COLUMN {column}"))
            print(f"[OK] Migration: dropped {column} from {table}")
        else:
            print(f"[OK] Migration: {column} already absent from {table}")

    # 自动迁移：确保 expires_at 列存在
    try:
        async with engine.begin() as conn:
            await _add_column(conn, "users", "expires_at", "TIMESTAMPTZ DEFAULT NULL" if not is_sqlite else "TEXT DEFAULT NULL")
    except Exception as e:
        print(f"[SKIP] Migration expires_at: {e}")

    # 自动迁移：确保 is_admin 列存在
    try:
        async with engine.begin() as conn:
            await _add_column(conn, "users", "is_admin", "BOOLEAN DEFAULT FALSE")
    except Exception as e:
        print(f"[SKIP] Migration is_admin: {e}")

    # 自动迁移：删除 students 表的 pet_type 和 pet_name 列
    for col in ['pet_type', 'pet_name']:
        try:
            async with engine.begin() as conn:
                await _drop_column(conn, "students", col)
        except Exception as e:
            print(f"[SKIP] Migration drop {col}: {e}")

    # 自动迁移：删除 students 表的 avatar/level/experience 列
    for col in ['avatar', 'level', 'experience']:
        try:
            async with engine.begin() as conn:
                await _drop_column(conn, "students", col)
        except Exception as e:
            print(f"[SKIP] Migration drop {col}: {e}")

    # 自动迁移：确保已存在的管理员账号 is_admin=TRUE
    init_user = os.environ.get("INIT_ADMIN_USER")
    if init_user:
        try:
            async with engine.begin() as conn:
                await conn.execute(text("UPDATE users SET is_admin = TRUE WHERE username = :u"), {"u": init_user})
            print(f"[OK] Migration: admin user '{init_user}' is_admin set to TRUE")
        except Exception as e:
            print(f"[SKIP] Migration admin is_admin: {e}")
    else:
        # 兜底：没有 INIT_ADMIN_USER 时，把有班级的用户设为管理员
        try:
            async with engine.begin() as conn:
                await conn.execute(text("UPDATE users SET is_admin = TRUE WHERE id IN (SELECT DISTINCT owner_id FROM classes)"))
            print("[OK] Migration: class owners set as admin")
        except Exception as e:
            print(f"[SKIP] Migration class owners admin: {e}")

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
                    text("UPDATE users SET password_hash = :p, is_admin = TRUE WHERE username = :u"),
                    {"p": pw_hash, "u": init_user}
                )
                print(f"[OK] Admin user '{init_user}' password updated, is_admin=TRUE")
            else:
                await session.execute(
                    text("INSERT INTO users (username, password_hash, display_name, is_admin) VALUES (:u, :p, :d, TRUE)"),
                    {"u": init_user, "p": pw_hash, "d": "管理员"}
                )
                print(f"[OK] Admin user '{init_user}' created with is_admin=TRUE")
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


# PyInstaller 打包兼容：检测是否在打包环境中运行
if getattr(sys, 'frozen', False):
    # 打包后：资源在 _MEIPASS 目录下
    _BUNDLE_DIR = sys._MEIPASS
else:
    # 开发环境：正常路径
    _BUNDLE_DIR = os.path.dirname(os.path.dirname(__file__))


# 管理后台独立页面
TEMPLATES_DIR = os.path.join(_BUNDLE_DIR, "app", "templates") if getattr(sys, 'frozen', False) else os.path.join(os.path.dirname(__file__), "templates")
ADMIN_STATIC_DIR = os.path.join(TEMPLATES_DIR, "static")

if os.path.isdir(ADMIN_STATIC_DIR):
    app.mount("/admin-assets", StaticFiles(directory=ADMIN_STATIC_DIR), name="admin-assets")


@app.get("/admin-panel", response_class=HTMLResponse)
async def admin_panel():
    html_path = os.path.join(TEMPLATES_DIR, "admin.html")
    if os.path.exists(html_path):
        return HTMLResponse(content=open(html_path, encoding="utf-8").read())
    return HTMLResponse(content="<h1>管理后台页面未找到</h1>", status_code=404)


# 静态文件服务（前端）- 使用 StaticFiles 中间件，比 Python FileResponse 快得多
STATIC_DIR = os.path.join(_BUNDLE_DIR, "static") if getattr(sys, 'frozen', False) else os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.isdir(STATIC_DIR):
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import Response
    import mimetypes

    class GzipCacheMiddleware(BaseHTTPMiddleware):
        """为 StaticFiles 提供 gzip 预压缩和长期缓存"""
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            path = request.url.path
            # 为所有静态资源添加缓存头
            if path.startswith("/assets/") or path.startswith("/admin-assets/"):
                response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
                # 检查是否可以返回 .gz 版本
                accept = request.headers.get("accept-encoding", "")
                if "gzip" in accept:
                    if path.startswith("/assets/"):
                        file_path = os.path.join(STATIC_DIR, path.lstrip("/"))
                    else:
                        file_path = os.path.join(ADMIN_STATIC_DIR, path.lstrip("/admin-assets/"))
                    gz_path = file_path + ".gz"
                    if os.path.isfile(gz_path):
                        ct, _ = mimetypes.guess_type(file_path)
                        return Response(
                            content=open(gz_path, "rb").read(),
                            media_type=ct,
                            headers={
                                "Content-Encoding": "gzip",
                                "Vary": "Accept-Encoding",
                                "Cache-Control": "public, max-age=31536000, immutable",
                            },
                        )
            return response

    app.add_middleware(GzipCacheMiddleware)
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """前端 SPA 路由兜底：非 API/静态路径都返回 index.html"""
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path, headers={"Cache-Control": "no-cache"})
        return FileResponse(os.path.join(STATIC_DIR, "index.html"), headers={"Cache-Control": "no-cache"})
