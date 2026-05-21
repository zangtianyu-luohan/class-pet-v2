<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>📊 班级总览</h1>
      <span class="subtitle">{{ classStore.currentClass?.name || '请先创建班级' }}</span>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #eef2ff; color: #6366f1">👥</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_students }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #fef3c7; color: #f59e0b">⭐</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_points }}</div>
            <div class="stat-label">班级总积分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #d1fae5; color: #10b981">📈</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avg_points }}</div>
            <div class="stat-label">人均积分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #fce7f3; color: #ec4899">📝</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.today_records }}</div>
            <div class="stat-label">今日记录</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card shadow="never" class="quick-actions">
      <template #header>
        <span>⚡ 快捷操作</span>
      </template>
      <div class="action-buttons">
        <el-button @click="$router.push('/students')">
          <el-icon><Plus /></el-icon> 添加学生
        </el-button>
        <el-button @click="$router.push('/tools')">
          <el-icon><MagicStick /></el-icon> 课堂工具
        </el-button>
        <el-button @click="$router.push('/leaderboard')">
          <el-icon><Trophy /></el-icon> 查看排行
        </el-button>
        <el-button @click="$router.push('/badges')">
          <el-icon><Medal /></el-icon> 颁发勋章
        </el-button>
        <el-button @click="$router.push('/screen')" type="warning">
          <el-icon><Monitor /></el-icon> 大屏展示
        </el-button>
      </div>
    </el-card>

    <!-- 空状态 -->
    <el-empty v-if="stats.total_students === 0" description="还没有学生">
      <el-button type="primary" @click="$router.push('/students')">去添加学生</el-button>
    </el-empty>

    <!-- 近7天积分趋势 -->
    <el-card v-if="stats.total_students > 0" shadow="never" class="trend-card">
      <template #header><span>📈 近7天积分趋势</span></template>
      <div class="trend-chart">
        <div v-for="day in trend" :key="day.date" class="trend-bar-wrap">
          <div class="trend-bar" :style="{ height: barHeight(day.count) + '%' }">
            <span class="trend-count" v-if="day.count > 0">{{ day.count }}</span>
          </div>
          <div class="trend-label">{{ day.date }}</div>
        </div>
      </div>
    </el-card>

    <!-- 快速加分悬浮按钮 -->
    <div class="quick-points-fab" @click="showQuickPoints = true">
      <el-icon size="24"><Plus /></el-icon>
    </div>

    <!-- 快速加分面板 -->
    <QuickPoints v-model="showQuickPoints" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api'
import { useClassStore } from '../stores/class'
import QuickPoints from '../components/QuickPoints.vue'
import { Monitor, Plus } from '@element-plus/icons-vue'

const showQuickPoints = ref(false)

const classStore = useClassStore()
const stats = ref({ total_students: 0, total_points: 0, avg_points: 0, today_records: 0 })
const trend = ref([])

async function fetchStats() {
  if (!classStore.currentClassId) return
  try {
    const res = await api.get(`/api/classes/${classStore.currentClassId}/stats`)
    stats.value = res.data
  } catch (e) { /* handled */ }
}

async function fetchTrend() {
  if (!classStore.currentClassId) return
  try {
    // 从积分日志中统计近7天
    const res = await api.get('/api/students/points-logs', {
      params: { class_id: classStore.currentClassId, page_size: 500 }
    })
    const logs = res.data.items || []
    const now = new Date()
    const days = []
    for (let i = 6; i >= 0; i--) {
      const d = new Date(now)
      d.setDate(d.getDate() - i)
      const label = `${d.getMonth() + 1}/${d.getDate()}`
      const dateStr = d.toISOString().slice(0, 10)
      const count = logs.filter(l => l.created_at && l.created_at.slice(0, 10) === dateStr).length
      days.push({ date: label, count })
    }
    trend.value = days
  } catch { trend.value = [] }
}

const maxTrend = computed(() => Math.max(1, ...trend.value.map(d => d.count)))
function barHeight(count) { return Math.max(4, (count / maxTrend.value) * 100) }

onMounted(() => { fetchStats(); fetchTrend() })
watch(() => classStore.currentClassId, () => { fetchStats(); fetchTrend() })
</script>

<style scoped>
.dashboard { width: 100%; }

.page-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  flex-wrap: wrap;
}
.page-header h1 { margin: 0; font-size: 22px; }
.subtitle { color: #94a3b8; font-size: 14px; }

.stats-row {
  margin-bottom: 20px;
}

.stats-row .el-col {
  margin-bottom: 12px;
}

.stat-card {
  border-radius: 16px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 2px;
}

.quick-actions {
  border-radius: 16px;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.action-buttons .el-button {
  flex: 1;
  min-width: 120px;
}

/* 趋势图 */
.trend-card { border-radius: 16px; margin-bottom: 20px; }
.trend-chart { display: flex; align-items: flex-end; justify-content: space-around; height: 160px; gap: 8px; padding: 0 8px; }
.trend-bar-wrap { display: flex; flex-direction: column; align-items: center; flex: 1; height: 100%; justify-content: flex-end; }
.trend-bar { width: 100%; max-width: 48px; background: linear-gradient(180deg, #6366f1, #818cf8); border-radius: 6px 6px 0 0; transition: height 0.3s; position: relative; min-height: 4px; }
.trend-count { position: absolute; top: -20px; left: 50%; transform: translateX(-50%); font-size: 12px; font-weight: 600; color: #6366f1; white-space: nowrap; }
.trend-label { font-size: 12px; color: #94a3b8; margin-top: 6px; }

/* 手机端 */
@media (max-width: 767px) {
  .stat-card :deep(.el-card__body) {
    padding: 14px;
    gap: 10px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 18px;
    border-radius: 10px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 12px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-buttons .el-button {
    width: 100%;
  }
}

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
</style>
