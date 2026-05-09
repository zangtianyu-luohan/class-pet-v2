# 班级OK萌宠 v2.0

前后端分离的班级积分管理系统。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| 后端 | FastAPI + SQLAlchemy (async) |
| 数据库 | SQLite (开发) / PostgreSQL (生产) |
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

## 部署

### 1. Supabase 数据库
1. 注册 https://supabase.com
2. 创建项目，获取 PostgreSQL 连接字符串
3. 修改 `backend/.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres.xxx:password@aws-0-xx.pooler.supabase.com:6543/postgres
```

### 2. Render 后端
1. 连接 GitHub 仓库
2. 设置 Build Command: `pip install -r requirements.txt`
3. 设置 Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. 添加环境变量

### 3. Vercel 前端
1. 连接 GitHub 仓库
2. Framework: Vite
3. 添加环境变量 `VITE_API_URL` 指向 Render 后端地址
