<template>
  <div class="badges-page">
    <div class="page-header">
      <h1>🎖️ 勋章管理</h1>
      <el-button type="primary" @click="showAdd = true"><el-icon><Plus /></el-icon> 创建勋章</el-button>
    </div>

    <!-- 勋章列表 -->
    <el-row :gutter="16">
      <el-col :span="6" v-for="badge in badges" :key="badge.id">
        <el-card shadow="hover" class="badge-card">
          <div class="badge-icon">{{ badge.icon }}</div>
          <h3>{{ badge.name }}</h3>
          <p>{{ badge.description }}</p>
          <el-space>
            <el-button size="small" @click="openAward(badge)">🎖️ 颁发</el-button>
            <el-popconfirm title="确定删除？" @confirm="deleteBadge(badge.id)">
              <template #reference><el-button size="small" type="danger">删除</el-button></template>
            </el-popconfirm>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
    <el-empty v-if="!badges.length" description="暂无勋章，点击上方创建" />

    <!-- 颁发记录 -->
    <el-card shadow="never" style="margin-top: 24px; border-radius: 16px">
      <template #header><span>📋 颁发记录</span></template>
      <el-table :data="records" stripe v-if="records.length">
        <el-table-column label="勋章" width="80">
          <template #default="{ row }">{{ row.badge_icon }}</template>
        </el-table-column>
        <el-table-column prop="badge_name" label="名称" />
        <el-table-column prop="student_name" label="学生" />
        <el-table-column prop="awarded_at" label="时间" width="170">
          <template #default="{ row }">{{ formatDate(row.awarded_at) }}</template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无颁发记录" :image-size="60" />
    </el-card>

    <!-- 创建勋章弹窗 -->
    <el-dialog v-model="showAdd" title="创建勋章" width="400px">
      <el-form :model="addForm" label-width="60px">
        <el-form-item label="名称"><el-input v-model="addForm.name" /></el-form-item>
        <el-form-item label="图标">
          <el-select v-model="addForm.icon">
            <el-option v-for="e in emojiOptions" :key="e" :label="e" :value="e" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="addForm.description" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" @click="createBadge">创建</el-button>
      </template>
    </el-dialog>

    <!-- 颁发弹窗 -->
    <el-dialog v-model="showAward" title="颁发勋章" width="400px">
      <p>勋章：<strong>{{ awardBadge?.icon }} {{ awardBadge?.name }}</strong></p>
      <el-select v-model="awardStudentId" placeholder="选择学生" style="width: 100%">
        <el-option v-for="s in students" :key="s.id" :label="`${s.name} (${s.student_no})`" :value="s.id" />
      </el-select>
      <template #footer>
        <el-button @click="showAward = false">取消</el-button>
        <el-button type="primary" @click="awardBadgeSubmit">颁发</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '../api'
import { useClassStore } from '../stores/class'

const classStore = useClassStore()
const badges = ref([])
const records = ref([])
const students = ref([])

const showAdd = ref(false)
const addForm = ref({ name: '', icon: '🏅', description: '' })
const emojiOptions = ['🏅', '⭐', '🎖️', '🌟', '👑', '🎯', '💎', '🏆', '📚', '💪', '🎨', '🔬']

const showAward = ref(false)
const awardBadge = ref(null)
const awardStudentId = ref(null)

function formatDate(d) { return dayjs(d).format('MM-DD HH:mm') }

async function fetchBadges() {
  try { const res = await api.get('/api/badges/'); badges.value = res.data } catch (e) {}
}

async function fetchRecords() {
  try { const res = await api.get('/api/badges/records'); records.value = res.data } catch (e) {}
}

async function fetchStudents() {
  if (!classStore.currentClassId) return
  try {
    const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } })
    students.value = res.data
  } catch (e) {}
}

async function createBadge() {
  try {
    await api.post('/api/badges/', addForm.value)
    ElMessage.success('勋章已创建')
    showAdd.value = false
    addForm.value = { name: '', icon: '🏅', description: '' }
    fetchBadges()
  } catch (e) {}
}

async function deleteBadge(id) {
  try {
    await api.delete(`/api/badges/${id}`)
    ElMessage.success('已删除')
    fetchBadges()
  } catch (e) {}
}

function openAward(badge) {
  awardBadge.value = badge
  awardStudentId.value = null
  showAward.value = true
  fetchStudents()
}

async function awardBadgeSubmit() {
  if (!awardStudentId.value) { ElMessage.warning('请选择学生'); return }
  try {
    await api.post('/api/badges/award', { badge_id: awardBadge.value.id, student_id: awardStudentId.value })
    ElMessage.success('颁发成功！')
    showAward.value = false
    fetchRecords()
  } catch (e) {}
}

onMounted(() => { fetchBadges(); fetchRecords(); fetchStudents() })
</script>

<style scoped>
.badges-page { max-width: 1100px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h1 { margin: 0; font-size: 22px; }
.badge-card { text-align: center; border-radius: 16px; margin-bottom: 16px; }
.badge-icon { font-size: 40px; margin-bottom: 8px; }
.badge-card h3 { margin: 0 0 4px; }
.badge-card p { color: #94a3b8; font-size: 13px; margin: 0 0 12px; }
</style>
