<template>
  <el-dialog v-model="visible" title="🎰 积分抽奖" :close-on-click-modal="false" width="460px" @close="$emit('update:modelValue', false)">
    <div v-if="showPrizeEdit" style="margin-bottom:12px;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
        <span style="font-weight:600;">奖项设置（权重总和: {{ totalWeight }}）</span>
        <el-button size="small" @click="addPrize">+ 添加奖项</el-button>
      </div>
      <div v-for="(prize, idx) in prizes" :key="idx" style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">
        <el-input v-model="prize.name" style="width:140px;" placeholder="名称" />
        <el-input v-model="prize.text" style="width:120px;" placeholder="奖品内容" />
        <el-input-number v-model="prize.weight" :min="1" :max="100" style="width:100px;" />
        <el-button type="danger" size="small" circle @click="removePrize(idx)">×</el-button>
      </div>
      <div style="text-align:right;margin-top:8px;">
        <el-button size="small" @click="resetPrizes">恢复默认</el-button>
        <el-button type="primary" size="small" @click="savePrizes">保存</el-button>
      </div>
    </div>
    <div v-else>
      <div style="margin-bottom:12px;text-align:center;">
        <el-button size="small" @click="showPrizeEdit=true">⚙️ 奖项设置</el-button>
      </div>
      <div v-if="result && !result.rolling" style="text-align:center;padding:20px 0;">
        <div style="font-size:20px;font-weight:700;margin:8px 0;">{{ result.student.name }}</div>
        <el-tag size="large" :color="result.prize.color" style="color:#fff;font-size:16px;padding:8px 20px;">
          {{ result.prize.name }}：{{ result.prize.text }}
        </el-tag>
      </div>
      <div v-else-if="result && result.rolling" style="text-align:center;padding:20px 0;">
        <div style="font-size:20px;color:#6366f1;font-weight:600;">{{ result.student.name }}</div>
      </div>
      <div v-else style="text-align:center;color:#94a3b8;padding:20px 0;">点击开始抽奖</div>
    </div>
    <template #footer>
      <el-button type="primary" size="large" @click="start" :loading="spinning">
        🎰 {{ running ? '抽奖中...' : '开始抽奖' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'
import { useClassStore } from '../../stores/class'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])
const classStore = useClassStore()

const visible = ref(props.modelValue)
const result = ref(null)
const running = ref(false)
const spinning = ref(false)
const showPrizeEdit = ref(false)
const students = ref([])

const defaultPrizes = [
  { name: '🥇 一等奖', text: '积分 ×3', color: '#f59e0b', weight: 5 },
  { name: '🥈 二等奖', text: '积分 ×2', color: '#6366f1', weight: 15 },
  { name: '🥉 三等奖', text: '积分 ×1', color: '#10b981', weight: 30 },
  { name: '🎁 参与奖', text: '积分不变', color: '#94a3b8', weight: 50 },
]
const prizes = ref(JSON.parse(localStorage.getItem('lottery_prizes') || 'null') || defaultPrizes)
const totalWeight = computed(() => prizes.value.reduce((s, p) => s + (Number(p.weight) || 0), 0))

watch(() => props.modelValue, v => {
  visible.value = v
  if (v) { result.value = null; running.value = false; showPrizeEdit.value = false; loadStudents() }
})
watch(visible, v => emit('update:modelValue', v))

function savePrizes() {
  for (const p of prizes.value) { if (!p.name || !p.weight) { ElMessage.warning('奖项名称和权重不能为空'); return } }
  localStorage.setItem('lottery_prizes', JSON.stringify(prizes.value))
  showPrizeEdit.value = false
  ElMessage.success('奖项已保存')
}
function resetPrizes() { prizes.value = JSON.parse(JSON.stringify(defaultPrizes)); localStorage.removeItem('lottery_prizes'); ElMessage.success('已恢复默认') }
function addPrize() { prizes.value.push({ name: '🎊 新奖项', text: '积分 ×1', color: '#8b5cf6', weight: 10 }) }
function removePrize(idx) { if (prizes.value.length <= 2) { ElMessage.warning('至少保留2个奖项'); return }; prizes.value.splice(idx, 1) }

async function loadStudents() {
  try {
    const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } })
    students.value = res.data
  } catch { students.value = [] }
}

function rollPrize() {
  const total = prizes.value.reduce((s, p) => s + (Number(p.weight) || 0), 0)
  let r = Math.random() * total
  for (const p of prizes.value) { r -= (Number(p.weight) || 0); if (r <= 0) return p }
  return prizes.value[prizes.value.length - 1]
}

async function start() {
  if (!students.value.length) { ElMessage.warning('没有可用的学生'); return }
  running.value = true
  result.value = null
  spinning.value = true

  const student = students.value[Math.floor(Math.random() * students.value.length)]
  const prize = rollPrize()
  let count = 0
  const interval = setInterval(() => {
    result.value = {
      student: students.value[Math.floor(Math.random() * students.value.length)],
      prize: prizes.value[Math.floor(Math.random() * prizes.value.length)],
      rolling: true
    }
    count++
    if (count > 20) {
      clearInterval(interval)
      result.value = { student, prize, rolling: false }
      spinning.value = false

      // 基于数据结构的积分逻辑（不依赖文字）
      const prizeIdx = prizes.value.indexOf(prize)
      const isParticipation = prize.text.includes('不变')
      const multiplier = prize.text.match(/×(\d+)/)?.[1]
      const cost = 10

      let delta
      if (isParticipation) {
        delta = -cost
      } else if (multiplier) {
        delta = cost * (parseInt(multiplier) - 1)
      } else {
        delta = -cost
      }

      if (delta !== 0) {
        api.post('/api/students/points/adjust', {
          student_id: student.id,
          points: delta,
          reason: `抽奖${prize.name}`,
          category: 'lottery'
        }).catch(() => {})
      } else {
        api.post('/api/students/points/adjust', {
          student_id: student.id,
          points: -cost,
          reason: '抽奖参与奖',
          category: 'lottery'
        }).catch(() => {})
      }
      loadStudents()
    }
  }, 80)
}
</script>
