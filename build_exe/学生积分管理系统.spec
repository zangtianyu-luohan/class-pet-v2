# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['..\\backend\\launch.py'],
    pathex=['.', 'D:\\QwenPaw\\Library\\bin'],
    binaries=[('D:\\QwenPaw\\Library\\bin\\libssl-3-x64.dll', '.'), ('D:\\QwenPaw\\Library\\bin\\libcrypto-3-x64.dll', '.'), ('D:\\QwenPaw\\Library\\bin\\ffi.dll', '.'), ('D:\\QwenPaw\\Library\\bin\\ffi-7.dll', '.'), ('D:\\QwenPaw\\Library\\bin\\ffi-8.dll', '.'), ('D:\\QwenPaw\\Library\\bin\\liblzma.dll', '.'), ('D:\\QwenPaw\\Library\\bin\\libbz2.dll', '.'), ('D:\\QwenPaw\\Library\\bin\\libexpat.dll', '.'), ('D:\\QwenPaw\\Library\\bin\\sqlite3.dll', '.'), ('D:\\QwenPaw\\Library\\bin\\zlib.dll', '.')],
    datas=[('C:\\Users\\53205\\Desktop\\资料\\罗涵\\学习积分管理系统\\backend\\static', 'static'), ('C:\\Users\\53205\\Desktop\\资料\\罗涵\\学习积分管理系统\\backend\\app\\templates', 'app/templates')],
    hiddenimports=['uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'fastapi', 'starlette', 'sqlalchemy', 'sqlalchemy.ext.asyncio', 'aiosqlite', 'pydantic', 'pydantic_settings', 'jose', 'bcrypt', 'passlib', 'passlib.handlers', 'passlib.handlers.bcrypt', 'multipart', 'app', 'app.main', 'app.config', 'app.database', 'app.models', 'app.models.user', 'app.models.class_', 'app.models.student', 'app.models.badge', 'app.models.points_log', 'app.models.points_rule', 'app.models.login_log', 'app.schemas', 'app.schemas.user', 'app.schemas.student', 'app.schemas.class_', 'app.schemas.badge', 'app.routes', 'app.routes.auth', 'app.routes.classes', 'app.routes.students', 'app.routes.badges', 'app.routes.leaderboard', 'app.routes.rules', 'app.routes.admin', 'app.utils', 'app.utils.auth', 'app.utils.deps', 'app.utils.security', 'app.utils.exceptions', 'app.utils.login_security'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'pytest', 'PIL', 'cv2'],
    noarchive=False,
    optimize=0,
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
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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
