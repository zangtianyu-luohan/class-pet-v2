<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>📊 班级总览</h1>
      <span class="subtitle">{{ classStore.currentClass?.name || '请先创建班级' }}</span>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #eef2ff; color: #6366f1">👥</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_students }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #fef3c7; color: #f59e0b">⭐</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_points }}</div>
            <div class="stat-label">班级总积分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: #d1fae5; color: #10b981">📈</div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avg_points }}</div>
            <div class="stat-label">人均积分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
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
      <el-space wrap>
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
      </el-space>
    </el-card>

    <!-- 空状态 -->
    <el-empty v-if="stats.total_students === 0" description="还没有学生">
      <el-button type="primary" @click="$router.push('/students')">去添加学生</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api'
import { useClassStore } from '../stores/class'

const classStore = useClassStore()
const stats = ref({ total_students: 0, total_points: 0, avg_points: 0, today_records: 0 })

async function fetchStats() {
  if (!classStore.currentClassId) return
  try {
    const res = await api.get('/api/leaderboard/stats', { params: { class_id: classStore.currentClassId } })
    stats.value = res.data
  } catch (e) { /* ignore */ }
}

onMounted(fetchStats)
watch(() => classStore.currentClassId, fetchStats)
</script>

<style scoped>
.dashboard { max-width: 1200px; }
.page-header { margin-bottom: 24px; }
.page-header h1 { margin: 0; font-size: 22px; color: #1e293b; }
.subtitle { color: #94a3b8; font-size: 14px; }
.stats-row { margin-bottom: 24px; }
.stat-card { border-radius: 16px; }
.stat-card :deep(.el-card__body) { display: flex; align-items: center; gap: 16px; padding: 20px; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; flex-shrink: 0; }
.stat-value { font-size: 24px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 13px; color: #94a3b8; }
.quick-actions { border-radius: 16px; margin-bottom: 24px; }
</style>
