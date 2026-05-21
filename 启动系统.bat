@echo off
chcp 65001 >nul 2>&1
title 学生积分管理系统 v2.0
echo.
echo  学生积分管理系统 v2.0
echo  =====================================
echo.

:: 启动后端（后台）
echo [1/2] 启动后端 API (FastAPI)...
cd /d "%~dp0backend"
start "后端-API" cmd /c ".venv\Scripts\python.exe launch.py"

:: 等待后端启动
timeout /t 3 /nobreak >nul

:: 启动前端（后台）
echo [2/2] 启动前端 (Vite)...
cd /d "%~dp0frontend"
start "前端-Vite" cmd /c "npx vite --host 0.0.0.0"

echo.
echo  启动完成！
echo  =====================================
echo  教师端:    http://localhost:5173
echo  后端API:   http://127.0.0.1:8866/docs
echo  管理后台:  http://127.0.0.1:8866/admin-panel
echo  管理员:    admin / Admin123456
echo  =====================================
echo.
echo  按任意键关闭此窗口（服务会在后台继续运行）
echo  停止服务请关闭 [后端-API] 和 [前端-Vite] 窗口
echo.
pause >nul
