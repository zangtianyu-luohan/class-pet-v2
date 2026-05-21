# 学生积分管理系统 v2.0

前后端分离的班级积分管理系统。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| 后端 | FastAPI + SQLAlchemy (async) |
| 数据库 | SQLite |
| 认证 | JWT |

## 本地开发

### 启动后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 启动前端
```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### API 文档
访问 http://localhost:8000/api/docs (Swagger UI)

## 构建 EXE 桌面版

```bash
cd frontend && npm run build
xcopy dist ..\backend\static /E /I /Y
cd ..\build_exe && build.bat
```

构建产物输出到 `build_exe/dist/学生积分管理系统/`，双击 EXE 即可运行（默认 http://127.0.0.1:8866）。
