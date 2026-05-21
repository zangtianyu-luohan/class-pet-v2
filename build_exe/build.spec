# -*- mode: python ; coding: utf-8 -*-
"""
学生积分管理系统 - PyInstaller 打包配置
"""

import os
import sys

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(SPEC)))
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')
STATIC_DIR = os.path.join(BACKEND_DIR, 'static')
TEMPLATES_DIR = os.path.join(BACKEND_DIR, 'app', 'templates')
ADMIN_STATIC_DIR = os.path.join(TEMPLATES_DIR, 'static')

# 收集数据文件
datas = [
    # 前端构建产物
    (STATIC_DIR, 'static'),
    # 管理后台模板
    (TEMPLATES_DIR, 'app/templates'),
    # 管理后台静态文件
    (ADMIN_STATIC_DIR, 'app/templates/static'),
]

# 收集隐藏导入（确保所有依赖被打包）
hiddenimports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'starlette',
    'sqlalchemy',
    'sqlalchemy.ext.asyncio',
    'aiosqlite',
    'pydantic',
    'pydantic_settings',
    'jose',
    'passlib',
    'bcrypt',
    'multipart',
    'app',
    'app.main',
    'app.config',
    'app.database',
    'app.models',
    'app.models.user',
    'app.models.class_',
    'app.models.student',
    'app.models.badge',
    'app.models.points_log',
    'app.schemas',
    'app.schemas.user',
    'app.schemas.student',
    'app.schemas.class_',
    'app.schemas.badge',
    'app.routes',
    'app.routes.auth',
    'app.routes.classes',
    'app.routes.students',
    'app.routes.badges',
    'app.routes.leaderboard',
    'app.routes.rules',
    'app.routes.admin',
    'app.utils',
    'app.utils.auth',
    'app.utils.deps',
    'app.utils.stats',
    'app.utils.security',
    'app.utils.exceptions',
    'app.utils.login_security',
]

a = Analysis(
    ['launch.py'],
    pathex=[BACKEND_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', '_tkinter',
        'matplotlib', 'numpy', 'pandas',
        'pytest', 'unittest',
        'PIL', 'cv2',
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='学生积分管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 显示控制台窗口，方便查看日志
    icon=None,  # 可以后续添加 .ico 图标
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='学生积分管理系统',
)
