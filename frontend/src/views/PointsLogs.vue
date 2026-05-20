<template>
  <div class="points-logs-page">
    <div class="page-header">
      <h1>📝 积分日志</h1>
      <el-button type="success" @click="exportExcel" style="margin-left:auto;">
        📥 导出 Excel
      </el-button>
    </div>

    <el-card shadow="never" class="filter-card">
      <div class="filter-row">
        <el-input v-model="search" placeholder="搜索学生姓名/原因" clearable style="width:200px;" @clear="fetchLogs" @keyup.enter="fetchLogs">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="categoryFilter" placeholder="类型筛选" clearable style="width:140px;" @change="fetchLogs">
          <el-option label="全部" value="" />
          <el-option label="手动调整" value="manual" />
          <el-option label="奖励" value="bonus" />
          <el-option label="惩罚" value="penalty" />
          <el-option label="抽奖中奖" value="lottery_win" />
          <el-option label="抽奖消耗" value="lottery_cost" />
          <el-option label="积分兑换" value="exchange" />
        </el-select>
        <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD" style="width:260px;" @change="fetchLogs" clearable />
        <span style="font-size:14px;color:#64748b;">共 {{ total }} 条记录</span>
      </div>
    </el-card>

    <!-- 桌面端表格 -->
    <el-table v-if="!isMobile" :data="logs" stripe style="width:100%" v-loading="loading">
      <el-table-column label="序号" width="70" type="index" />
      <el-table-column prop="student_name" label="学生" />
      <el-table-column label="积分变动">
        <template #default="{ row }">
          <el-tag :type="row.points > 0 ? 'success' : 'danger'" size="large">
            {{ row.points > 0 ? '+' : '' }}{{ row.points }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reason" label="原因" />
      <el-table-column prop="category" label="类型">
        <template #default="{ row }">
          <el-tag size="small">{{ categoryLabel(row.category) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="时间">
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
import { ref, onMounted, computed, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import api from '../api'
import { useClassStore } from '../stores/class'

const classStore = useClassStore()

const logs = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const search = ref('')
const categoryFilter = ref('')
const dateRange = ref(null)

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
  if (!t) return '-'
  const d = new Date(t)
  return d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

async function fetchLogs() {
  loading.value = true
  try {
    const params = {
      class_id: classStore.currentClassId,
      page: page.value,
      page_size: pageSize,
    }
    if (search.value) params.search = search.value
    if (categoryFilter.value) params.category = categoryFilter.value
    if (dateRange.value && dateRange.value[0]) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await api.get('/api/students/points-logs', { params })
    logs.value = res.data.items || []
    total.value = res.data.total || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function exportExcel() {
  // 获取全部数据用于导出
  loading.value = true
  try {
    const params = {
      class_id: classStore.currentClassId,
      page: 1,
      page_size: 9999,
    }
    if (search.value) params.search = search.value
    if (categoryFilter.value) params.category = categoryFilter.value
    if (dateRange.value && dateRange.value[0]) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await api.get('/api/students/points-logs', { params })
    const allLogs = res.data.items || []
    const exportData = allLogs.map((l, i) => ({
      '序号': i + 1,
      '学生姓名': l.student_name,
      '积分变动': l.points,
      '原因': l.reason,
      '类型': categoryLabel(l.category),
      '时间': formatTime(l.created_at),
    }))
    const XLSX = await import('xlsx')
    const ws = XLSX.utils.json_to_sheet(exportData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '积分日志')
    XLSX.writeFile(wb, `积分日志_${new Date().toISOString().slice(0, 10)}.xlsx`)
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

onMounted(fetchLogs)
watch(() => classStore.currentClassId, () => { page.value = 1; fetchLogs() })
</script>

<style scoped>
.points-logs-page { width: 100%; }
.page-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.page-header h1 { margin: 0; font-size: 22px; }
.filter-card { margin-bottom: 16px; }
.filter-card :deep(.el-card__body) { padding: 12px 16px; }
.filter-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }

.log-cards { display: flex; flex-direction: column; gap: 10px; }
.log-card {
  background: #fff; border-radius: 12px; padding: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.log-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.log-student { font-weight: 600; font-size: 15px; }
.log-reason { font-size: 13px; color: #64748b; margin-bottom: 6px; }
.log-meta { display: flex; justify-content: space-between; align-items: center; }
.log-time { font-size: 12px; color: #94a3b8; }

.pagination-wrap { display: flex; justify-content: center; margin-top: 16px; }
</style>
