<template>
  <div class="students-page">
    <div class="page-header">
      <h1>👥 学生管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="showAdd = true" :icon="Plus">添加学生</el-button>
        <el-button @click="showBatch = true" :icon="Document">批量导入</el-button>
        <el-button @click="showBatchPoints = true" :icon="Star" :disabled="!selected.length">批量积分</el-button>
        <el-button type="success" @click="exportStudentsExcel">📥 导出Excel</el-button>
        <el-button @click="undoLast" :loading="undoLoading">↩ 撤销</el-button>
        <el-popconfirm title="确定清零所有学生积分？此操作不可撤销！" @confirm="resetPoints">
          <template #reference>
            <el-button type="danger">🗑 清零积分</el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <div class="filter-row">
      <el-input v-model="search" placeholder="搜索姓名或学号" :prefix-icon="Search" clearable class="search-input" @input="fetchStudents" />
      <el-select v-model="sortBy" class="sort-select" @change="fetchStudents">
        <el-option label="按积分" value="points" />
        <el-option label="按姓名" value="name" />
      </el-select>
    </div>

    <!-- 桌面端表格 -->
    <el-table v-if="!isMobile" :data="students" stripe style="width: 100%" v-loading="loading" @selection-change="onSelect" empty-text="暂无学生数据，点击上方「添加学生」开始">
      <el-table-column type="selection" width="50" />
      <el-table-column label="序号" width="70" type="index" />
      <el-table-column prop="student_no" label="学号" />
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="points" label="积分" sortable>
        <template #default="{ row }">
          <el-tag :type="row.points >= 0 ? 'success' : 'danger'">{{ row.points }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" fixed="right">
        <template #default="{ row }">
          <el-button-group>
            <el-button size="small" type="success" @click="openPoints(row, 5)">+5</el-button>
            <el-button size="small" type="success" @click="openPoints(row, 10)">+10</el-button>
            <el-button size="small" type="warning" @click="openPoints(row, -5)">-5</el-button>
          </el-button-group>
          <el-dropdown v-if="rules.length" trigger="click" @command="cmd => applyRule(row, cmd)" style="margin-left:4px;">
            <el-button size="small">规则</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-for="r in rules" :key="r.id" :command="r.id">
                  {{ r.icon }} {{ r.name }} ({{ r.points > 0 ? '+' : '' }}{{ r.points }})
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button size="small" @click="$router.push(`/students/${row.id}`)">详情</el-button>
          <el-popconfirm title="确定删除该学生？" @confirm="deleteStudent(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 移动端卡片列表 -->
    <div v-else class="student-cards" v-loading="loading">
      <el-checkbox
        v-if="students.length"
        v-model="selectAll"
        :indeterminate="selected.length > 0 && selected.length < students.length"
        class="select-all"
        @change="toggleSelectAll"
      >全选 ({{ selected.length }}/{{ students.length }})</el-checkbox>

      <div v-for="student in students" :key="student.id" class="student-card">
        <div class="card-left">
          <el-checkbox :model-value="selected.includes(student)" @change="toggleSelect(student)" />
          <div class="student-info">
            <div class="student-name">{{ student.name }}</div>
            <div class="student-meta">{{ student.student_no }}</div>
          </div>
        </div>
        <div class="card-right">
          <el-tag :type="student.points >= 0 ? 'success' : 'danger'" size="large">{{ student.points }}分</el-tag>
          <div class="card-actions">
            <el-button size="small" type="success" @click="openPoints(student, 5)">+5</el-button>
            <el-button size="small" type="success" @click="openPoints(student, 10)">+10</el-button>
            <el-button size="small" type="warning" @click="openPoints(student, -5)">-5</el-button>
            <el-button size="small" @click="$router.push(`/students/${student.id}`)">详情</el-button>
            <el-popconfirm title="确定删除？" @confirm="deleteStudent(student.id)">
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加学生弹窗 -->
    <el-dialog v-model="showAdd" title="添加学生">
      <el-form :model="addForm" label-width="60px">
        <el-form-item label="学号"><el-input v-model="addForm.student_no" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="addForm.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" @click="addStudent">确认添加</el-button>
      </template>
    </el-dialog>

    <!-- 积分弹窗 -->
    <el-dialog v-model="showPoints" title="调整积分">
      <p>学生：<strong>{{ pointsTarget?.name }}</strong></p>
      <el-input-number v-model="pointsValue" :min="-100" :max="100" style="margin-top: 12px" />
      <el-input v-model="pointsReason" placeholder="原因" style="margin-top: 12px" />
      <template #footer>
        <el-button @click="showPoints = false">取消</el-button>
        <el-button type="primary" @click="submitPoints">确认</el-button>
      </template>
    </el-dialog>

    <!-- 批量积分弹窗 -->
    <el-dialog v-model="showBatchPoints" title="批量积分">
      <p>已选 <strong>{{ selected.length }}</strong> 名学生</p>
      <el-input-number v-model="batchPointsValue" :min="-100" :max="100" style="margin-top: 12px" />
      <el-input v-model="batchPointsReason" placeholder="原因" style="margin-top: 12px" />
      <template #footer>
        <el-button @click="showBatchPoints = false">取消</el-button>
        <el-button type="primary" @click="submitBatchPoints">确认</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入弹窗 -->
    <el-dialog v-model="showBatch" title="批量导入" width="520px">
      <el-tabs v-model="batchTab">
        <el-tab-pane label="📄 Excel 导入" name="excel">
          <div style="margin-bottom:12px;">
            <input type="file" ref="excelFileInput" accept=".xlsx,.xls,.csv" style="display:none" @change="onExcelFileChange" />
            <el-button type="primary" @click="$refs.excelFileInput.click()">📁 选择 Excel 文件</el-button>
            <span v-if="excelFileName" style="margin-left:8px;font-size:13px;color:#64748b;">{{ excelFileName }}</span>
          </div>
          <div v-if="excelPreview.length" style="margin-top:12px;">
            <div style="font-size:13px;color:#10b981;margin-bottom:8px;">
              ✅ 识别到 {{ excelPreview.length }} 名学生（自动匹配：学号/姓名）
            </div>
            <el-table :data="excelPreview.slice(0, 10)" size="small" stripe max-height="250">
              <el-table-column prop="student_no" label="学号" width="80" />
              <el-table-column prop="name" label="姓名" width="100" />
            </el-table>
            <div v-if="excelPreview.length > 10" style="font-size:12px;color:#64748b;margin-top:4px;">
              ...还有 {{ excelPreview.length - 10 }} 名学生
            </div>
          </div>
          <div v-if="excelErrors.length" style="margin-top:8px;">
            <div v-for="(err, i) in excelErrors" :key="i" style="font-size:12px;color:#f87171;">⚠️ {{ err }}</div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="📝 文本导入" name="text">
          <p style="color: #94a3b8; font-size: 13px">每行一个学生，格式：学号,姓名</p>
          <el-input v-model="batchText" type="textarea" :rows="6" placeholder="01,张三&#10;02,李四" style="margin-top: 8px" />
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="showBatch = false">取消</el-button>
        <el-button type="primary" @click="batchTab === 'excel' ? importExcel() : importBatch()">
          导入 {{ excelPreview.length && batchTab === 'excel' ? `(${excelPreview.length}人)` : '' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Search, Plus, Document, Star } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { useClassStore } from '../stores/class'

const classStore = useClassStore()
const students = ref([])
const loading = ref(false)
const search = ref('')
const sortBy = ref('points')
const selected = ref([])
const selectAll = ref(false)

const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value < 768)
function onResize() { windowWidth.value = window.innerWidth }
onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))

const showAdd = ref(false)
const addForm = ref({ student_no: '', name: '' })

const showPoints = ref(false)
const pointsTarget = ref(null)
const pointsValue = ref(5)
const pointsReason = ref('')

const showBatchPoints = ref(false)
const batchPointsValue = ref(5)
const batchPointsReason = ref('')

const showBatch = ref(false)
const batchText = ref('')
const batchTab = ref('excel')
const excelFileName = ref('')
const excelPreview = ref([])
const excelErrors = ref([])

const rules = ref([])
const undoLoading = ref(false)

function onSelect(rows) {
  selected.value = rows
  selectAll.value = rows.length === students.value.length && students.value.length > 0
}

function toggleSelect(student) {
  const idx = selected.value.indexOf(student)
  if (idx >= 0) {
    selected.value = selected.value.filter(s => s !== student)
  } else {
    selected.value = [...selected.value, student]
  }
  selectAll.value = selected.value.length === students.value.length
}

function toggleSelectAll(val) {
  selected.value = val ? [...students.value] : []
}

async function fetchStudents() {
  if (!classStore.currentClassId) return
  loading.value = true
  try {
    const res = await api.get('/api/students/', {
      params: { class_id: classStore.currentClassId, search: search.value, sort_by: sortBy.value }
    })
    students.value = res.data
  } catch (e) { /* handled */ } finally { loading.value = false }
}

async function addStudent() {
  try {
    await api.post('/api/students/', addForm.value, { params: { class_id: classStore.currentClassId } })
    ElMessage.success('添加成功')
    showAdd.value = false
    addForm.value = { student_no: '', name: '' }
    fetchStudents()
  } catch (e) { /* handled */ }
}

async function deleteStudent(id) {
  try {
    await api.delete(`/api/students/${id}`)
    ElMessage.success('已删除')
    fetchStudents()
  } catch (e) { /* handled */ }
}

function openPoints(student, value) {
  pointsTarget.value = student
  pointsValue.value = value
  pointsReason.value = ''
  showPoints.value = true
}

async function submitPoints() {
  if (!pointsReason.value) { ElMessage.warning('请填写原因'); return }
  try {
    await api.post('/api/students/points/adjust', {
      student_id: pointsTarget.value.id,
      points: pointsValue.value,
      reason: pointsReason.value,
    })
    ElMessage.success('积分已更新')
    showPoints.value = false
    fetchStudents()
  } catch (e) { /* handled */ }
}

async function submitBatchPoints() {
  if (!batchPointsReason.value) { ElMessage.warning('请填写原因'); return }
  if (!selected.value.length) { ElMessage.warning('请先选择学生'); return }
  try {
    await api.post('/api/students/points/batch', {
      student_ids: selected.value.map(s => s.id),
      points: batchPointsValue.value,
      reason: batchPointsReason.value,
    })
    ElMessage.success('批量积分已更新')
    showBatchPoints.value = false
    fetchStudents()
  } catch (e) { /* handled */ }
}

async function importBatch() {
  const lines = batchText.value.trim().split('\n').filter(l => l.trim())
  const studentsList = lines.map(line => {
    const [student_no, name] = line.split(',').map(s => s.trim())
    return { student_no, name }
  }).filter(s => s.student_no && s.name)

  if (!studentsList.length) { ElMessage.warning('没有有效数据'); return }
  try {
    await api.post('/api/students/batch', { students: studentsList }, { params: { class_id: classStore.currentClassId } })
    ElMessage.success('导入完成')
    showBatch.value = false
    batchText.value = ''
    fetchStudents()
  } catch (e) { /* handled */ }
}

// ===== Excel 导入 =====

// 自动识别列名映射
const colAliases = {
  student_no: ['学号', '编号', 'no', 'no.', 'number', '序号', 'id', '学生编号', '学生学号'],
  name: ['姓名', '名字', 'name', '学生姓名', '学生名字', '名称'],
}

function matchColumn(headers, field) {
  const aliases = colAliases[field] || []
  const lowerHeaders = headers.map(h => String(h).toLowerCase().trim())
  for (const alias of aliases) {
    const idx = lowerHeaders.indexOf(alias.toLowerCase())
    if (idx >= 0) return idx
  }
  // 模糊匹配
  for (const alias of aliases) {
    const idx = lowerHeaders.findIndex(h => h.includes(alias.toLowerCase()) || alias.toLowerCase().includes(h))
    if (idx >= 0) return idx
  }
  return -1
}

function onExcelFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  excelFileName.value = file.name
  excelErrors.value = []
  excelPreview.value = []

  const reader = new FileReader()
  reader.onload = async (evt) => {
    try {
      const XLSX = await import('xlsx')
      const data = new Uint8Array(evt.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      const sheetName = workbook.SheetNames[0]
      const sheet = workbook.Sheets[sheetName]
      const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 })

      if (jsonData.length < 2) {
        excelErrors.value = ['文件至少需要2行（标题行+数据行）']
        return
      }

      // 找标题行（第一行或第二行）
      let headerRow = jsonData[0]
      let dataStart = 1

      // 检查第一行是否像标题
      const firstRowStr = headerRow.map(String).join('').toLowerCase()
      if (!firstRowStr.includes('学号') && !firstRowStr.includes('姓名') && !firstRowStr.includes('name') && !firstRowStr.includes('no')) {
        // 第一行不像标题，可能是没有标题的纯数据，按位置匹配
        const noIdx = matchColumn(jsonData[0], 'student_no')
        const nameIdx = matchColumn(jsonData[0], 'name')
        if (noIdx < 0 && nameIdx < 0) {
          // 按默认位置：第1列学号，第2列姓名
          headerRow = ['学号', '姓名']
          dataStart = 0
        } else {
          headerRow = jsonData[0]
          dataStart = 1
        }
      }

      const noIdx = matchColumn(headerRow, 'student_no')
      const nameIdx = matchColumn(headerRow, 'name')

      if (noIdx < 0 && nameIdx < 0) {
        // 按位置兜底
        const students = []
        for (let i = dataStart; i < jsonData.length; i++) {
          const row = jsonData[i]
          if (!row || !row.length) continue
          const student_no = String(row[0] || '').trim()
          const name = String(row[1] || '').trim()
          if (student_no && name) {
            students.push({ student_no, name })
          }
        }
        excelPreview.value = students
        if (!students.length) excelErrors.value = ['未识别到有效学生数据']
        return
      }

      const students = []
      const errors = []
      for (let i = dataStart; i < jsonData.length; i++) {
        const row = jsonData[i]
        if (!row || !row.length || row.every(c => !c && c !== 0)) continue

        const student_no = noIdx >= 0 ? String(row[noIdx] || '').trim() : ''
        const name = nameIdx >= 0 ? String(row[nameIdx] || '').trim() : ''

        if (!student_no && !name) continue
        if (!student_no) { errors.push(`第${i + 1}行：缺少学号`); continue }
        if (!name) { errors.push(`第${i + 1}行：缺少姓名`); continue }
        students.push({ student_no, name })
      }

      excelPreview.value = students
      excelErrors.value = errors
      if (!students.length && !errors.length) {
        excelErrors.value = ['未识别到有效学生数据']
      }
    } catch (err) {
      excelErrors.value = ['文件解析失败：' + err.message]
    }
  }
  reader.readAsArrayBuffer(file)
}

async function importExcel() {
  if (!excelPreview.value.length) { ElMessage.warning('没有可导入的数据'); return }
  try {
    const res = await api.post('/api/students/batch', { students: excelPreview.value }, { params: { class_id: classStore.currentClassId } })
    ElMessage.success(`成功导入 ${res.data.length} 名学生`)
    showBatch.value = false
    excelPreview.value = []
    excelFileName.value = ''
    excelErrors.value = []
    fetchStudents()
  } catch (e) { /* handled */ }
}

// ===== Excel 导出 =====
async function exportStudentsExcel() {
  const XLSX = await import('xlsx')
  const exportData = students.value.map((s, i) => ({
    '序号': i + 1,
    '学号': s.student_no,
    '姓名': s.name,
    '积分': s.points,
  }))
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '学生列表')
  XLSX.writeFile(wb, `学生列表_${new Date().toISOString().slice(0, 10)}.xlsx`)
}

async function fetchRules() {
  try { const res = await api.get('/api/rules/'); rules.value = res.data.filter(r => r.is_active) } catch { /* */ }
}

async function applyRule(student, ruleId) {
  const rule = rules.value.find(r => r.id === ruleId)
  if (!rule) return
  try {
    await api.post('/api/students/points/adjust', {
      student_id: student.id, points: rule.points, reason: rule.name, category: rule.category
    })
    ElMessage.success(`${student.name} ${rule.points > 0 ? '+' : ''}${rule.points}（${rule.name}）`)
    fetchStudents()
  } catch (e) { /* handled */ }
}

async function undoLast() {
  undoLoading.value = true
  try {
    const res = await api.post('/api/students/undo', null, { params: { class_id: classStore.currentClassId } })
    ElMessage.success(res.data.message)
    fetchStudents()
  } catch (e) { /* handled */ } finally { undoLoading.value = false }
}

async function resetPoints() {
  try {
    const res = await api.post('/api/students/points/reset', null, { params: { class_id: classStore.currentClassId } })
    ElMessage.success(res.data.message)
    fetchStudents()
  } catch (e) { /* handled */ }
}

onMounted(() => { fetchStudents(); fetchRules() })
watch(() => classStore.currentClassId, () => { fetchStudents(); fetchRules() })
</script>

<style scoped>
.students-page { width: 100%; }

.page-header h1 { margin: 0; font-size: 22px; }

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 筛选栏 */
.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.search-input {
  max-width: 320px;
}

.sort-select {
  width: 120px;
}

/* 移动端卡片 */
.student-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.select-all {
  padding: 8px 0;
  font-size: 14px;
  color: #64748b;
}

.student-card {
  background: #fff;
  border-radius: 12px;
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  gap: 12px;
}

.card-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.student-info {
  min-width: 0;
}

.student-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.student-meta {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

.card-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.card-actions {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

/* 响应式 */
@media (max-width: 767px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .el-button {
    flex: 1;
  }

  .filter-row {
    flex-direction: column;
  }

  .search-input {
    max-width: 100%;
  }

  .sort-select {
    width: 100%;
  }
}
</style>
