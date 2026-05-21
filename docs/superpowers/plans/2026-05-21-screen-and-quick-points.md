# 大屏展示 + 快速加分 + Docker 部署 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 实现大屏展示页面、快速加分功能和 Docker 部署方案

**架构：** 前端使用 Vue 3 + vue-grid-layout 实现大屏拖拽布局，后端使用 FastAPI + SSE 实现实时推送，部署使用 Docker + PostgreSQL + Nginx

**技术栈：** Vue 3, Vite, Element Plus, vue-grid-layout, FastAPI, SQLAlchemy, PostgreSQL, Docker, Nginx

---

## 文件结构

### 后端新增文件
- `backend/app/utils/sse_manager.py` - SSE 连接管理
- `backend/app/routes/sse.py` - SSE 路由
- `backend/Dockerfile` - 后端 Docker 镜像

### 前端新增文件
- `frontend/src/api/sse.js` - SSE 客户端
- `frontend/src/stores/screen.js` - 大屏状态管理
- `frontend/src/views/Screen.vue` - 大屏展示页面
- `frontend/src/components/screen/RankCard.vue` - 排行榜卡片
- `frontend/src/components/screen/DynamicCard.vue` - 实时动态卡片
- `frontend/src/components/screen/TimerCard.vue` - 计时器卡片
- `frontend/src/components/screen/RandomCard.vue` - 随机点名卡片
- `frontend/src/components/QuickPoints.vue` - 快速加分面板

### 前端修改文件
- `frontend/src/views/Dashboard.vue` - 添加"进入大屏"按钮 + 悬浮按钮
- `frontend/src/router/index.js` - 添加大屏路由

### 部署文件
- `docker-compose.yml` - Docker Compose 配置
- `nginx.conf` - Nginx 配置
- `.env` - 环境变量
- `deploy.sh` - 部署脚本

---

## 任务 1：后端 SSE 连接管理

**文件：**
- 创建：`backend/app/utils/sse_manager.py`

- [ ] **步骤 1：创建 SSE 管理器类**

```python
# backend/app/utils/sse_manager.py

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any


class SSEManager:
    """SSE 连接管理器"""

    def __init__(self):
        self.connections: List[asyncio.Queue] = []

    async def connect(self) -> asyncio.Queue:
        """创建新的 SSE 连接"""
        queue = asyncio.Queue()
        self.connections.append(queue)
        return queue

    def disconnect(self, queue: asyncio.Queue):
        """断开 SSE 连接"""
        if queue in self.connections:
            self.connections.remove(queue)

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """广播事件到所有连接"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        for queue in self.connections:
            await queue.put(event)

    async def broadcast_points_change(self, student_id: int, student_name: str, points: int, reason: str):
        """广播积分变化事件"""
        await self.broadcast("points_change", {
            "student_id": student_id,
            "student_name": student_name,
            "points": points,
            "reason": reason
        })

    async def broadcast_student_add(self, student_id: int, student_name: str, student_no: str):
        """广播学生添加事件"""
        await self.broadcast("student_add", {
            "student_id": student_id,
            "student_name": student_name,
            "student_no": student_no
        })

    async def broadcast_student_delete(self, student_id: int, student_name: str):
        """广播学生删除事件"""
        await self.broadcast("student_delete", {
            "student_id": student_id,
            "student_name": student_name
        })

    async def broadcast_badge_award(self, student_id: int, student_name: str, badge_name: str, badge_icon: str):
        """广播勋章颁发事件"""
        await self.broadcast("badge_award", {
            "student_id": student_id,
            "student_name": student_name,
            "badge_name": badge_name,
            "badge_icon": badge_icon
        })

    async def send_heartbeat(self):
        """发送心跳事件"""
        await self.broadcast("heartbeat", {})


# 全局 SSE 管理器实例
sse_manager = SSEManager()
```

- [ ] **步骤 2：验证文件创建**

运行：`ls -la backend/app/utils/sse_manager.py`
预期：文件存在

- [ ] **步骤 3：Commit**

```bash
git add backend/app/utils/sse_manager.py
git commit -m "feat: 添加 SSE 连接管理器"
```

---

## 任务 2：后端 SSE 路由

**文件：**
- 创建：`backend/app/routes/sse.py`
- 修改：`backend/app/main.py`（注册路由）

- [ ] **步骤 1：创建 SSE 路由**

```python
# backend/app/routes/sse.py

import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from ..utils.sse_manager import sse_manager

router = APIRouter()


@router.get("/api/sse/events")
async def sse_events(request: Request):
    """SSE 事件流端点"""

    async def event_generator():
        # 创建连接
        queue = await sse_manager.connect()
        try:
            while True:
                # 检查客户端是否断开
                if await request.is_disconnected():
                    break

                # 获取事件
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                except asyncio.TimeoutError:
                    # 发送心跳
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': ''}, ensure_ascii=False)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            sse_manager.disconnect(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )
```

- [ ] **步骤 2：注册 SSE 路由到 main.py**

在 `backend/app/main.py` 中添加：

```python
# 在路由导入部分添加
from .routes import sse

# 在路由注册部分添加
app.include_router(sse.router, tags=["SSE"])
```

- [ ] **步骤 3：验证路由注册**

运行：`cd backend && python -c "from app.main import app; print([r.path for r in app.routes])"`
预期：输出包含 `/api/sse/events`

- [ ] **步骤 4：Commit**

```bash
git add backend/app/routes/sse.py backend/app/main.py
git commit -m "feat: 添加 SSE 路由"
```

---

## 任务 3：前端 SSE 客户端

**文件：**
- 创建：`frontend/src/api/sse.js`

- [ ] **步骤 1：创建 SSE 客户端类**

```javascript
// frontend/src/api/sse.js

class SSEClient {
  constructor() {
    this.eventSource = null
    this.listeners = {}
    this.reconnectTimer = null
    this.isConnecting = false
  }

  connect() {
    if (this.isConnecting || (this.eventSource && this.eventSource.readyState === EventSource.OPEN)) {
      return
    }

    this.isConnecting = true
    this.eventSource = new EventSource('/api/sse/events')

    this.eventSource.onopen = () => {
      this.isConnecting = false
      console.log('SSE 连接已建立')
    }

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.emit(data.type, data.data)
      } catch (e) {
        console.error('SSE 数据解析失败:', e)
      }
    }

    this.eventSource.onerror = () => {
      this.isConnecting = false
      console.log('SSE 连接断开，3秒后重连...')
      this.eventSource.close()

      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer)
      }

      this.reconnectTimer = setTimeout(() => {
        this.connect()
      }, 3000)
    }
  }

  on(eventType, callback) {
    if (!this.listeners[eventType]) {
      this.listeners[eventType] = []
    }
    this.listeners[eventType].push(callback)
  }

  off(eventType, callback) {
    if (this.listeners[eventType]) {
      this.listeners[eventType] = this.listeners[eventType].filter(cb => cb !== callback)
    }
  }

  emit(eventType, data) {
    if (this.listeners[eventType]) {
      this.listeners[eventType].forEach(callback => callback(data))
    }
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    if (this.eventSource) {
      this.eventSource.close()
      this.eventSource = null
    }

    this.isConnecting = false
  }
}

export const sseClient = new SSEClient()
```

- [ ] **步骤 2：验证文件创建**

运行：`ls -la frontend/src/api/sse.js`
预期：文件存在

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/api/sse.js
git commit -m "feat: 添加 SSE 客户端"
```

---

## 任务 4：大屏状态管理

**文件：**
- 创建：`frontend/src/stores/screen.js`

- [ ] **步骤 1：创建 Pinia Store**

```javascript
// frontend/src/stores/screen.js

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useScreenStore = defineStore('screen', () => {
  // 排行榜数据
  const rankList = ref([])

  // 实时动态
  const dynamics = ref([])

  // 最大动态记录数
  const maxDynamics = 100

  // 获取排行榜数据
  async function fetchRankList(classId) {
    try {
      const res = await api.get('/api/leaderboard/points', {
        params: { class_id: classId }
      })
      rankList.value = res.data
    } catch (e) {
      console.error('获取排行榜失败:', e)
    }
  }

  // 获取今天的积分日志
  async function fetchTodayLogs(classId) {
    try {
      const res = await api.get('/api/students/points-logs', {
        params: {
          class_id: classId,
          page_size: 50
        }
      })
      dynamics.value = res.data.items || []
    } catch (e) {
      console.error('获取积分日志失败:', e)
    }
  }

  // 处理积分变化事件
  function handlePointsChange(data) {
    // 更新排行榜
    const student = rankList.value.find(s => s.id === data.student_id)
    if (student) {
      student.points = (student.points || 0) + data.points
      // 重新排序
      rankList.value.sort((a, b) => b.points - a.points)
    }

    // 添加到动态列表
    dynamics.value.unshift({
      id: Date.now(),
      student_name: data.student_name,
      points: data.points,
      reason: data.reason,
      created_at: data.timestamp || new Date().toISOString()
    })

    // 限制动态数量
    if (dynamics.value.length > maxDynamics) {
      dynamics.value = dynamics.value.slice(0, maxDynamics)
    }
  }

  // 处理学生添加事件
  function handleStudentAdd(data) {
    rankList.value.push({
      id: data.student_id,
      name: data.student_name,
      student_no: data.student_no,
      points: 0
    })
  }

  // 处理学生删除事件
  function handleStudentDelete(data) {
    rankList.value = rankList.value.filter(s => s.id !== data.student_id)
  }

  // 清空数据
  function clear() {
    rankList.value = []
    dynamics.value = []
  }

  return {
    rankList,
    dynamics,
    fetchRankList,
    fetchTodayLogs,
    handlePointsChange,
    handleStudentAdd,
    handleStudentDelete,
    clear
  }
})
```

- [ ] **步骤 2：验证文件创建**

运行：`ls -la frontend/src/stores/screen.js`
预期：文件存在

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/stores/screen.js
git commit -m "feat: 添加大屏状态管理"
```

---

## 任务 5：排行榜卡片组件

**文件：**
- 创建：`frontend/src/components/screen/RankCard.vue`

- [ ] **步骤 1：创建排行榜卡片组件**

```vue
<template>
  <div class="rank-card">
    <div class="card-header">
      <h3>🏆 排行榜</h3>
    </div>
    <div class="card-body">
      <div class="rank-list" ref="rankListRef">
        <div
          v-for="(student, index) in rankList"
          :key="student.id"
          class="rank-item"
          :class="{ 'top3': index < 3 }"
        >
          <span class="rank-num">{{ index + 1 }}</span>
          <span class="rank-name">{{ student.name }}</span>
          <span class="rank-points" :class="{ 'flash': student._flash }">
            {{ student.points }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  rankList: {
    type: Array,
    default: () => []
  }
})

const rankListRef = ref(null)

// 监听积分变化，触发闪烁动画
watch(() => props.rankList, (newList) => {
  newList.forEach(student => {
    if (student._flash) {
      setTimeout(() => {
        student._flash = false
      }, 500)
    }
  })
}, { deep: true })

// 触发闪烁动画
function flashStudent(studentId) {
  const student = props.rankList.find(s => s.id === studentId)
  if (student) {
    student._flash = true
  }
}

defineExpose({ flashStudent })
</script>

<style scoped>
.rank-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #fff;
}

.card-body {
  flex: 1;
  overflow: hidden;
}

.rank-list {
  height: 100%;
  overflow-y: auto;
}

.rank-list::-webkit-scrollbar {
  width: 4px;
}

.rank-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.rank-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  transition: background 0.2s;
}

.rank-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.rank-item.top3 {
  background: rgba(255, 215, 0, 0.1);
  border-left: 3px solid #ffd700;
}

.rank-num {
  width: 30px;
  font-size: 14px;
  font-weight: 600;
  color: #ffd700;
}

.rank-name {
  flex: 1;
  font-size: 14px;
  color: #fff;
}

.rank-points {
  font-size: 16px;
  font-weight: 700;
  color: #10b981;
  transition: all 0.3s;
}

.rank-points.flash {
  animation: flash 0.5s ease-in-out;
}

@keyframes flash {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}
</style>
```

- [ ] **步骤 2：验证文件创建**

运行：`ls -la frontend/src/components/screen/RankCard.vue`
预期：文件存在

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/components/screen/RankCard.vue
git commit -m "feat: 添加排行榜卡片组件"
```

---

## 任务 6：实时动态卡片组件

**文件：**
- 创建：`frontend/src/components/screen/DynamicCard.vue`

- [ ] **步骤 1：创建实时动态卡片组件**

```vue
<template>
  <div class="dynamic-card">
    <div class="card-header">
      <h3>📊 实时动态</h3>
    </div>
    <div class="card-body">
      <div class="dynamic-list" ref="listRef">
        <div
          v-for="item in dynamics"
          :key="item.id"
          class="dynamic-item"
          :class="{ 'points-add': item.points > 0, 'points-sub': item.points < 0 }"
        >
          <span class="dynamic-name">{{ item.student_name }}</span>
          <span class="dynamic-points" :class="{ 'positive': item.points > 0, 'negative': item.points < 0 }">
            {{ item.points > 0 ? '+' : '' }}{{ item.points }}
          </span>
          <span class="dynamic-reason">{{ item.reason }}</span>
          <span class="dynamic-time">{{ formatTime(item.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  dynamics: {
    type: Array,
    default: () => []
  }
})

const listRef = ref(null)

// 格式化时间
function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

// 监听新动态，自动滚动到底部
watch(() => props.dynamics.length, async () => {
  await nextTick()
  if (listRef.value) {
    listRef.value.scrollTop = 0
  }
})
</script>

<style scoped>
.dynamic-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #fff;
}

.card-body {
  flex: 1;
  overflow: hidden;
}

.dynamic-list {
  height: 100%;
  overflow-y: auto;
}

.dynamic-list::-webkit-scrollbar {
  width: 4px;
}

.dynamic-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.dynamic-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  animation: slideIn 0.3s ease-out;
}

.dynamic-item.points-add {
  border-left: 3px solid #10b981;
}

.dynamic-item.points-sub {
  border-left: 3px solid #ef4444;
}

.dynamic-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  min-width: 60px;
}

.dynamic-points {
  font-size: 16px;
  font-weight: 700;
  min-width: 50px;
  text-align: center;
}

.dynamic-points.positive {
  color: #10b981;
}

.dynamic-points.negative {
  color: #ef4444;
}

.dynamic-reason {
  flex: 1;
  font-size: 13px;
  color: #94a3b8;
}

.dynamic-time {
  font-size: 12px;
  color: #64748b;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
```

- [ ] **步骤 2：验证文件创建**

运行：`ls -la frontend/src/components/screen/DynamicCard.vue`
预期：文件存在

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/components/screen/DynamicCard.vue
git commit -m "feat: 添加实时动态卡片组件"
```

---

## 任务 7：计时器卡片组件

**文件：**
- 创建：`frontend/src/components/screen/TimerCard.vue`

- [ ] **步骤 1：创建计时器卡片组件**

```vue
<template>
  <div class="timer-card">
    <div class="card-header">
      <h3>⏱️ 课堂计时</h3>
    </div>
    <div class="card-body">
      <div class="timer-display">
        {{ formatTime(elapsed) }}
      </div>
      <div class="timer-controls">
        <el-button
          v-if="!isRunning"
          type="primary"
          @click="start"
        >
          开始
        </el-button>
        <el-button
          v-else
          type="warning"
          @click="pause"
        >
          暂停
        </el-button>
        <el-button @click="reset">
          重置
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

const elapsed = ref(0)
const isRunning = ref(false)
let timer = null

// 格式化时间
function formatTime(seconds) {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hrs > 0) {
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 开始计时
function start() {
  if (isRunning.value) return

  isRunning.value = true
  timer = setInterval(() => {
    elapsed.value++
  }, 1000)
}

// 暂停计时
function pause() {
  isRunning.value = false
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

// 重置计时
function reset() {
  pause()
  elapsed.value = 0
}

// 组件卸载时清理
onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})

defineExpose({ start, pause, reset })
</script>

<style scoped>
.timer-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #fff;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.timer-display {
  font-size: 48px;
  font-weight: 700;
  color: #fff;
  font-variant-numeric: tabular-nums;
  margin-bottom: 24px;
}

.timer-controls {
  display: flex;
  gap: 12px;
}
</style>
```

- [ ] **步骤 2：验证文件创建**

运行：`ls -la frontend/src/components/screen/TimerCard.vue`
预期：文件存在

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/components/screen/TimerCard.vue
git commit -m "feat: 添加计时器卡片组件"
```

---

## 任务 8：随机点名卡片组件

**文件：**
- 创建：`frontend/src/components/screen/RandomCard.vue`

- [ ] **步骤 1：创建随机点名卡片组件**

```vue
<template>
  <div class="random-card">
    <div class="card-header">
      <h3>🎲 随机点名</h3>
    </div>
    <div class="card-body">
      <div class="random-result">
        <div v-if="result" class="result-name">{{ result.name }}</div>
        <div v-else class="result-placeholder">点击开始</div>
      </div>
      <div class="random-controls">
        <el-button
          type="primary"
          size="large"
          @click="pick"
          :loading="spinning"
          :disabled="students.length > 0 && pickedNames.length >= students.length"
        >
          {{ pickedNames.length >= students.length && students.length > 0 ? '已点完' : '开始抽取' }}
        </el-button>
        <el-button v-if="pickedNames.length" @click="reset">
          重置
        </el-button>
      </div>
      <div v-if="pickedNames.length" class="picked-list">
        <div class="picked-header">已点过 ({{ pickedNames.length }}/{{ students.length }})</div>
        <div class="picked-tags">
          <el-tag
            v-for="name in pickedNames"
            :key="name"
            size="small"
            style="margin: 2px;"
          >
            {{ name }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../../api'
import { useClassStore } from '../../stores/class'

const classStore = useClassStore()
const students = ref([])
const result = ref(null)
const spinning = ref(false)
const pickedNames = ref([])

// 加载学生列表
async function loadStudents() {
  if (!classStore.currentClassId) return
  try {
    const res = await api.get('/api/students/', {
      params: { class_id: classStore.currentClassId }
    })
    students.value = res.data
  } catch (e) {
    console.error('加载学生失败:', e)
  }
}

// 随机抽取
async function pick() {
  if (!students.value.length) {
    await loadStudents()
  }
  if (!students.value.length) return

  const available = students.value.filter(s => !pickedNames.value.includes(s.name))
  if (!available.length) return

  spinning.value = true
  result.value = null

  let count = 0
  const interval = setInterval(() => {
    result.value = available[Math.floor(Math.random() * available.length)]
    count++

    if (count > 15) {
      clearInterval(interval)
      spinning.value = false
      if (result.value) {
        pickedNames.value.push(result.value.name)
      }
    }
  }, 100)
}

// 重置
function reset() {
  pickedNames.value = []
  result.value = null
}

defineExpose({ loadStudents })
</script>

<style scoped>
.random-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #fff;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.random-result {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
}

.result-name {
  font-size: 36px;
  font-weight: 700;
  color: #6366f1;
}

.result-placeholder {
  font-size: 18px;
  color: #94a3b8;
}

.random-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.picked-list {
  width: 100%;
}

.picked-header {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.picked-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
</style>
```

- [ ] **步骤 2：验证文件创建**

运行：`ls -la frontend/src/components/screen/RandomCard.vue`
预期：文件存在

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/components/screen/RandomCard.vue
git commit -m "feat: 添加随机点名卡片组件"
```

---

## 任务 9：大屏展示页面

**文件：**
- 创建：`frontend/src/views/Screen.vue`

- [ ] **步骤 1：安装 vue-grid-layout**

运行：`cd frontend && npm install vue-grid-layout@next`
预期：安装成功

- [ ] **步骤 2：创建大屏展示页面**

```vue
<template>
  <div class="screen-page" :class="{ 'dark-mode': true }">
    <div class="screen-header">
      <h1>📊 班级大屏</h1>
      <div class="header-actions">
        <el-button @click="resetLayout">重置布局</el-button>
        <el-button @click="$router.push('/')">返回首页</el-button>
      </div>
    </div>

    <div class="screen-content">
      <grid-layout
        v-model:layout="layout"
        :col-num="12"
        :row-height="30"
        :is-draggable="true"
        :is-resizable="true"
        :vertical-compact="true"
        :use-css-transforms="true"
      >
        <grid-item
          v-for="item in layout"
          :key="item.i"
          :x="item.x"
          :y="item.y"
          :w="item.w"
          :h="item.h"
          :i="item.i"
          :min-w="3"
          :min-h="4"
        >
          <component
            :is="getComponent(item.i)"
            v-bind="getProps(item.i)"
            :ref="el => setRef(item.i, el)"
          />
        </grid-item>
      </grid-layout>
    </div>

    <!-- 积分变化特效 -->
    <div v-if="effect.show" class="points-effect" :class="effect.type">
      <span class="effect-name">{{ effect.name }}</span>
      <span class="effect-points">{{ effect.points > 0 ? '+' : '' }}{{ effect.points }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, markRaw } from 'vue'
import { GridLayout, GridItem } from 'vue-grid-layout'
import { useScreenStore } from '../stores/screen'
import { useClassStore } from '../stores/class'
import { sseClient } from '../api/sse'
import RankCard from '../components/screen/RankCard.vue'
import DynamicCard from '../components/screen/DynamicCard.vue'
import TimerCard from '../components/screen/TimerCard.vue'
import RandomCard from '../components/screen/RandomCard.vue'

const screenStore = useScreenStore()
const classStore = useClassStore()

// 组件引用
const refs = {}

// 默认布局
const defaultLayout = [
  { i: 'rank', x: 0, y: 0, w: 4, h: 10 },
  { i: 'dynamic', x: 4, y: 0, w: 4, h: 10 },
  { i: 'timer', x: 8, y: 0, w: 4, h: 5 },
  { i: 'random', x: 8, y: 5, w: 4, h: 5 }
]

const layout = ref(JSON.parse(JSON.stringify(defaultLayout)))

// 特效状态
const effect = reactive({
  show: false,
  type: '',
  name: '',
  points: 0
})

// 获取组件
function getComponent(id) {
  const map = {
    rank: markRaw(RankCard),
    dynamic: markRaw(DynamicCard),
    timer: markRaw(TimerCard),
    random: markRaw(RandomCard)
  }
  return map[id]
}

// 获取组件属性
function getProps(id) {
  const map = {
    rank: { rankList: screenStore.rankList },
    dynamic: { dynamics: screenStore.dynamics }
  }
  return map[id] || {}
}

// 设置引用
function setRef(id, el) {
  if (el) {
    refs[id] = el
  }
}

// 重置布局
function resetLayout() {
  layout.value = JSON.parse(JSON.stringify(defaultLayout))
}

// 显示积分变化特效
function showPointsEffect(data) {
  effect.show = true
  effect.type = data.points > 0 ? 'add' : 'sub'
  effect.name = data.student_name
  effect.points = data.points

  // 触发排行榜卡片闪烁
  if (refs.rank) {
    refs.rank.flashStudent(data.student_id)
  }

  setTimeout(() => {
    effect.show = false
  }, 1000)
}

// SSE 事件处理
function handlePointsChange(data) {
  screenStore.handlePointsChange(data)
  showPointsEffect(data)
}

function handleStudentAdd(data) {
  screenStore.handleStudentAdd(data)
}

function handleStudentDelete(data) {
  screenStore.handleStudentDelete(data)
}

// 初始化
onMounted(async () => {
  // 加载数据
  if (classStore.currentClassId) {
    await screenStore.fetchRankList(classStore.currentClassId)
    await screenStore.fetchTodayLogs(classStore.currentClassId)
  }

  // 连接 SSE
  sseClient.connect()
  sseClient.on('points_change', handlePointsChange)
  sseClient.on('student_add', handleStudentAdd)
  sseClient.on('student_delete', handleStudentDelete)

  // 加载随机点名学生
  if (refs.random) {
    refs.random.loadStudents()
  }
})

// 清理
onUnmounted(() => {
  sseClient.off('points_change', handlePointsChange)
  sseClient.off('student_add', handleStudentAdd)
  sseClient.off('student_delete', handleStudentDelete)
  sseClient.disconnect()
  screenStore.clear()
})
</script>

<style scoped>
.screen-page {
  min-height: 100vh;
  background: #0f0f23;
  color: #fff;
  padding: 20px;
}

.screen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.screen-header h1 {
  margin: 0;
  font-size: 24px;
}

.screen-content {
  height: calc(100vh - 100px);
}

/* 积分变化特效 */
.points-effect {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: effectIn 0.5s ease-out;
}

.points-effect.add {
  color: #10b981;
}

.points-effect.sub {
  color: #ef4444;
}

.effect-name {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.effect-points {
  font-size: 48px;
  font-weight: 700;
}

@keyframes effectIn {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.5);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}

/* vue-grid-layout 样式 */
.vue-grid-layout {
  height: 100%;
}

.vue-grid-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  overflow: hidden;
}

.vue-grid-item.vue-resizable-handle {
  background: none;
}

.vue-grid-item.vue-resizable-handle::after {
  content: '';
  position: absolute;
  right: 5px;
  bottom: 5px;
  width: 10px;
  height: 10px;
  border-right: 2px solid rgba(255, 255, 255, 0.3);
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
}
</style>
```

- [ ] **步骤 3：验证文件创建**

运行：`ls -la frontend/src/views/Screen.vue`
预期：文件存在

- [ ] **步骤 4：Commit**

```bash
git add frontend/src/views/Screen.vue
git commit -m "feat: 添加大屏展示页面"
```

---

## 任务 10：添加大屏路由

**文件：**
- 修改：`frontend/src/router/index.js`

- [ ] **步骤 1：添加大屏路由**

在 `frontend/src/router/index.js` 中添加：

```javascript
// 在路由配置中添加
{
  path: '/screen',
  name: 'Screen',
  component: () => import('../views/Screen.vue'),
  meta: { requiresAuth: true }
}
```

- [ ] **步骤 2：验证路由添加**

运行：`cd frontend && npm run dev`
预期：访问 http://localhost:5173/screen 可以看到大屏页面

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/router/index.js
git commit -m "feat: 添加大屏路由"
```

---

## 任务 11：快速加分面板组件

**文件：**
- 创建：`frontend/src/components/QuickPoints.vue`

- [ ] **步骤 1：创建快速加分面板组件**

```vue
<template>
  <div class="quick-points-panel" v-if="visible">
    <div class="panel-header">
      <h3>⚡ 快速加分</h3>
      <el-button text @click="close">
        <el-icon><Close /></el-icon>
      </el-button>
    </div>

    <div class="panel-body">
      <!-- 搜索和排序 -->
      <div class="filter-row">
        <el-input
          v-model="search"
          placeholder="搜索学生..."
          clearable
          size="small"
        />
        <el-select v-model="sortBy" size="small" style="width: 100px;">
          <el-option label="按积分" value="points" />
          <el-option label="按姓名" value="name" />
        </el-select>
      </div>

      <!-- 学生列表 -->
      <div class="student-list">
        <div
          v-for="student in filteredStudents"
          :key="student.id"
          class="student-item"
        >
          <el-checkbox
            v-model="student.selected"
            class="student-checkbox"
          />
          <div class="student-info">
            <div class="student-name">{{ student.name }}</div>
            <div class="student-meta">{{ student.student_no }} · 积分: {{ student.points }}</div>
          </div>
          <div class="student-actions">
            <el-button size="small" type="success" @click="quickPoints(student, 5)">+5</el-button>
            <el-button size="small" type="success" @click="quickPoints(student, 10)">+10</el-button>
            <el-button size="small" type="warning" @click="quickPoints(student, -5)">-5</el-button>
          </div>
        </div>
      </div>

      <!-- 批量操作 -->
      <div class="batch-section">
        <div class="batch-row">
          <el-select v-model="batchReason" placeholder="选择原因" size="small" style="flex: 1;">
            <el-option
              v-for="reason in presetReasons"
              :key="reason"
              :label="reason"
              :value="reason"
            />
          </el-select>
          <el-input
            v-model="customReason"
            placeholder="自定义原因"
            size="small"
            style="width: 120px;"
          />
        </div>
        <div class="batch-row">
          <el-input-number
            v-model="batchPoints"
            :min="-100"
            :max="100"
            size="small"
            style="width: 120px;"
          />
          <el-button
            type="primary"
            size="small"
            @click="batchAddPoints"
            :disabled="!selectedStudents.length"
          >
            批量加分 ({{ selectedStudents.length }})
          </el-button>
          <el-button
            size="small"
            @click="undoLast"
            :disabled="!lastAction"
          >
            撤销
          </el-button>
        </div>
      </div>

      <!-- 最近操作 -->
      <div class="recent-section" v-if="recentActions.length">
        <div class="recent-header">最近操作</div>
        <div
          v-for="(action, index) in recentActions.slice(0, 5)"
          :key="index"
          class="recent-item"
        >
          <span class="recent-name">{{ action.studentName }}</span>
          <span class="recent-points" :class="{ 'positive': action.points > 0, 'negative': action.points < 0 }">
            {{ action.points > 0 ? '+' : '' }}{{ action.points }}
          </span>
          <span class="recent-reason">{{ action.reason }}</span>
          <span class="recent-time">{{ formatTime(action.time) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Close } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { useClassStore } from '../stores/class'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const classStore = useClassStore()
const visible = ref(props.modelValue)
const students = ref([])
const search = ref('')
const sortBy = ref('points')
const batchReason = ref('')
const customReason = ref('')
const batchPoints = ref(5)
const recentActions = ref([])
const lastAction = ref(null)

// 预设原因
const presetReasons = [
  '回答问题',
  '作业优秀',
  '课堂表现好',
  '纪律问题',
  '卫生问题'
]

// 监听 visible 变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadStudents()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 过滤后的学生列表
const filteredStudents = computed(() => {
  let list = [...students.value]

  // 搜索过滤
  if (search.value) {
    const keyword = search.value.toLowerCase()
    list = list.filter(s =>
      s.name.toLowerCase().includes(keyword) ||
      s.student_no.toLowerCase().includes(keyword)
    )
  }

  // 排序
  if (sortBy.value === 'points') {
    list.sort((a, b) => b.points - a.points)
  } else {
    list.sort((a, b) => a.name.localeCompare(b.name))
  }

  return list
})

// 选中的学生
const selectedStudents = computed(() => {
  return students.value.filter(s => s.selected)
})

// 加载学生列表
async function loadStudents() {
  if (!classStore.currentClassId) return
  try {
    const res = await api.get('/api/students/', {
      params: { class_id: classStore.currentClassId }
    })
    students.value = res.data.map(s => ({ ...s, selected: false }))
  } catch (e) {
    console.error('加载学生失败:', e)
  }
}

// 快速加分
async function quickPoints(student, points) {
  const reason = batchReason.value || customReason.value || (points > 0 ? '课堂表现好' : '纪律问题')

  try {
    await api.post('/api/students/points/adjust', {
      student_id: student.id,
      points: points,
      reason: reason
    })

    student.points += points

    recentActions.value.unshift({
      studentId: student.id,
      studentName: student.name,
      points: points,
      reason: reason,
      time: new Date()
    })

    lastAction.value = {
      studentId: student.id,
      points: -points,
      reason: reason
    }

    ElMessage.success(`${student.name} ${points > 0 ? '+' : ''}${points} 分`)
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// 批量加分
async function batchAddPoints() {
  if (!selectedStudents.value.length) return

  const reason = batchReason.value || customReason.value || '批量加分'
  const points = batchPoints.value

  try {
    for (const student of selectedStudents.value) {
      await api.post('/api/students/points/adjust', {
        student_id: student.id,
        points: points,
        reason: reason
      })

      student.points += points
      student.selected = false
    }

    recentActions.value.unshift({
      studentId: 0,
      studentName: `${selectedStudents.value.length} 名学生`,
      points: points,
      reason: reason,
      time: new Date()
    })

    lastAction.value = {
      studentIds: selectedStudents.value.map(s => s.id),
      points: -points,
      reason: reason
    }

    ElMessage.success(`批量操作成功`)
  } catch (e) {
    ElMessage.error('批量操作失败')
  }
}

// 撤销上一步操作
async function undoLast() {
  if (!lastAction.value) return

  try {
    if (lastAction.value.studentIds) {
      // 批量撤销
      for (const studentId of lastAction.value.studentIds) {
        await api.post('/api/students/points/adjust', {
          student_id: studentId,
          points: lastAction.value.points,
          reason: `撤销: ${lastAction.value.reason}`
        })
      }
    } else {
      // 单个撤销
      await api.post('/api/students/points/adjust', {
        student_id: lastAction.value.studentId,
        points: lastAction.value.points,
        reason: `撤销: ${lastAction.value.reason}`
      })
    }

    lastAction.value = null
    await loadStudents()
    ElMessage.success('撤销成功')
  } catch (e) {
    ElMessage.error('撤销失败')
  }
}

// 格式化时间
function formatTime(date) {
  if (!date) return ''
  const d = new Date(date)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

// 关闭面板
function close() {
  visible.value = false
}

onMounted(() => {
  if (visible.value) {
    loadStudents()
  }
})
</script>

<style scoped>
.quick-points-panel {
  position: fixed;
  bottom: 80px;
  right: 20px;
  width: 400px;
  max-height: 600px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e8ecf1;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.filter-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.student-list {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 12px;
}

.student-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.student-item:hover {
  background: #f5f7fa;
}

.student-checkbox {
  flex-shrink: 0;
}

.student-info {
  flex: 1;
  min-width: 0;
}

.student-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.student-meta {
  font-size: 12px;
  color: #94a3b8;
}

.student-actions {
  display: flex;
  gap: 4px;
}

.batch-section {
  border-top: 1px solid #e8ecf1;
  padding-top: 12px;
  margin-bottom: 12px;
}

.batch-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.recent-section {
  border-top: 1px solid #e8ecf1;
  padding-top: 12px;
}

.recent-header {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 13px;
}

.recent-name {
  font-weight: 600;
  color: #1e293b;
  min-width: 60px;
}

.recent-points {
  font-weight: 700;
  min-width: 40px;
  text-align: center;
}

.recent-points.positive {
  color: #10b981;
}

.recent-points.negative {
  color: #ef4444;
}

.recent-reason {
  flex: 1;
  color: #64748b;
}

.recent-time {
  color: #94a3b8;
}

@media (max-width: 767px) {
  .quick-points-panel {
    width: calc(100% - 40px);
    right: 20px;
    left: 20px;
  }
}
</style>
```

- [ ] **步骤 2：验证文件创建**

运行：`ls -la frontend/src/components/QuickPoints.vue`
预期：文件存在

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/components/QuickPoints.vue
git commit -m "feat: 添加快速加分面板组件"
```

---

## 任务 12：Dashboard 添加入口

**文件：**
- 修改：`frontend/src/views/Dashboard.vue`

- [ ] **步骤 1：添加"进入大屏"按钮和悬浮按钮**

在 `frontend/src/views/Dashboard.vue` 的快捷操作区域添加：

```vue
<!-- 在快捷操作按钮区域添加 -->
<el-button @click="$router.push('/screen')" type="warning">
  <el-icon><Monitor /></el-icon> 大屏展示
</el-button>
```

在模板底部添加：

```vue
<!-- 快速加分悬浮按钮 -->
<div class="quick-points-fab" @click="showQuickPoints = true">
  <el-icon size="24"><Plus /></el-icon>
</div>

<!-- 快速加分面板 -->
<QuickPoints v-model="showQuickPoints" />
```

在 script 部分添加：

```javascript
import { ref } from 'vue'
import QuickPoints from '../components/QuickPoints.vue'
import { Monitor, Plus } from '@element-plus/icons-vue'

const showQuickPoints = ref(false)
```

在 style 部分添加：

```css
.quick-points-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
  z-index: 100;
  color: #fff;
}

.quick-points-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.5);
}
```

- [ ] **步骤 2：验证修改**

运行：`cd frontend && npm run dev`
预期：首页右下角有悬浮按钮，点击弹出快速加分面板

- [ ] **步骤 3：Commit**

```bash
git add frontend/src/views/Dashboard.vue
git commit -m "feat: Dashboard 添加大屏入口和快速加分按钮"
```

---

## 任务 13：Docker 部署配置

**文件：**
- 创建：`docker-compose.yml`
- 创建：`nginx.conf`
- 创建：`backend/Dockerfile`
- 创建：`.env`
- 创建：`deploy.sh`

- [ ] **步骤 1：创建 docker-compose.yml**

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: student-points-db
    restart: always
    environment:
      POSTGRES_DB: student_points
      POSTGRES_USER: ztylh
      POSTGRES_PASSWORD: ${DB_PASSWORD}
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

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: student-points-backend
    restart: always
    environment:
      DATABASE_URL: postgresql+asyncpg://ztylh:${DB_PASSWORD}@db:5432/student_points
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

- [ ] **步骤 2：创建 nginx.conf**

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8866;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 30s;
    }

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

- [ ] **步骤 3：创建 backend/Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8866

CMD ["gunicorn", "app.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8866", "--timeout", "30", "--keep-alive", "60"]
```

- [ ] **步骤 4：创建 .env**

```bash
SECRET_KEY=your-secret-key-here
DB_PASSWORD=Zty256310x!
```

- [ ] **步骤 5：创建 deploy.sh**

```bash
#!/bin/bash

set -e

PROJECT_DIR="/root/student-points"

echo "开始部署..."

# 创建目录
mkdir -p $PROJECT_DIR/postgres
mkdir -p $PROJECT_DIR/backups

# 生成 SECRET_KEY
if [ ! -f .env ]; then
  SECRET_KEY=$(openssl rand -hex 32)
  echo "SECRET_KEY=$SECRET_KEY" > .env
  echo "DB_PASSWORD=Zty256310x!" >> .env
  echo "已生成 .env 文件"
fi

# 构建前端
echo "构建前端..."
cd frontend
npm install
npm run build
cd ..

# 复制前端文件
echo "复制前端文件..."
cp -r frontend/dist backend/static

# 构建并启动服务
echo "启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 验证部署
echo "验证部署..."
if curl -s http://localhost:8866/health > /dev/null; then
  echo "✓ 后端服务启动成功"
else
  echo "✗ 后端服务启动失败"
fi

if curl -s http://localhost > /dev/null; then
  echo "✓ 前端服务启动成功"
else
  echo "✗ 前端服务启动失败"
fi

echo ""
echo "部署完成！"
echo "访问地址: http://124.223.107.60"
echo "API 文档: http://124.223.107.60:8866/docs"
echo "管理后台: http://124.223.107.60/admin-panel"
```

- [ ] **步骤 6：验证文件创建**

运行：`ls -la docker-compose.yml nginx.conf backend/Dockerfile .env deploy.sh`
预期：所有文件存在

- [ ] **步骤 7：Commit**

```bash
git add docker-compose.yml nginx.conf backend/Dockerfile .env deploy.sh
git commit -m "feat: 添加 Docker 部署配置"
```

---

## 任务 14：更新 requirements.txt

**文件：**
- 修改：`backend/requirements.txt`

- [ ] **步骤 1：添加 gunicorn 依赖**

在 `backend/requirements.txt` 中添加：

```
gunicorn==21.2.0
```

- [ ] **步骤 2：验证依赖添加**

运行：`cat backend/requirements.txt | grep gunicorn`
预期：输出 `gunicorn==21.2.0`

- [ ] **步骤 3：Commit**

```bash
git add backend/requirements.txt
git commit -m "feat: 添加 gunicorn 依赖"
```

---

## 任务 15：测试 SSE 功能

**文件：**
- 无新增文件，测试现有功能

- [ ] **步骤 1：启动后端服务**

运行：`cd backend && uvicorn app.main:app --reload --port 8866`
预期：服务启动成功

- [ ] **步骤 2：测试 SSE 端点**

运行：`curl -N http://localhost:8866/api/sse/events`
预期：连接成功，保持连接

- [ ] **步骤 3：测试积分变化广播**

在另一个终端运行：
```bash
curl -X POST http://localhost:8866/api/students/points/adjust \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "points": 10, "reason": "测试"}'
```

预期：SSE 连接收到积分变化事件

- [ ] **步骤 4：停止服务**

按 Ctrl+C 停止服务

- [ ] **步骤 5：Commit**

```bash
git add .
git commit -m "test: 验证 SSE 功能"
```

---

## 任务 16：测试大屏页面

**文件：**
- 无新增文件，测试现有功能

- [ ] **步骤 1：启动前端服务**

运行：`cd frontend && npm run dev`
预期：服务启动成功

- [ ] **步骤 2：访问大屏页面**

访问：http://localhost:5173/screen
预期：大屏页面正常显示

- [ ] **步骤 3：测试拖拽功能**

操作：拖拽卡片调整位置和大小
预期：拖拽正常工作

- [ ] **步骤 4：测试积分特效**

操作：在学生管理页面给学生加分
预期：大屏页面显示积分变化特效

- [ ] **步骤 5：停止服务**

按 Ctrl+C 停止服务

- [ ] **步骤 6：Commit**

```bash
git add .
git commit -m "test: 验证大屏页面功能"
```

---

## 任务 17：测试快速加分功能

**文件：**
- 无新增文件，测试现有功能

- [ ] **步骤 1：启动前端服务**

运行：`cd frontend && npm run dev`
预期：服务启动成功

- [ ] **步骤 2：访问首页**

访问：http://localhost:5173/
预期：首页正常显示，右下角有悬浮按钮

- [ ] **步骤 3：测试快速加分面板**

操作：点击悬浮按钮，弹出快速加分面板
预期：面板正常显示

- [ ] **步骤 4：测试快速加分**

操作：点击学生旁边的 +5 按钮
预期：学生积分增加，显示成功提示

- [ ] **步骤 5：测试批量加分**

操作：勾选多个学生，点击批量加分
预期：所有选中的学生积分增加

- [ ] **步骤 6：测试撤销功能**

操作：点击撤销按钮
预期：上一步操作被撤销

- [ ] **步骤 7：停止服务**

按 Ctrl+C 停止服务

- [ ] **步骤 8：Commit**

```bash
git add .
git commit -m "test: 验证快速加分功能"
```

---

## 任务 18：部署到服务器

**文件：**
- 无新增文件，部署到服务器

- [ ] **步骤 1：上传代码到服务器**

运行：
```bash
scp -r . root@124.223.107.60:/root/student-points/
```

预期：代码上传成功

- [ ] **步骤 2：登录服务器**

运行：`ssh root@124.223.107.60`
预期：登录成功

- [ ] **步骤 3：运行部署脚本**

运行：
```bash
cd /root/student-points
chmod +x deploy.sh
./deploy.sh
```

预期：部署成功

- [ ] **步骤 4：验证部署**

访问：http://124.223.107.60
预期：前端页面正常访问

访问：http://124.223.107.60:8866/docs
预期：API 文档正常访问

访问：http://124.223.107.60/admin-panel
预期：管理后台正常访问

- [ ] **步骤 5：Commit**

```bash
git add .
git commit -m "feat: 部署到服务器"
```

---

## 自检清单

### 规格覆盖度
- [x] SSE 实时推送 - 任务 1-3
- [x] 大屏展示页面 - 任务 4-10
- [x] 快速加分功能 - 任务 11-12
- [x] Docker 部署 - 任务 13-14
- [x] 测试验证 - 任务 15-17
- [x] 服务器部署 - 任务 18

### 占位符检查
- [x] 无 TODO 或待定内容
- [x] 所有代码完整
- [x] 所有命令可执行

### 类型一致性
- [x] SSE 事件类型一致
- [x] API 接口一致
- [x] 组件属性一致
