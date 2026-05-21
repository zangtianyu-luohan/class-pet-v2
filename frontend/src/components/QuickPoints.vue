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

const presetReasons = [
  '回答问题',
  '作业优秀',
  '课堂表现好',
  '纪律问题',
  '卫生问题'
]

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadStudents()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const filteredStudents = computed(() => {
  let list = [...students.value]

  if (search.value) {
    const keyword = search.value.toLowerCase()
    list = list.filter(s =>
      s.name.toLowerCase().includes(keyword) ||
      s.student_no.toLowerCase().includes(keyword)
    )
  }

  if (sortBy.value === 'points') {
    list.sort((a, b) => b.points - a.points)
  } else {
    list.sort((a, b) => a.name.localeCompare(b.name))
  }

  return list
})

const selectedStudents = computed(() => {
  return students.value.filter(s => s.selected)
})

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

async function undoLast() {
  if (!lastAction.value) return

  try {
    if (lastAction.value.studentIds) {
      for (const studentId of lastAction.value.studentIds) {
        await api.post('/api/students/points/adjust', {
          student_id: studentId,
          points: lastAction.value.points,
          reason: `撤销: ${lastAction.value.reason}`
        })
      }
    } else {
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

function formatTime(date) {
  if (!date) return ''
  const d = new Date(date)
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}

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
