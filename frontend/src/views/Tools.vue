<template>
  <div class="tools-page">
    <div class="page-header">
      <h1>🎮 课堂工具</h1>
    </div>

    <el-row :gutter="16">
      <el-col :span="6" v-for="tool in tools" :key="tool.id">
        <el-card shadow="hover" class="tool-card" @click="openTool(tool.id)">
          <div class="tool-icon">{{ tool.icon }}</div>
          <h3>{{ tool.name }}</h3>
          <p>{{ tool.desc }}</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- 随机点名弹窗 -->
    <el-dialog v-model="showRandom" title="🎲 随机点名" width="500px" :close-on-click-modal="false">
      <div class="random-result" v-if="randomResult">
        <div class="random-pet">{{ petEmoji(randomResult.pet_type) }}</div>
        <div class="random-name">{{ randomResult.name }}</div>
        <div class="random-no">{{ randomResult.student_no }}</div>
      </div>
      <div class="random-result" v-else>
        <div style="font-size: 18px; color: #94a3b8">点击按钮随机抽取</div>
      </div>
      <template #footer>
        <el-button type="primary" size="large" @click="randomPick" :loading="randomSpinning">
          🎲 开始抽取
        </el-button>
      </template>
    </el-dialog>

    <!-- 计时器弹窗 -->
    <el-dialog v-model="showTimer" title="⏱️ 计时器" width="400px" :close-on-click-modal="false">
      <div class="timer-display">{{ timerDisplay }}</div>
      <el-space>
        <el-button @click="setTimer(60)">1分钟</el-button>
        <el-button @click="setTimer(180)">3分钟</el-button>
        <el-button @click="setTimer(300)">5分钟</el-button>
      </el-space>
      <template #footer>
        <el-button @click="toggleTimer">{{ timerRunning ? '⏸ 暂停' : '▶ 开始' }}</el-button>
        <el-button @click="resetTimer">🔄 重置</el-button>
      </template>
    </el-dialog>

    <!-- 随机分组弹窗 -->
    <el-dialog v-model="showGroup" title="👥 随机分组" width="500px">
      <el-form inline>
        <el-form-item label="分几组">
          <el-input-number v-model="groupCount" :min="2" :max="10" />
        </el-form-item>
      </el-form>
      <div v-if="groups.length" style="margin-top: 16px">
        <div v-for="(group, i) in groups" :key="i" style="margin-bottom: 12px">
          <el-tag size="large" type="primary" style="margin-right: 8px">第{{ i + 1 }}组</el-tag>
          <el-tag v-for="s in group" :key="s.id" style="margin: 2px">{{ petEmoji(s.pet_type) }} {{ s.name }}</el-tag>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="doGroup">开始分组</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import api from '../api'
import { useClassStore } from '../stores/class'

const classStore = useClassStore()

const tools = [
  { id: 'random', icon: '🎲', name: '随机点名', desc: '公平随机，支持多轮不重复' },
  { id: 'timer', icon: '⏱️', name: '计时器', desc: '课堂计时，到时提醒' },
  { id: 'group', icon: '👥', name: '随机分组', desc: '均衡分组，支持设置组数' },
  { id: 'lottery', icon: '🎰', name: '积分抽奖', desc: '消耗积分抽奖，激励学生' },
]

const petEmojis = { cat: '🐱', dog: '🐶', rabbit: '🐰', panda: '🐼', penguin: '🐧' }
function petEmoji(type) { return petEmojis[type] || '🐱' }

// 随机点名
const showRandom = ref(false)
const randomResult = ref(null)
const randomSpinning = ref(false)
let allStudents = []

async function randomPick() {
  if (!allStudents.length) {
    const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } })
    allStudents = res.data
  }
  if (!allStudents.length) return

  randomSpinning.value = true
  randomResult.value = null
  let count = 0
  const interval = setInterval(() => {
    randomResult.value = allStudents[Math.floor(Math.random() * allStudents.length)]
    count++
    if (count > 15) {
      clearInterval(interval)
      randomSpinning.value = false
    }
  }, 100)
}

// 计时器
const showTimer = ref(false)
const timerSeconds = ref(60)
const timerRunning = ref(false)
let timerInterval = null

const timerDisplay = computed(() => {
  const m = Math.floor(timerSeconds.value / 60)
  const s = timerSeconds.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

function setTimer(sec) { timerSeconds.value = sec; timerRunning.value = false; clearInterval(timerInterval) }
function toggleTimer() {
  if (timerRunning.value) {
    clearInterval(timerInterval)
    timerRunning.value = false
  } else {
    timerRunning.value = true
    timerInterval = setInterval(() => {
      if (timerSeconds.value <= 0) { clearInterval(timerInterval); timerRunning.value = false; return }
      timerSeconds.value--
    }, 1000)
  }
}
function resetTimer() { clearInterval(timerInterval); timerSeconds.value = 60; timerRunning.value = false }
onUnmounted(() => clearInterval(timerInterval))

// 随机分组
const showGroup = ref(false)
const groupCount = ref(3)
const groups = ref([])

async function doGroup() {
  const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } })
  const list = [...res.data].sort(() => Math.random() - 0.5)
  groups.value = Array.from({ length: groupCount.value }, () => [])
  list.forEach((s, i) => groups.value[i % groupCount.value].push(s))
}

function openTool(id) {
  if (id === 'random') { randomResult.value = null; showRandom.value = true }
  else if (id === 'timer') { resetTimer(); showTimer.value = true }
  else if (id === 'group') { groups.value = []; showGroup.value = true }
}
</script>

<style scoped>
.tools-page { max-width: 900px; }
.page-header h1 { margin: 0 0 20px; font-size: 22px; }
.tool-card { text-align: center; cursor: pointer; border-radius: 16px; transition: transform 0.2s; margin-bottom: 16px; }
.tool-card:hover { transform: translateY(-4px); }
.tool-icon { font-size: 40px; margin-bottom: 8px; }
.tool-card h3 { margin: 0 0 4px; }
.tool-card p { color: #94a3b8; font-size: 13px; margin: 0; }
.random-result { text-align: center; padding: 32px 0; }
.random-pet { font-size: 64px; }
.random-name { font-size: 28px; font-weight: 700; color: #6366f1; margin-top: 8px; }
.random-no { color: #94a3b8; }
.timer-display { font-size: 64px; font-weight: 700; text-align: center; color: #6366f1; font-variant-numeric: tabular-nums; padding: 24px 0; }
</style>
