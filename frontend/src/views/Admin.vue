<template>
  <div class="admin-page">
    <!-- 顶部状态栏 -->
    <div class="admin-topbar">
      <div class="topbar-left">
        <span class="topbar-icon">🛡️</span>
        <h1>管理后台</h1>
        <el-tag type="success" size="small" effect="dark">v{{ stats.system?.app_version || '2.0.0' }}</el-tag>
      </div>
      <div class="topbar-right">
        <span class="topbar-time">{{ currentTime }}</span>
        <el-button size="small" @click="refreshAll" :loading="refreshing" text style="color: #94a3b8">
          🔄 刷新
        </el-button>
      </div>
    </div>

    <!-- 核心指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card" v-for="m in metrics" :key="m.label">
        <div class="metric-icon" :style="{ background: m.bg }">{{ m.icon }}</div>
        <div class="metric-body">
          <div class="metric-value">{{ m.value }}</div>
          <div class="metric-label">{{ m.label }}</div>
        </div>
        <div class="metric-trend" v-if="m.trend" :class="m.trend > 0 ? 'up' : 'down'">
          {{ m.trend > 0 ? '↑' : '↓' }} {{ Math.abs(m.trend) }}
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <!-- 7日趋势 -->
      <div class="chart-panel">
        <div class="panel-header">
          <span>📈 近7日积分趋势</span>
          <span class="panel-sub">总计 {{ weekTotal }} 条记录</span>
        </div>
        <div class="trend-chart">
          <div class="chart-bars">
            <div v-for="(item, i) in stats.daily_stats" :key="i" class="chart-col">
              <div class="col-value">{{ item.count }}</div>
              <div class="col-bar-wrap">
                <div class="col-bar" :style="{ height: barPercent(item.count) + '%' }"></div>
              </div>
              <div class="col-label">{{ item.date }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 系统信息 -->
      <div class="info-panel">
        <div class="panel-header">
          <span>🖥️ 系统信息</span>
        </div>
        <div class="info-list">
          <div class="info-row"><span>应用版本</span><span>{{ stats.system?.app_version }}</span></div>
          <div class="info-row"><span>Python</span><span>{{ stats.system?.python_version }}</span></div>
          <div class="info-row"><span>平台</span><span class="mono">{{ stats.system?.platform }}</span></div>
          <div class="info-row"><span>数据库</span><span>PostgreSQL</span></div>
          <div class="info-row"><span>部署平台</span><span>Railway</span></div>
        </div>

        <!-- 快捷操作 -->
        <div class="panel-header" style="margin-top: 12px">
          <span>⚡ 快捷操作</span>
        </div>
        <div class="quick-actions">
          <el-button size="small" @click="downloadBackup" :loading="backingUp">💾 备份数据</el-button>
          <el-button size="small" @click="$router.push('/students')">👥 学生管理</el-button>
          <el-button size="small" @click="$router.push('/classes')">🏫 班级管理</el-button>
        </div>
      </div>
    </div>

    <!-- 最近登录 + 操作日志 -->
    <div class="logs-row">
      <div class="log-panel">
        <div class="panel-header">
          <span>🔐 最近登录</span>
          <el-button size="small" text @click="activeTab = 'loginLogs'">查看全部 →</el-button>
        </div>
        <div class="log-table">
          <div class="log-thead">
            <span>状态</span><span>用户</span><span>IP</span><span>时间</span>
          </div>
          <div v-for="log in (stats.recent_logins || []).slice(0, 8)" :key="log.created_at" class="log-trow" :class="{ fail: !log.success }">
            <span>{{ log.success ? '✅' : '❌' }}</span>
            <span class="bold">{{ log.username }}</span>
            <span class="mono">{{ log.ip_address || '-' }}</span>
            <span class="dim">{{ formatTime(log.created_at) }}</span>
          </div>
          <div v-if="!stats.recent_logins?.length" class="log-empty">暂无记录</div>
        </div>
      </div>
    </div>

    <!-- 功能管理 Tabs -->
    <div class="admin-tabs">
      <div class="tab-nav">
        <button v-for="tab in tabs" :key="tab.key" :class="{ active: activeTab === tab.key }" @click="activeTab = tab.key">
          {{ tab.icon }} {{ tab.label }}
        </button>
      </div>

      <!-- 用户管理 -->
      <div class="tab-content" v-show="activeTab === 'users'">
        <div class="content-header">
          <el-button type="primary" size="small" @click="showCreateUser = true" :icon="Plus">创建用户</el-button>
        </div>
        <el-table :data="users" stripe v-loading="loadingUsers" size="small">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="display_name" label="显示名称" />
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button size="small" @click="openResetPwd(row)">重置密码</el-button>
              <el-popconfirm title="确定删除？" @confirm="deleteUser(row.id)">
                <template #reference><el-button size="small" type="danger">删除</el-button></template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 登录日志 -->
      <div class="tab-content" v-show="activeTab === 'loginLogs'">
        <div class="content-header">
          <el-radio-group v-model="logFilter" size="small" @change="fetchLoginLogs">
            <el-radio-button value="all">全部</el-radio-button>
            <el-radio-button value="success">成功</el-radio-button>
            <el-radio-button value="fail">失败</el-radio-button>
          </el-radio-group>
        </div>
        <el-table :data="loginLogs" stripe v-loading="loadingLogs" size="small">
          <el-table-column prop="username" label="用户" width="100" />
          <el-table-column label="状态" width="70">
            <template #default="{ row }">
              <el-tag :type="row.success ? 'success' : 'danger'" size="small">{{ row.success ? '成功' : '失败' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="ip_address" label="IP" width="130" />
          <el-table-column prop="fail_reason" label="失败原因" />
          <el-table-column prop="created_at" label="时间" width="150">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 积分日志 -->
      <div class="tab-content" v-show="activeTab === 'pointsLogs'">
        <el-table :data="pointsLogs" stripe v-loading="loadingPoints" size="small">
          <el-table-column prop="student_id" label="学生ID" width="80" />
          <el-table-column prop="points" label="积分" width="80">
            <template #default="{ row }">
              <el-tag :type="row.points > 0 ? 'success' : 'danger'" size="small">{{ row.points > 0 ? '+' : '' }}{{ row.points }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="原因" />
          <el-table-column prop="category" label="类型" width="80" />
          <el-table-column prop="created_at" label="时间" width="150">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 数据备份 -->
      <div class="tab-content backup-tab" v-show="activeTab === 'backup'">
        <div class="backup-card">
          <div class="backup-icon">📦</div>
          <h3>数据备份</h3>
          <p>导出所有数据为 JSON 文件（用户、班级、学生、积分记录、勋章）</p>
          <el-button type="primary" :icon="Download" @click="downloadBackup" :loading="backingUp">下载备份文件</el-button>
        </div>
      </div>
    </div>

    <!-- 创建用户弹窗 -->
    <el-dialog v-model="showCreateUser" title="创建用户">
      <el-form :model="newUser" label-width="80px">
        <el-form-item label="用户名"><el-input v-model="newUser.username" /></el-form-item>
        <el-form-item label="密码"><el-input v-model="newUser.password" type="password" show-password /></el-form-item>
        <el-form-item label="显示名称"><el-input v-model="newUser.display_name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateUser = false">取消</el-button>
        <el-button type="primary" @click="createUser">创建</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码弹窗 -->
    <el-dialog v-model="showResetPwd" title="重置密码">
      <p>用户：<strong>{{ resetTarget?.username }}</strong></p>
      <el-input v-model="newPassword" type="password" show-password placeholder="新密码（至少8位）" style="margin-top: 12px" />
      <template #footer>
        <el-button @click="showResetPwd = false">取消</el-button>
        <el-button type="primary" @click="resetPassword">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { Plus, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '../api'

const refreshing = ref(false)
const stats = ref({ overview: {}, daily_stats: [], recent_logins: [], system: {} })
const users = ref([])
const loginLogs = ref([])
const pointsLogs = ref([])

const loadingUsers = ref(false)
const loadingLogs = ref(false)
const loadingPoints = ref(false)
const backingUp = ref(false)

const logFilter = ref('all')
const activeTab = ref('users')

const showCreateUser = ref(false)
const newUser = reactive({ username: '', password: '', display_name: '' })

const showResetPwd = ref(false)
const resetTarget = ref(null)
const newPassword = ref('')

const currentTime = ref(dayjs().format('YYYY-MM-DD HH:mm:ss'))
let timeTimer = null

const tabs = [
  { key: 'users', icon: '👥', label: '用户管理' },
  { key: 'loginLogs', icon: '📋', label: '登录日志' },
  { key: 'pointsLogs', icon: '📊', label: '积分日志' },
  { key: 'backup', icon: '💾', label: '数据备份' },
]

function formatTime(d) { return d ? dayjs(d).format('MM-DD HH:mm') : '-' }

const metrics = computed(() => {
  const o = stats.value.overview || {}
  return [
    { icon: '👤', label: '用户数', value: o.user_count || 0, bg: 'linear-gradient(135deg, #667eea, #764ba2)' },
    { icon: '🏫', label: '班级数', value: o.class_count || 0, bg: 'linear-gradient(135deg, #f093fb, #f5576c)' },
    { icon: '👥', label: '学生数', value: o.student_count || 0, bg: 'linear-gradient(135deg, #4facfe, #00f2fe)' },
    { icon: '⭐', label: '总积分', value: o.total_points || 0, bg: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
    { icon: '📝', label: '积分记录', value: o.total_records || 0, bg: 'linear-gradient(135deg, #fa709a, #fee140)' },
    { icon: '🏆', label: '勋章数', value: o.badge_count || 0, bg: 'linear-gradient(135deg, #a18cd1, #fbc2eb)' },
    { icon: '📈', label: '今日记录', value: o.today_records || 0, bg: 'linear-gradient(135deg, #fccb90, #d57eeb)' },
    { icon: '🔥', label: '本周记录', value: o.week_records || 0, bg: 'linear-gradient(135deg, #e0c3fc, #8ec5fc)' },
  ]
})

const weekTotal = computed(() => {
  return (stats.value.daily_stats || []).reduce((s, d) => s + d.count, 0)
})

function barPercent(count) {
  const max = Math.max(...(stats.value.daily_stats || []).map(d => d.count), 1)
  return Math.max((count / max) * 100, 3)
}

async function fetchStats() {
  try { const res = await api.get('/api/admin/stats'); stats.value = res.data } catch (e) {}
}

async function fetchUsers() {
  loadingUsers.value = true
  try { const res = await api.get('/api/admin/users'); users.value = res.data } catch (e) {}
  finally { loadingUsers.value = false }
}

async function fetchLoginLogs() {
  loadingLogs.value = true
  try {
    const params = { limit: 100 }
    if (logFilter.value === 'success') params.success_only = true
    const res = await api.get('/api/admin/login-logs', { params })
    loginLogs.value = logFilter.value === 'fail' ? res.data.filter(l => !l.success) : res.data
  } catch (e) {}
  finally { loadingLogs.value = false }
}

async function fetchPointsLogs() {
  loadingPoints.value = true
  try { const res = await api.get('/api/admin/points-logs'); pointsLogs.value = res.data } catch (e) {}
  finally { loadingPoints.value = false }
}

async function refreshAll() {
  refreshing.value = true
  await Promise.all([fetchStats(), fetchUsers(), fetchLoginLogs(), fetchPointsLogs()])
  refreshing.value = false
}

async function createUser() {
  try {
    await api.post('/api/admin/users', newUser)
    ElMessage.success('创建成功')
    showCreateUser.value = false
    Object.assign(newUser, { username: '', password: '', display_name: '' })
    fetchUsers()
  } catch (e) {}
}

async function deleteUser(id) {
  try { await api.delete(`/api/admin/users/${id}`); ElMessage.success('已删除'); fetchUsers() } catch (e) {}
}

function openResetPwd(user) { resetTarget.value = user; newPassword.value = ''; showResetPwd.value = true }

async function resetPassword() {
  try {
    await api.post(`/api/admin/users/${resetTarget.value.id}/reset-password`, { new_password: newPassword.value })
    ElMessage.success('密码已重置'); showResetPwd.value = false
  } catch (e) {}
}

async function downloadBackup() {
  backingUp.value = true
  try {
    const res = await api.post('/api/admin/backup', {}, { responseType: 'blob' })
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `sps_backup_${dayjs().format('YYYYMMDD_HHmmss')}.json`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('备份下载成功')
  } catch (e) {}
  finally { backingUp.value = false }
}

onMounted(() => {
  refreshAll()
  timeTimer = setInterval(() => { currentTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss') }, 1000)
})

onUnmounted(() => { clearInterval(timeTimer) })
</script>

<style scoped>
.admin-page {
  max-width: 1200px;
  background: #0f172a;
  min-height: calc(100vh - 48px);
  margin: -24px;
  padding: 24px;
  color: #e2e8f0;
}

/* 顶部栏 */
.admin-topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}
.topbar-left { display: flex; align-items: center; gap: 12px; }
.topbar-icon { font-size: 28px; }
.topbar-left h1 { font-size: 20px; margin: 0; color: #f1f5f9; }
.topbar-right { display: flex; align-items: center; gap: 16px; }
.topbar-time { font-family: 'Courier New', monospace; color: #64748b; font-size: 14px; }

/* 指标卡片 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.metric-card {
  background: #1e293b;
  border-radius: 14px;
  padding: 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  border: 1px solid #334155;
  transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,0,0,0.3); }
.metric-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}
.metric-body { flex: 1; }
.metric-value { font-size: 26px; font-weight: 800; color: #f8fafc; font-variant-numeric: tabular-nums; }
.metric-label { font-size: 12px; color: #94a3b8; margin-top: 2px; }

/* 图表区域 */
.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.chart-panel, .info-panel, .log-panel {
  background: #1e293b;
  border-radius: 14px;
  padding: 20px;
  border: 1px solid #334155;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 15px;
  font-weight: 600;
  color: #f1f5f9;
}
.panel-sub { font-size: 12px; color: #64748b; font-weight: 400; }

/* 柱状图 */
.trend-chart { padding: 8px 0; }
.chart-bars { display: flex; align-items: flex-end; gap: 8px; height: 180px; }
.chart-col { flex: 1; display: flex; flex-direction: column; align-items: center; height: 100%; }
.col-value { font-size: 13px; font-weight: 700; color: #a5b4fc; margin-bottom: 6px; }
.col-bar-wrap { flex: 1; width: 100%; max-width: 48px; display: flex; align-items: flex-end; }
.col-bar {
  width: 100%;
  background: linear-gradient(180deg, #818cf8, #6366f1);
  border-radius: 6px 6px 0 0;
  min-height: 4px;
  transition: height 0.5s ease;
}
.col-label { font-size: 12px; color: #64748b; margin-top: 8px; }

/* 系统信息 */
.info-list { display: flex; flex-direction: column; gap: 0; }
.info-row {
  display: flex; justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #334155;
  font-size: 13px;
}
.info-row:last-child { border-bottom: none; }
.info-row span:first-child { color: #94a3b8; }
.info-row span:last-child { color: #e2e8f0; font-weight: 500; }
.mono { font-family: 'Courier New', monospace; font-size: 12px; }

.quick-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }

/* 登录日志表格 */
.log-table { font-size: 13px; }
.log-thead, .log-trow {
  display: grid;
  grid-template-columns: 50px 80px 1fr 100px;
  gap: 8px;
  padding: 8px 0;
  align-items: center;
}
.log-thead { color: #64748b; font-size: 12px; border-bottom: 1px solid #334155; }
.log-trow { border-bottom: 1px solid #1e293b; }
.log-trow.fail { background: rgba(239, 68, 68, 0.08); border-radius: 6px; }
.bold { font-weight: 600; color: #f1f5f9; }
.dim { color: #64748b; font-size: 12px; }
.log-empty { text-align: center; padding: 20px; color: #64748b; }

/* Tabs */
.admin-tabs {
  background: #1e293b;
  border-radius: 14px;
  border: 1px solid #334155;
  overflow: hidden;
}

.tab-nav {
  display: flex;
  border-bottom: 1px solid #334155;
  overflow-x: auto;
}
.tab-nav button {
  flex: 1;
  padding: 14px 20px;
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}
.tab-nav button:hover { color: #e2e8f0; background: rgba(255,255,255,0.03); }
.tab-nav button.active {
  color: #818cf8;
  border-bottom-color: #818cf8;
  background: rgba(129, 140, 248, 0.05);
}

.tab-content {
  padding: 20px;
}

.content-header {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
  align-items: center;
}

/* Element Plus 暗色覆盖 */
.admin-tabs :deep(.el-table) {
  background: transparent;
  color: #e2e8f0;
}
.admin-tabs :deep(.el-table th.el-table__cell) {
  background: #0f172a !important;
  color: #94a3b8;
  border-bottom-color: #334155;
}
.admin-tabs :deep(.el-table td.el-table__cell) {
  border-bottom-color: #334155;
}
.admin-tabs :deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background: rgba(255,255,255,0.02);
}
.admin-tabs :deep(.el-table__body tr:hover > td) {
  background: rgba(255,255,255,0.04) !important;
}

/* 备份 */
.backup-tab { display: flex; justify-content: center; align-items: center; min-height: 200px; }
.backup-card { text-align: center; }
.backup-icon { font-size: 48px; margin-bottom: 12px; }
.backup-card h3 { margin: 0 0 8px; color: #f1f5f9; }
.backup-card p { color: #94a3b8; margin-bottom: 20px; font-size: 14px; }

/* 响应式 */
@media (max-width: 767px) {
  .admin-page { padding: 16px; }
  .metrics-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .metric-card { padding: 12px; gap: 10px; }
  .metric-icon { width: 38px; height: 38px; font-size: 18px; }
  .metric-value { font-size: 20px; }
  .charts-row { grid-template-columns: 1fr; }
  .chart-bars { height: 140px; }
  .log-thead, .log-trow { grid-template-columns: 40px 60px 1fr 80px; font-size: 12px; }
  .tab-nav button { padding: 10px 12px; font-size: 13px; }
}
</style>
