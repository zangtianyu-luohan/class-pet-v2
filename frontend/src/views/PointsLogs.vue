<template>
  <div class="points-logs-page">
    <div class="page-header">
      <h1>📝 积分日志</h1>
    </div>

    <el-card shadow="never" class="filter-card">
      <div class="filter-row">
        <span style="font-size:14px;color:#64748b;">共 {{ total }} 条记录</span>
      </div>
    </el-card>

    <!-- 桌面端表格 -->
    <el-table v-if="!isMobile" :data="logs" stripe style="width:100%" v-loading="loading">
      <el-table-column label="序号" width="70" type="index" />
      <el-table-column prop="student_name" label="学生" width="120" />
      <el-table-column label="积分变动" width="120">
        <template #default="{ row }">
          <el-tag :type="row.points > 0 ? 'success' : 'danger'" size="large">
            {{ row.points > 0 ? '+' : '' }}{{ row.points }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reason" label="原因" min-width="200" />
      <el-table-column prop="category" label="类型" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ categoryLabel(row.category) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="时间" width="180">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <!-- 移动端卡片 -->
    <div v-else class="log-cards" v-loading="loading">
      <div v-for="log in logs" :key="log.id" class="log-card">
        <div class="log-card-header">
          <span class="log-student">{{ log.student_name }}</span>
          <el-tag :type="log.points > 0 ? 'success' : 'danger'" size="large">
            {{ log.points > 0 ? '+' : '' }}{{ log.points }}
          </el-tag>
        </div>
        <div class="log-reason">{{ log.reason }}</div>
        <div class="log-meta">
          <el-tag size="small">{{ categoryLabel(log.category) }}</el-tag>
          <span class="log-time">{{ formatTime(log.created_at) }}</span>
        </div>
      </div>
      <el-empty v-if="!logs.length && !loading" description="暂无积分日志" />
    </div>

    <!-- 分页 -->
    <div class="pagination-wrap" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="fetchLogs"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../api'
import { useClassStore } from '../stores/class'

const classStore = useClassStore()

const logs = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)

const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value < 768)

const categoryMap = {
  manual: '手动调整',
  bonus: '奖励',
  penalty: '惩罚',
  lottery_win: '抽奖中奖',
  lottery_cost: '抽奖消耗',
  exchange: '积分兑换',
}

function categoryLabel(cat) {
  return categoryMap[cat] || cat || '其他'
}

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function fetchLogs() {
  if (!classStore.currentClassId) return
  loading.value = true
  try {
    const res = await api.get('/api/students/points-logs', {
      params: { class_id: classStore.currentClassId, page: page.value, page_size: pageSize }
    })
    logs.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLogs()
  window.addEventListener('resize', () => { windowWidth.value = window.innerWidth })
})
</script>

<style scoped>
.points-logs-page { max-width: 1200px; margin: 0 auto; }
.page-header { margin-bottom: 16px; }
.page-header h1 { font-size: 24px; font-weight: 700; }
.filter-card { margin-bottom: 16px; }
.filter-row { display: flex; align-items: center; gap: 12px; }
.pagination-wrap { display: flex; justify-content: center; margin-top: 20px; }

/* 移动端卡片 */
.log-cards { display: flex; flex-direction: column; gap: 10px; }
.log-card {
  background: #fff;
  border-radius: 10px;
  padding: 14px 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.log-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.log-student { font-size: 16px; font-weight: 600; }
.log-reason { font-size: 14px; color: #475569; margin-bottom: 8px; }
.log-meta { display: flex; align-items: center; gap: 8px; }
.log-time { font-size: 12px; color: #94a3b8; }
</style>
