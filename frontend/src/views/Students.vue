<template>
  <div class="students-page">
    <div class="page-header">
      <h1>👥 学生管理</h1>
      <el-space>
        <el-button type="primary" @click="showAdd = true"><el-icon><Plus /></el-icon> 添加学生</el-button>
        <el-button @click="showBatch = true"><el-icon><Document /></el-icon> 批量导入</el-button>
        <el-button @click="showBatchPoints = true"><el-icon><Star /></el-icon> 批量积分</el-button>
      </el-space>
    </div>

    <el-card shadow="never" class="filter-card">
      <el-space>
        <el-input v-model="search" placeholder="搜索姓名或学号" :prefix-icon="Search" clearable style="width: 240px" @input="fetchStudents" />
        <el-select v-model="sortBy" style="width: 120px" @change="fetchStudents">
          <el-option label="按积分" value="points" />
          <el-option label="按姓名" value="name" />
          <el-option label="按等级" value="level" />
        </el-select>
      </el-space>
    </el-card>

    <el-table :data="students" stripe style="width: 100%" v-loading="loading" @selection-change="onSelect">
      <el-table-column type="selection" width="50" />
      <el-table-column label="序号" width="70" type="index" />
      <el-table-column prop="student_no" label="学号" width="100" />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column label="萌宠" width="80">
        <template #default="{ row }">{{ petEmoji(row.pet_type) }}</template>
      </el-table-column>
      <el-table-column prop="level" label="等级" width="80">
        <template #default="{ row }">Lv.{{ row.level }}</template>
      </el-table-column>
      <el-table-column prop="points" label="积分" width="100" sortable>
        <template #default="{ row }">
          <el-tag :type="row.points >= 0 ? 'success' : 'danger'">{{ row.points }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="260" fixed="right">
        <template #default="{ row }">
          <el-button-group>
            <el-button size="small" type="success" @click="openPoints(row, 5)">+5</el-button>
            <el-button size="small" type="success" @click="openPoints(row, 10)">+10</el-button>
            <el-button size="small" type="warning" @click="openPoints(row, -5)">-5</el-button>
          </el-button-group>
          <el-button size="small" @click="$router.push(`/students/${row.id}`)">详情</el-button>
          <el-popconfirm title="确定删除该学生？" @confirm="deleteStudent(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && students.length === 0" description="暂无学生" />

    <!-- 添加学生弹窗 -->
    <el-dialog v-model="showAdd" title="添加学生" width="420px">
      <el-form :model="addForm" label-width="60px">
        <el-form-item label="学号"><el-input v-model="addForm.student_no" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="addForm.name" /></el-form-item>
        <el-form-item label="萌宠">
          <el-select v-model="addForm.pet_type">
            <el-option label="🐱 猫咪" value="cat" />
            <el-option label="🐶 小狗" value="dog" />
            <el-option label="🐰 兔子" value="rabbit" />
            <el-option label="🐼 熊猫" value="panda" />
            <el-option label="🐧 企鹅" value="penguin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" @click="addStudent">确认添加</el-button>
      </template>
    </el-dialog>

    <!-- 积分弹窗 -->
    <el-dialog v-model="showPoints" title="调整积分" width="400px">
      <p>学生：<strong>{{ pointsTarget?.name }}</strong></p>
      <el-input-number v-model="pointsValue" :min="-100" :max="100" />
      <el-input v-model="pointsReason" placeholder="原因" style="margin-top: 12px" />
      <template #footer>
        <el-button @click="showPoints = false">取消</el-button>
        <el-button type="primary" @click="submitPoints">确认</el-button>
      </template>
    </el-dialog>

    <!-- 批量积分弹窗 -->
    <el-dialog v-model="showBatchPoints" title="批量积分" width="400px">
      <p>已选 <strong>{{ selected.length }}</strong> 名学生</p>
      <el-input-number v-model="batchPointsValue" :min="-100" :max="100" />
      <el-input v-model="batchPointsReason" placeholder="原因" style="margin-top: 12px" />
      <template #footer>
        <el-button @click="showBatchPoints = false">取消</el-button>
        <el-button type="primary" @click="submitBatchPoints">确认</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入弹窗 -->
    <el-dialog v-model="showBatch" title="批量导入" width="500px">
      <p style="color: #94a3b8; font-size: 13px">每行一个学生，格式：学号,姓名,萌宠类型(cat/dog/rabbit/panda/penguin)</p>
      <el-input v-model="batchText" type="textarea" :rows="8" placeholder="01,张三,cat&#10;02,李四,dog&#10;03,王五,rabbit" />
      <template #footer>
        <el-button @click="showBatch = false">取消</el-button>
        <el-button type="primary" @click="importBatch">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
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

const showAdd = ref(false)
const addForm = ref({ student_no: '', name: '', pet_type: 'cat' })

const showPoints = ref(false)
const pointsTarget = ref(null)
const pointsValue = ref(5)
const pointsReason = ref('')

const showBatchPoints = ref(false)
const batchPointsValue = ref(5)
const batchPointsReason = ref('')

const showBatch = ref(false)
const batchText = ref('')

const petEmojis = { cat: '🐱', dog: '🐶', rabbit: '🐰', panda: '🐼', penguin: '🐧' }
function petEmoji(type) { return petEmojis[type] || '🐱' }

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
    addForm.value = { student_no: '', name: '', pet_type: 'cat' }
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

function onSelect(rows) { selected.value = rows }

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
    const [student_no, name, pet_type] = line.split(',').map(s => s.trim())
    return { student_no, name, pet_type: pet_type || 'cat' }
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

onMounted(fetchStudents)
watch(() => classStore.currentClassId, fetchStudents)
</script>

<style scoped>
.students-page { max-width: 1200px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h1 { margin: 0; font-size: 22px; }
.filter-card { margin-bottom: 16px; border-radius: 12px; }
.filter-card :deep(.el-card__body) { padding: 12px 16px; }
</style>
