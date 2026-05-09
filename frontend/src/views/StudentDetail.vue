<template>
  <div class="student-detail" v-loading="loading">
    <el-page-header @back="$router.push('/students')" :title="'返回学生列表'">
      <template #content>
        <span style="font-size: 18px; font-weight: 600">{{ petEmoji(student?.pet_type) }} {{ student?.name }}</span>
      </template>
    </el-page-header>

    <el-row :gutter="20" style="margin-top: 24px" v-if="student">
      <!-- 基本信息 -->
      <el-col :span="8">
        <el-card shadow="never" class="info-card">
          <div class="pet-avatar">{{ petEmoji(student.pet_type) }}</div>
          <h2>{{ student.name }}</h2>
          <p class="student-no">学号：{{ student.student_no }}</p>
          <el-divider />
          <div class="info-grid">
            <div><span class="label">等级</span><span class="value">Lv.{{ student.level }}</span></div>
            <div><span class="label">积分</span><span class="value" :class="student.points >= 0 ? 'positive' : 'negative'">{{ student.points }}</span></div>
            <div><span class="label">萌宠</span><span class="value">{{ student.pet_name || '未命名' }}</span></div>
          </div>
          <el-divider />
          <el-button @click="showEdit = true" style="width: 100%">✏️ 编辑信息</el-button>
        </el-card>
      </el-col>

      <!-- 积分记录 -->
      <el-col :span="16">
        <el-card shadow="never">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center">
              <span>📝 积分记录</span>
              <el-button type="primary" size="small" @click="showPoints = true">➕ 调整积分</el-button>
            </div>
          </template>
          <el-table :data="logs" stripe>
            <el-table-column prop="created_at" label="时间" width="170">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column prop="points" label="积分" width="80">
              <template #default="{ row }">
                <el-tag :type="row.points > 0 ? 'success' : 'danger'">{{ row.points > 0 ? '+' : '' }}{{ row.points }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="原因" />
            <el-table-column prop="category" label="类型" width="80" />
          </el-table>
          <el-empty v-if="!logs.length" description="暂无积分记录" :image-size="80" />
        </el-card>

        <!-- 勋章 -->
        <el-card shadow="never" style="margin-top: 16px">
          <template #header><span>🎖️ 获得勋章</span></template>
          <el-space wrap v-if="badges.length">
            <el-tag v-for="b in badges" :key="b.id" size="large" effect="plain">
              {{ b.badge_icon }} {{ b.badge_name }}
            </el-tag>
          </el-space>
          <el-empty v-else description="暂无勋章" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="showEdit" title="编辑学生信息" width="400px">
      <el-form :model="editForm" label-width="60px">
        <el-form-item label="姓名"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="学号"><el-input v-model="editForm.student_no" /></el-form-item>
        <el-form-item label="萌宠">
          <el-select v-model="editForm.pet_type">
            <el-option label="🐱 猫咪" value="cat" />
            <el-option label="🐶 小狗" value="dog" />
            <el-option label="🐰 兔子" value="rabbit" />
            <el-option label="🐼 熊猫" value="panda" />
            <el-option label="🐧 企鹅" value="penguin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEdit = false">取消</el-button>
        <el-button type="primary" @click="updateStudent">保存</el-button>
      </template>
    </el-dialog>

    <!-- 积分弹窗 -->
    <el-dialog v-model="showPoints" title="调整积分" width="400px">
      <el-input-number v-model="pointsValue" :min="-100" :max="100" />
      <el-input v-model="pointsReason" placeholder="原因" style="margin-top: 12px" />
      <template #footer>
        <el-button @click="showPoints = false">取消</el-button>
        <el-button type="primary" @click="submitPoints">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '../api'

const route = useRoute()
const studentId = route.params.id

const student = ref(null)
const logs = ref([])
const badges = ref([])
const loading = ref(true)

const showEdit = ref(false)
const editForm = reactive({ name: '', student_no: '', pet_type: 'cat' })

const showPoints = ref(false)
const pointsValue = ref(5)
const pointsReason = ref('')

const petEmojis = { cat: '🐱', dog: '🐶', rabbit: '🐰', panda: '🐼', penguin: '🐧' }
function petEmoji(type) { return petEmojis[type] || '🐱' }
function formatDate(d) { return dayjs(d).format('MM-DD HH:mm') }

async function fetchAll() {
  loading.value = true
  try {
    const [sRes, lRes, bRes] = await Promise.all([
      api.get(`/api/students/${studentId}`),
      api.get(`/api/students/${studentId}/logs`),
      api.get(`/api/badges/student/${studentId}`),
    ])
    student.value = sRes.data
    logs.value = lRes.data
    badges.value = bRes.data
    Object.assign(editForm, { name: student.value.name, student_no: student.value.student_no, pet_type: student.value.pet_type })
  } catch (e) { /* handled */ } finally { loading.value = false }
}

async function updateStudent() {
  try {
    await api.put(`/api/students/${studentId}`, editForm)
    ElMessage.success('更新成功')
    showEdit.value = false
    fetchAll()
  } catch (e) { /* handled */ }
}

async function submitPoints() {
  if (!pointsReason.value) { ElMessage.warning('请填写原因'); return }
  try {
    await api.post('/api/students/points/adjust', {
      student_id: Number(studentId), points: pointsValue.value, reason: pointsReason.value,
    })
    ElMessage.success('积分已更新')
    showPoints.value = false
    fetchAll()
  } catch (e) { /* handled */ }
}

onMounted(fetchAll)
</script>

<style scoped>
.student-detail { max-width: 1100px; }
.info-card { text-align: center; border-radius: 16px; }
.pet-avatar { font-size: 64px; margin: 8px 0; }
.info-card h2 { margin: 0; font-size: 20px; }
.student-no { color: #94a3b8; font-size: 13px; }
.info-grid { display: flex; justify-content: space-around; }
.info-grid .label { display: block; font-size: 12px; color: #94a3b8; }
.info-grid .value { font-size: 20px; font-weight: 700; color: #1e293b; }
.info-grid .value.positive { color: #10b981; }
.info-grid .value.negative { color: #ef4444; }
</style>
