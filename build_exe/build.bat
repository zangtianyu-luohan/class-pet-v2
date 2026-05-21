@echo off
chcp 65001 >nul
echo ========================================
echo  学生积分管理系统 - 打包 EXE
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查前端构建...
if not exist "..\frontend\dist\index.html" (
    echo 前端未构建，开始构建...
    cd /d "%~dp0..\frontend"
    call npm run build
    cd /d "%~dp0"
)

echo [2/4] 复制前端产物到 backend\static...
if not exist "..\backend\static" mkdir "..\backend\static"
robocopy "..\frontend\dist" "..\backend\static" /s /e /r:0 /purge >nul
echo   前端文件已复制

echo       复制启动器到 backend 目录...
copy /y "launch.py" "..\backend\launch.py" >nul

echo [3/4] 安装/更新 PyInstaller...
set "VENV_PYTHON=%~dp0..\backend\.venv\Scripts\python.exe"
set "VENV_PIP=%~dp0..\backend\.venv\Scripts\pip.exe"
set "VENV_PYINSTALLER=%~dp0..\backend\.venv\Scripts\pyinstaller.exe"
"%VENV_PIP%" show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo   安装 PyInstaller...
    "%VENV_PIP%" install pyinstaller
) else (
    echo   PyInstaller 已安装
)

echo [4/4] 开始打包...
echo   这可能需要几分钟，请耐心等待...
echo.

"%VENV_PYTHON%" -m PyInstaller --clean --noconfirm --distpath "%~dp0dist" --workpath "%~dp0build" build.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo  打包失败！请检查错误信息
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo  打包完成！
echo ========================================
echo.
echo 输出目录: %~dp0dist\学生积分管理系统\
echo.
echo 使用方法:
echo   1. 复制 dist\学生积分管理系统\ 整个文件夹到目标电脑
echo   2. 运行 学生积分管理系统.exe
echo   3. 浏览器会自动打开 http://localhost:8866
echo   4. 默认管理员: admin / Admin123456
echo.

:: 复制启动脚本到输出目录
copy /y "launch.spec" "%~dp0dist\学生积分管理系统\" >nul 2>&1

echo 按任意键打开输出目录...
pause >nul
explorer "%~dp0dist\学生积分管理系统"
