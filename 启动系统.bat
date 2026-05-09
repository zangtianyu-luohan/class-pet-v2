@echo off
chcp 65001 >nul 2>&1
title 班级OK萌宠 v2.0
echo.
echo  🐾 班级OK萌宠 v2.0 - 前后端分离版
echo  =====================================
echo.

:: 启动后端
echo [1/2] 启动后端 API (FastAPI)...
cd /d "%~dp0backend"
start /B D:\QwenPaw\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

:: 启动前端
echo [2/2] 启动前端 (Vite)...
cd /d "%~dp0frontend"
start /B npx vite --host 0.0.0.0

echo.
echo  ✅ 启动完成！
echo  前端地址: http://localhost:5173
echo  后端API:  http://localhost:8000/api/docs
echo.
echo  按任意键关闭此窗口（服务会在后台继续运行）
pause >nul
