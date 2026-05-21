# 项目约定

## 项目名称
学生积分管理系统 v2.0

## 目录结构
```
backend/          # FastAPI 后端
  app/
    models/       # SQLAlchemy 数据模型
    schemas/      # Pydantic 请求/响应模型
    routes/       # API 路由
    utils/        # 工具函数（JWT、密码哈希）
    services/     # 业务逻辑（待扩展）
frontend/         # Vue 3 前端
  src/
    views/        # 页面组件
    stores/       # Pinia 状态管理
    api/          # Axios 实例
    components/   # 公共组件
    router/       # 路由配置
```

## 数据模型
- User：教师账号（username, password_hash, display_name, is_admin, expires_at）
- Class：班级（name, description, owner_id）
- Student：学生（student_no, name, points, class_id）
- PointsLog：积分日志（student_id, points, reason, category, operator_id）
- Badge / StudentBadge：勋章及颁发记录
- PointsRule：积分规则模板

## API 约定
- 前缀：/api/
- 认证：Authorization: Bearer <token>
- 分页：?page=1&page_size=20
- 错误格式：{"detail": "错误信息"}

## 前端约定
- 状态管理：Pinia（auth.js 管认证，class.js 管班级）
- HTTP 客户端：Axios，拦截器自动加 token、处理 401
- UI 组件库：Element Plus
- 日期处理：dayjs

## 数据库
- SQLite（本地文件，零配置）
- ORM：SQLAlchemy 2.0 async
