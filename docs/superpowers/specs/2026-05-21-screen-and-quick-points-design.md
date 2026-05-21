# 学生积分管理系统 - 大屏展示 + 快速加分 + Docker 部署设计文档

## 概述

本文档描述了学生积分管理系统的三个核心功能增强：
1. 大屏展示页面 - 投屏展示，全班互动
2. 快速加分功能 - 提高课堂操作效率
3. Docker 部署方案 - 服务器部署

## 一、整体架构

### 页面结构

```
frontend/src/
├── views/
│   ├── Dashboard.vue          # 首页，增加"进入大屏"按钮 + 悬浮按钮
│   └── Screen.vue             # 大屏展示页面（新增）
├── components/
│   ├── screen/                # 大屏卡片组件（新增）
│   │   ├── RankCard.vue       # 排行榜卡片
│   │   ├── DynamicCard.vue    # 实时动态卡片
│   │   ├── TimerCard.vue      # 计时器卡片
│   │   └── RandomCard.vue     # 随机点名卡片
│   └── QuickPoints.vue        # 快速加分面板（新增）
└── stores/
    └── screen.js              # 大屏状态管理（新增）
```

### 后端新增

```
backend/app/
├── routes/
│   └── sse.py                 # SSE 端点（新增）
└── utils/
    └── sse_manager.py         # SSE 连接管理（新增）
```

### 数据流

```
教师在任意页面加分/扣分
    ↓
后端 API 处理积分变更
    ↓
SSE Manager 广播事件
    ↓
大屏页面接收事件
    ↓
更新对应卡片（排行榜、动态、特效）
```

## 二、大屏展示页面

### 页面路由

```
/screen  →  大屏展示页面
```

### 页面布局

```
┌─────────────────────────────────────────────────────────┐
│  [排行榜卡片]        [实时动态卡片]        [计时器卡片]  │
│     可拖拽              可拖拽               可拖拽      │
│     可调整大小          可调整大小           可调整大小   │
│                                                         │
│  [随机点名卡片]       [其他卡片...]        [其他卡片...] │
│     可拖拽              可拖拽               可拖拽      │
│     可调整大小          可调整大小           可调整大小   │
└─────────────────────────────────────────────────────────┘
```

### 卡片组件设计

#### 1. 排行榜卡片 (RankCard.vue)

**功能**：
- 显示全班学生名字 + 积分
- 支持滚动查看
- 实时更新（SSE 推送）

**样式**：
- 深色背景
- 学生名字 + 积分数字
- 积分变化动画（绿色/红色）

#### 2. 实时动态卡片 (DynamicCard.vue)

**功能**：
- 显示今天所有积分变化
- 实时滚动更新
- 显示：学生名字 + 积分变化 + 原因

**样式**：
- 深色背景
- 新记录从底部进入
- 积分变化颜色区分（绿色加分/红色扣分）

#### 3. 计时器卡片 (TimerCard.vue)

**功能**：
- 正计时，记录课堂时长
- 开始/暂停/重置按钮

**样式**：
- 深色背景
- 大号数字显示
- 按钮样式

#### 4. 随机点名卡片 (RandomCard.vue)

**功能**：
- 显示随机点名结果
- 开始点名按钮
- 显示已点过的学生

**样式**：
- 深色背景
- 大号名字显示
- 按钮样式

### 特效设计

#### 加分特效
- **颜色**：绿色 (#10b981)
- **动画**：
  1. 卡片闪烁（0.5 秒）
  2. 数字飞入（+10 从右侧飞入，1 秒后消失）

#### 扣分特效
- **颜色**：红色 (#ef4444)
- **动画**：
  1. 卡片闪烁（0.5 秒）
  2. 数字飞入（-5 从右侧飞入，1 秒后消失）

### 数据流

```
教师在任意页面加分/扣分
    ↓
后端 API 处理积分变更
    ↓
SSE Manager 广播事件
    ↓
大屏页面接收事件
    ↓
更新对应卡片（排行榜、动态、特效）
```

## 三、快速加分功能

### 入口

- **位置**：Dashboard 首页右下角悬浮按钮
- **样式**：圆形按钮，显示 "+" 图标
- **点击**：弹出快速加分面板

### 面板布局

```
┌─────────────────────────────────────────────────────────┐
│  搜索框：[搜索学生...]                    [排序▼] [×关闭] │
├─────────────────────────────────────────────────────────┤
│  学生列表：                                              │
│  ┌─────────────────────────────────────────────────────┐│
│  │ [✓] 小明 (2024001)  当前积分: 85  [+5] [+10] [-5]  ││
│  │ [ ] 小红 (2024002)  当前积分: 72  [+5] [+10] [-5]  ││
│  │ [ ] 小刚 (2024003)  当前积分: 68  [+5] [+10] [-5]  ││
│  │ ...                                                 ││
│  └─────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────┤
│  批量操作：                                              │
│  原因：[选择预设原因▼] [自定义原因...]                    │
│  分值：[+5] [+10] [-5] [自定义: ___]                     │
│  按钮：[批量加分] [撤销上一步]                            │
├─────────────────────────────────────────────────────────┤
│  最近操作：                                              │
│  1. 小明 +10 回答问题  (14:30)                          │
│  2. 小红 -5 纪律问题   (14:28)                          │
│  3. 小刚 +5 作业优秀   (14:25)                          │
└─────────────────────────────────────────────────────────┘
```

### 功能设计

#### 1. 学生列表
- 显示学生名字、学号、当前积分
- 支持勾选多个学生（批量操作）
- 支持搜索学生
- 支持排序（按积分、姓名）

#### 2. 快捷按钮
- 每个学生旁边有 +5、+10、-5 按钮
- 点击后直接加分/扣分
- 支持自定义分值

#### 3. 加分原因
- 系统预设原因：
  - 回答问题
  - 作业优秀
  - 课堂表现好
  - 纪律问题
  - 卫生问题
- 支持自定义原因

#### 4. 批量操作
- 勾选多个学生
- 选择统一原因
- 选择统一分值
- 点击"批量加分"按钮

#### 5. 撤销功能
- 支持撤销上一步操作
- 显示撤销按钮

#### 6. 操作记录
- 显示最近 5 条操作记录
- 包含：学生名字、分值、原因、时间

### 数据流

```
教师点击快捷按钮/批量加分
    ↓
调用后端 API 加分/扣分
    ↓
更新学生积分
    ↓
更新操作记录
    ↓
触发 SSE 广播（大屏页面更新）
```

## 四、SSE 实时推送

### SSE 端点

```
GET /api/sse/events
```

### 事件类型

#### 1. 积分变化事件
```json
{
  "type": "points_change",
  "data": {
    "student_id": 1,
    "student_name": "小明",
    "points": 10,
    "reason": "回答问题",
    "timestamp": "2024-01-15T14:30:00Z"
  }
}
```

#### 2. 学生添加事件
```json
{
  "type": "student_add",
  "data": {
    "student_id": 4,
    "student_name": "小华",
    "student_no": "2024004"
  }
}
```

#### 3. 学生删除事件
```json
{
  "type": "student_delete",
  "data": {
    "student_id": 4,
    "student_name": "小华"
  }
}
```

#### 4. 勋章颁发事件
```json
{
  "type": "badge_award",
  "data": {
    "student_id": 1,
    "student_name": "小明",
    "badge_name": "学习之星",
    "badge_icon": "⭐"
  }
}
```

### 心跳机制

- **间隔**：60 秒
- **格式**：
```json
{
  "type": "heartbeat",
  "timestamp": "2024-01-15T14:30:00Z"
}
```

### 连接管理

- **连接数限制**：无限制
- **超时时间**：无超时
- **重连机制**：客户端自动重连

### 后端实现

```python
# backend/app/routes/sse.py

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter()

# SSE 连接管理
class SSEManager:
    def __init__(self):
        self.connections = []
    
    async def connect(self, request):
        # 创建新的连接
        queue = asyncio.Queue()
        self.connections.append(queue)
        return queue
    
    def disconnect(self, queue):
        # 断开连接
        self.connections.remove(queue)
    
    async def broadcast(self, event):
        # 广播事件到所有连接
        for queue in self.connections:
            await queue.put(event)

sse_manager = SSEManager()

@router.get("/api/sse/events")
async def sse_events(request):
    async def event_generator():
        queue = await sse_manager.connect(request)
        try:
            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
        except asyncio.CancelledError:
            sse_manager.disconnect(queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

### 前端实现

```javascript
// frontend/src/api/sse.js

class SSEClient {
  constructor() {
    this.eventSource = null
    this.listeners = {}
  }
  
  connect() {
    this.eventSource = new EventSource('/api/sse/events')
    
    this.eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.emit(data.type, data.data)
    }
    
    this.eventSource.onerror = () => {
      // 自动重连
      setTimeout(() => this.connect(), 3000)
    }
  }
  
  on(eventType, callback) {
    if (!this.listeners[eventType]) {
      this.listeners[eventType] = []
    }
    this.listeners[eventType].push(callback)
  }
  
  emit(eventType, data) {
    if (this.listeners[eventType]) {
      this.listeners[eventType].forEach(callback => callback(data))
    }
  }
  
  disconnect() {
    if (this.eventSource) {
      this.eventSource.close()
    }
  }
}

export const sseClient = new SSEClient()
```

### 使用示例

```javascript
// 在大屏页面中使用
import { sseClient } from '../api/sse'

onMounted(() => {
  sseClient.connect()
  
  sseClient.on('points_change', (data) => {
    // 更新排行榜
    updateRankList(data)
    // 显示特效
    showPointsEffect(data)
  })
})

onUnmounted(() => {
  sseClient.disconnect()
})
```

## 五、Docker 部署方案

### 服务器信息

- **IP**：124.223.107.60
- **系统**：CentOS 8
- **CPU**：2 核
- **内存**：1.7GB（可用 1.3GB）
- **磁盘**：50GB（可用 45GB）

### 目录结构

```
/root/student-points/
├── docker-compose.yml          # Docker Compose 配置文件
├── .env                        # 环境变量配置文件
├── backend/                    # 后端代码
├── frontend/                   # 前端代码（构建后）
├── postgres/                   # PostgreSQL 数据目录
└── backups/                    # 备份目录
```

### Docker Compose 配置

```yaml
version: '3.8'

services:
  # PostgreSQL 数据库
  db:
    image: postgres:15-alpine
    container_name: student-points-db
    restart: always
    environment:
      POSTGRES_DB: student_points
      POSTGRES_USER: ztylh
      POSTGRES_PASSWORD: Zty256310x！
      TZ: Asia/Shanghai
      PGTZ: Asia/Shanghai
    volumes:
      - ./postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    command: >
      postgres
      -c shared_buffers=64MB
      -c work_mem=4MB
      -c max_connections=10
      -c log_statement=none
      -c log_min_duration_statement=-1
      -c idle_in_transaction_session_timeout=0
      -c deadlock_timeout=1s
      -c maintenance_work_mem=64MB
      -c effective_cache_size=128MB
      -c wal_buffers=4MB
      -c checkpoint_segments=8
      -c autovacuum=on
      -c autovacuum_vacuum_scale_factor=0.1
      -c autovacuum_analyze_scale_factor=0.05
      -c listen_addresses='*'
      -c password_encryption=trust
    deploy:
      resources:
        limits:
          memory: 256M
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ztylh -d student_points"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI 后端
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: student-points-backend
    restart: always
    environment:
      DATABASE_URL: postgresql+asyncpg://ztylh:Zty256310x！@db:5432/student_points
      SECRET_KEY: ${SECRET_KEY}
      TZ: Asia/Shanghai
      LANG: zh_CN.UTF-8
    ports:
      - "8866:8866"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: >
      gunicorn app.main:app
      --workers 2
      --worker-class uvicorn.workers.UvicornWorker
      --bind 0.0.0.0:8866
      --timeout 30
      --keep-alive 60

  # 前端静态文件（Nginx）
  frontend:
    image: nginx:alpine
    container_name: student-points-frontend
    restart: always
    environment:
      TZ: Asia/Shanghai
    ports:
      - "80:80"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend

networks:
  default:
    driver: bridge
```

### 环境变量配置 (.env)

```bash
# 自动生成的 SECRET_KEY
SECRET_KEY=your-auto-generated-secret-key-here
```

### Nginx 配置 (nginx.conf)

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://backend:8866;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 30s;
    }

    # SSE 代理
    location /api/sse/ {
        proxy_pass http://backend:8866;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 60s;
    }
}
```

### 后端 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8866

# 启动命令
CMD ["gunicorn", "app.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8866", "--timeout", "30", "--keep-alive", "60"]
```

### 部署脚本

```bash
#!/bin/bash

# 设置变量
PROJECT_DIR="/root/student-points"
REPO_URL="your-git-repo-url"

# 创建目录
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# 克隆代码
git clone $REPO_URL .

# 生成 SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)
echo "SECRET_KEY=$SECRET_KEY" > .env

# 构建前端
cd frontend
npm install
npm run build
cp -r dist ../backend/static
cd ..

# 构建并启动服务
docker-compose up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 验证部署
echo "验证部署..."
curl -s http://localhost:8866/health || echo "后端服务启动失败"
curl -s http://localhost || echo "前端服务启动失败"

echo "部署完成！"
echo "访问地址: http://124.223.107.60"
echo "API 文档: http://124.223.107.60:8866/docs"
```

### 访问地址

- **前端（教师端）**：http://124.223.107.60
- **管理后台**：http://124.223.107.60/admin-panel
- **API 文档**：http://124.223.107.60:8866/docs
- **数据库**：124.223.107.60:5432

## 六、技术栈

- **前端**：Vue 3 + Vite + Element Plus + vue-grid-layout
- **后端**：FastAPI + SQLAlchemy + Gunicorn + Uvicorn
- **数据库**：PostgreSQL 15
- **部署**：Docker + Docker Compose + Nginx

## 七、开发计划

### 阶段一：SSE 实时推送（1-2 天）
- 后端 SSE 端点
- SSE 连接管理
- 前端 SSE 客户端

### 阶段二：大屏展示页面（2-3 天）
- 页面布局
- 排行榜卡片
- 实时动态卡片
- 计时器卡片
- 随机点名卡片
- 拖拽布局
- 深色模式
- 积分变化特效

### 阶段三：快速加分功能（1-2 天）
- 悬浮按钮
- 快速加分面板
- 批量操作
- 预设原因
- 撤销功能
- 操作记录

### 阶段四：Docker 部署（1 天）
- Docker Compose 配置
- Nginx 配置
- 部署脚本
- 服务器部署

### 阶段五：测试和优化（1-2 天）
- 功能测试
- 性能优化
- Bug 修复

## 八、验收标准

### 大屏展示页面
- [ ] 排行榜卡片显示全班学生名字 + 积分
- [ ] 实时动态卡片显示今天所有积分变化
- [ ] 计时器卡片支持正计时
- [ ] 随机点名卡片支持随机点名
- [ ] 卡片支持拖拽调整位置和大小
- [ ] 支持深色模式
- [ ] 加分有绿色特效
- [ ] 扣分有红色特效
- [ ] 实时更新（SSE 推送）

### 快速加分功能
- [ ] 悬浮按钮在首页右下角
- [ ] 学生列表显示名字、学号、当前积分
- [ ] 每个学生旁边有 +5、+10、-5 按钮
- [ ] 支持自定义分值
- [ ] 支持搜索学生
- [ ] 支持排序（按积分、姓名）
- [ ] 支持批量操作
- [ ] 支持预设原因
- [ ] 支持撤销功能
- [ ] 显示最近 5 条操作记录

### Docker 部署
- [ ] PostgreSQL 数据库正常运行
- [ ] FastAPI 后端正常运行
- [ ] Nginx 前端正常运行
- [ ] 访问地址可正常访问
- [ ] API 文档可正常访问
- [ ] 管理后台可正常访问
