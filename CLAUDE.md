# 学生积分管理系统 v2.0

前后端分离的班级积分管理系统，面向教师，用于课堂积分激励。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + Vite 6 + Element Plus + Pinia + Vue Router |
| 后端 | FastAPI + SQLAlchemy (async) + Pydantic v2 |
| 数据库 | SQLite (aiosqlite) / PostgreSQL 15 (Docker) |
| 认证 | JWT (python-jose) + bcrypt |
| 构建 | PyInstaller (EXE 桌面版) / Docker |

## 目录结构

```
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── main.py          # 应用入口、路由注册、生命周期、自动迁移
│   │   ├── config.py        # pydantic-settings 配置
│   │   ├── database.py      # 异步引擎 + 会话工厂
│   │   ├── models/          # SQLAlchemy 模型 (User, Class, Student, Badge, PointsLog, PointsRule)
│   │   ├── schemas/         # Pydantic 请求/响应模型
│   │   ├── routes/          # API 路由 (auth, classes, students, badges, leaderboard, rules, admin)
│   │   ├── utils/           # 工具函数 (auth, deps, stats, security, exceptions, login_security)
│   │   ├── templates/       # 管理后台独立页面 (admin.html + static/)
│   │   └── static/          # 前端构建产物 (gitignore)
│   ├── requirements.txt
│   └── launch.py            # EXE 模式启动入口
│
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── views/           # 页面组件 (Login, Dashboard, Students, StudentDetail, Leaderboard, Badges, Tools, PointsLogs, Classes, Settings)
│   │   ├── components/      # 公共组件 (AppLayout.vue)
│   │   ├── stores/          # Pinia (auth.js, class.js)
│   │   ├── api/index.js     # Axios 实例 + 拦截器
│   │   ├── router/index.js  # 路由配置 + 守卫
│   │   └── assets/styles/   # 全局样式
│   ├── vite.config.js
│   └── package.json
│
├── build_exe/               # PyInstaller 构建配置
├── docs/                    # 项目文档
├── openspec/                # OpenSpec 项目规范
├── docker-compose.yml       # Docker 编排配置
├── nginx.conf               # Nginx 反向代理配置
├── deploy.sh                # 服务器部署脚本
├── .env                     # 环境变量 (gitignore)
├── 开发手册.md               # 完整开发文档
└── 启动系统.bat              # 一键启动脚本
```

## 开发命令

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8866
# API 文档: http://127.0.0.1:8866/docs
```

### 前端
```bash
cd frontend
npm install
npm run dev
# 访问: http://localhost:5173
```

### 构建 EXE
```bash
cd frontend && npm run build
xcopy dist ..\backend\static /E /I /Y
cd ..\build_exe && build.bat
# 产物: build_exe/dist/学生积分管理系统/
```

### Docker 部署
```bash
# 配置环境变量
cp .env.example .env  # 编辑 .env 填入 SECRET_KEY 和 DB_PASSWORD

# 一键部署
chmod +x deploy.sh
./deploy.sh

# 或手动操作
cd frontend && npm run build && cd ..
cp -r frontend/dist backend/static
docker-compose up -d --build
```

**服务架构:**
- `db`: PostgreSQL 15 Alpine，内存限制 256MB，优化了 2 核低内存配置
- `backend`: FastAPI + Gunicorn (2 workers)，端口 8866
- `frontend`: Nginx Alpine，端口 80，反向代理 API 到后端

**访问地址:**
- 前端: http://服务器IP
- API 文档: http://服务器IP:8866/docs
- 管理后台: http://服务器IP/admin-panel

## 架构要点

- **异步全链路**: 路由 → 业务逻辑 → 数据库全链路 async/await
- **依赖注入**: 通过 FastAPI `Depends()` 注入数据库会话 (`get_db`) 和当前用户 (`get_current_user`)
- **自动迁移**: `main.py` 的 `ensure_tables()` 中通过 PRAGMA/information_schema 检测列是否存在，自动 ALTER TABLE，无 Alembic
- **认证流程**: 登录(含图形验证码) → JWT(token 7天有效) → 前端 localStorage 存储 → Axios 拦截器自动附加 Authorization 头
- **管理后台**: 独立于前端教师端，`/admin-panel` 访问，自托管 Vue 3 + axios，深色主题
- **EXE 兼容**: `main.py` 通过 `sys.frozen` 检测 PyInstaller 环境，调整静态文件路径

## 代码约定

### Python (后端)
- 路由函数: `async def`，依赖注入用 `Depends()`
- 模型文件名与表对应: `class_.py` (避免关键字冲突)、`student.py`、`badge.py`、`points_log.py`
- Schema 与模型分离: schemas/ 目录下按实体分文件
- 配置通过 `pydantic-settings`，环境变量自动覆盖
- 错误处理: 全局异常处理器隐藏数据库细节，返回通用错误信息

### JavaScript (前端)
- Composition API (`setup()` 语法糖)
- Pinia store 使用 `defineStore` + `ref`/`computed` 模式
- API 调用统一通过 `api/index.js` 的 Axios 实例
- 路由懒加载: `() => import('../views/X.vue')`
- 状态持久化: token/user 存 localStorage，currentClassId 存 localStorage

## 关键文件速查

| 功能 | 文件 |
|------|------|
| 应用入口 + 迁移 | `backend/app/main.py` |
| 配置 | `backend/app/config.py` |
| 数据库引擎 | `backend/app/database.py` |
| 认证逻辑 | `backend/app/utils/auth.py`, `backend/app/utils/login_security.py` |
| 依赖注入 | `backend/app/utils/deps.py` |
| 统计逻辑 | `backend/app/utils/stats.py` |
| 安全中间件 | `backend/app/utils/security.py` |
| 前端 API 封装 | `frontend/src/api/index.js` |
| 前端路由 | `frontend/src/router/index.js` |
| 认证状态 | `frontend/src/stores/auth.js` |
| 班级状态 | `frontend/src/stores/class.js` |
| 主布局 | `frontend/src/components/AppLayout.vue` |
| 课堂工具 | `frontend/src/views/Tools.vue` |
| Docker 编排 | `docker-compose.yml` |
| Nginx 配置 | `nginx.conf` |
| 后端 Dockerfile | `backend/Dockerfile` |
| 部署脚本 | `deploy.sh` |

## 安全机制

- 密码: bcrypt 哈希，强度校验 (≥8位，含大小写+数字)
- 登录: 图形验证码(数学题)、失败锁定(5次/15分钟)、登录日志
- 输入: XSS 过滤 (student/schema field_validator)、SQL 注入防护 (SQLAlchemy 参数化)
- 响应: CSP 安全头、X-Content-Type-Options、X-Frame-Options
- 账号: `expires_at` 有效期控制，过期返回 403

## 数据库

- 默认 SQLite，通过 `DATABASE_URL` 环境变量可切换 PostgreSQL (asyncpg)
- 迁移方式: `main.py` 中 `ensure_tables()` 自动检测并添加/删除列
- 表关系: User → Class → Student → PointsLog / StudentBadge → Badge
- 管理员: `is_admin` 字段，通过 `INIT_ADMIN_USER`/`INIT_ADMIN_PASS` 环境变量初始化

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | 数据库连接串 | sqlite+aiosqlite:///./student_points.db |
| SECRET_KEY | JWT 签名密钥 | 需要修改默认值 |
| CORS_ORIGINS_STR | CORS 允许的源 | http://localhost:5173,http://localhost:3000 |
| INIT_ADMIN_USER | 初始管理员用户名 | - |
| INIT_ADMIN_PASS | 初始管理员密码 | - |
