<template>
  <div class="tools-page">
    <div class="page-header">
      <h1>🎮 课堂工具</h1>
    </div>

    <el-row :gutter="16">
      <el-col :xs="12" :sm="8" :md="6" v-for="tool in tools" :key="tool.id">
        <el-card shadow="hover" class="tool-card" @click="openTool(tool.id)">
          <div class="tool-icon">{{ tool.icon }}</div>
          <h3>{{ tool.name }}</h3>
          <p>{{ tool.desc }}</p>
        </el-card>
      </el-col>
    </el-row>

    <!-- 随机点名弹窗 -->
    <el-dialog v-model="showRandom" title="🎲 随机点名" :close-on-click-modal="false">
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
    <el-dialog v-model="showTimer" title="⏱️ 计时器" :close-on-click-modal="false">
      <div class="timer-display">{{ timerDisplay }}</div>
      <div class="timer-presets">
        <el-button @click="setTimer(60)">1分钟</el-button>
        <el-button @click="setTimer(180)">3分钟</el-button>
        <el-button @click="setTimer(300)">5分钟</el-button>
      </div>
      <template #footer>
        <el-button @click="toggleTimer">{{ timerRunning ? '⏸ 暂停' : '▶ 开始' }}</el-button>
        <el-button @click="resetTimer">🔄 重置</el-button>
      </template>
    </el-dialog>

    <!-- 随机分组弹窗 -->
    <el-dialog v-model="showGroup" title="👥 随机分组">
      <el-form inline>
        <el-form-item label="分几组">
          <el-input-number v-model="groupCount" :min="2" :max="10" />
        </el-form-item>
      </el-form>
      <div v-if="groups.length" style="margin-top: 16px">
        <div v-for="(group, i) in groups" :key="i" class="group-row">
          <el-tag size="large" type="primary" style="margin-right: 8px">第{{ i + 1 }}组</el-tag>
          <el-tag v-for="s in group" :key="s.id" style="margin: 2px">{{ petEmoji(s.pet_type) }} {{ s.name }}</el-tag>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="doGroup">开始分组</el-button>
      </template>
    </el-dialog>

    <!-- 积分抽奖弹窗 -->
    <el-dialog v-model="showLottery" title="🎰 积分抽奖" :close-on-click-modal="false" width="460px">
      <!-- 奖项编辑面板 -->
      <div v-if="showPrizeEdit" style="margin-bottom:12px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
          <span style="font-weight:600;color:#e2e8f0;">✏️ 编辑奖项</span>
          <el-button size="small" type="primary" plain @click="addPrize">➕ 添加</el-button>
        </div>
        <div v-for="(p, idx) in lotteryPrizes" :key="idx" style="display:flex;gap:6px;align-items:center;margin-bottom:8px;flex-wrap:wrap;">
          <el-input v-model="p.name" size="small" style="width:90px;" placeholder="名称" />
          <el-input v-model="p.text" size="small" style="width:90px;" placeholder="奖励说明" />
          <el-input v-model="p.color" size="small" style="width:80px;" placeholder="#颜色" />
          <el-input-number v-model.number="p.weight" size="small" :min="1" :max="100" style="width:80px;" controls-position="right" />
          <span style="font-size:12px;color:#64748b;">%</span>
          <el-button size="small" type="danger" text @click="removePrize(idx)" style="padding:4px;">🗑️</el-button>
        </div>
        <div style="font-size:12px;color:#94a3b8;margin-top:8px;">
          权重总和：{{ totalWeight }}%（建议100%）
          <span v-if="totalWeight !== 100" style="color:#f59e0b;">⚠️ 权重不等于100%，概率将按比例计算</span>
        </div>
        <div style="display:flex;gap:8px;margin-top:12px;">
          <el-button size="small" type="primary" @click="savePrizes">💾 保存</el-button>
          <el-button size="small" @click="resetPrizes">🔄 恢复默认</el-button>
          <el-button size="small" @click="showPrizeEdit = false">取消</el-button>
        </div>
        <el-divider style="margin:12px 0;" />
      </div>

      <!-- 抽奖主体 -->
      <div class="lottery-config" v-if="(!lotteryResult || lotteryResult.rolling) && !showPrizeEdit">
        <div style="text-align:center;margin-bottom:16px;">
          <div style="font-size:48px;margin-bottom:8px;">🎰</div>
          <div style="color:#94a3b8;font-size:14px;">每次消耗 <b style="color:#f59e0b;">{{ lotteryCost }}</b> 积分参与抽奖</div>
          <div style="color:#64748b;font-size:12px;margin-top:4px;">当前有 <b>{{ lotteryStudents.length }}</b> 名学生积分足够</div>
        </div>
        <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:12px;">
          <span style="font-size:13px;color:#94a3b8;">消耗积分：</span>
          <el-input-number v-model="lotteryCost" :min="1" :max="100" size="small" @change="loadLotteryStudents()" />
        </div>
        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px;">
          <div v-for="p in lotteryPrizes" :key="p.name"
            style="text-align:center;padding:8px 12px;border-radius:8px;background:#0f172a;border:1px solid #1e293b;min-width:90px;">
            <div style="font-size:13px;font-weight:600;" :style="{color:p.color}">{{ p.name }}</div>
            <div style="font-size:11px;color:#64748b;">{{ p.text }}</div>
            <div style="font-size:10px;color:#475569;">{{ p.weight }}%</div>
          </div>
        </div>
        <div style="text-align:center;margin-top:12px;">
          <el-button size="small" text type="primary" @click="showPrizeEdit = true">✏️ 编辑奖项</el-button>
        </div>
      </div>
      <div v-if="lotteryResult && !lotteryResult.rolling && !showPrizeEdit" class="lottery-result" style="text-align:center;padding:20px 0;">
        <div style="font-size:56px;margin-bottom:12px;">{{ petEmoji(lotteryResult.student.pet_type) }}</div>
        <div style="font-size:20px;font-weight:700;color:#f1f5f9;margin-bottom:4px;">{{ lotteryResult.student.name }}</div>
        <div style="font-size:14px;color:#94a3b8;margin-bottom:16px;">{{ lotteryResult.student.student_no }}</div>
        <div style="font-size:28px;font-weight:800;margin-bottom:4px;" :style="{color:lotteryResult.prize.color}">{{ lotteryResult.prize.name }}</div>
        <div style="font-size:15px;color:#94a3b8;">{{ lotteryResult.prize.text }}</div>
      </div>
      <template #footer v-if="!showPrizeEdit">
        <el-button type="warning" size="large" @click="lotteryRunning=false; startLottery()" :loading="lotterySpinning" :disabled="lotterySpinning">
          🎰 {{ lotteryResult && !lotteryResult.rolling ? '再来一次' : '开始抽奖' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 积分兑换弹窗 -->
    <el-dialog v-model="showExchange" title="🎁 积分兑换奖品" :close-on-click-modal="false" width="500px">
      <div style="text-align:center;margin-bottom:16px;">
        <div style="font-size:48px;">🎁</div>
        <div style="color:#94a3b8;font-size:14px;">学生用积分兑换实物奖品</div>
      </div>
      <!-- 奖品编辑 -->
      <div style="margin-bottom:16px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
          <span style="font-weight:600;font-size:14px;">🏷️ 奖品列表</span>
          <el-button size="small" type="primary" plain @click="addExchangeItem">➕ 添加奖品</el-button>
        </div>
        <div v-for="(item, idx) in exchangeItems" :key="idx" style="display:flex;gap:6px;align-items:center;margin-bottom:8px;flex-wrap:wrap;">
          <el-input v-model="item.name" size="small" style="width:100px;" placeholder="奖品名称" />
          <el-input-number v-model.number="item.cost" size="small" :min="1" :max="9999" style="width:100px;" controls-position="right" />
          <span style="font-size:12px;color:#64748b;">积分</span>
          <el-button size="small" type="danger" text @click="exchangeItems.splice(idx, 1)" style="padding:4px;">🗑️</el-button>
        </div>
        <div style="display:flex;gap:8px;margin-top:8px;">
          <el-button size="small" type="primary" @click="saveExchangeItems">💾 保存</el-button>
          <el-button size="small" @click="resetExchangeItems">🔄 恢复默认</el-button>
        </div>
      </div>
      <el-divider />
      <!-- 兑换操作 -->
      <div>
        <div style="font-weight:600;font-size:14px;margin-bottom:10px;">🎯 执行兑换</div>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px;">
          <el-select v-model="exchangeStudentId" filterable placeholder="选择学生" style="width:160px;" size="small">
            <el-option v-for="s in exchangeStudents" :key="s.id" :label="`${s.name} (${s.points}分)`" :value="s.id" />
          </el-select>
          <el-select v-model="exchangeItemIdx" placeholder="选择奖品" style="width:140px;" size="small">
            <el-option v-for="(item, idx) in exchangeItems" :key="idx" :label="`${item.name} (${item.cost}分)`" :value="idx" />
          </el-select>
          <el-button type="success" size="small" @click="doExchange" :disabled="!exchangeStudentId || exchangeItemIdx === null">兑换</el-button>
        </div>
        <div v-if="exchangeHistory.length" style="margin-top:10px;">
          <div style="font-size:12px;color:#64748b;margin-bottom:6px;">兑换记录：</div>
          <div v-for="(h, i) in exchangeHistory" :key="i" style="font-size:13px;color:#94a3b8;padding:4px 0;border-bottom:1px solid #1e293b;">
            {{ h.student }} 兑换了 {{ h.item }}（-{{ h.cost }}分）
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 积分阈值提醒弹窗 -->
    <el-dialog v-model="showThreshold" title="🔔 积分阈值提醒" :close-on-click-modal="false" width="500px">
      <div style="text-align:center;margin-bottom:16px;">
        <div style="font-size:48px;">🔔</div>
        <div style="color:#94a3b8;font-size:14px;">设置积分阈值，达标学生自动弹窗提醒可兑换/抽奖</div>
      </div>
      <div style="display:flex;gap:12px;align-items:center;margin-bottom:16px;flex-wrap:wrap;">
        <span style="font-size:14px;font-weight:600;">阈值积分：</span>
        <el-input-number v-model="thresholdPoints" :min="1" :max="9999" size="small" />
        <el-button type="primary" size="small" @click="checkThreshold">🔍 检查达标学生</el-button>
      </div>
      <div v-if="thresholdStudents.length" style="margin-top:12px;">
        <el-alert :title="`🎉 有 ${thresholdStudents.length} 名学生积分达标！`" type="success" show-icon :closable="false" style="margin-bottom:12px;" />
        <div v-for="s in thresholdStudents" :key="s.id" style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:#0f172a;border-radius:8px;margin-bottom:6px;">
          <div>
            <span style="font-size:15px;font-weight:600;color:#e2e8f0;">{{ petEmoji(s.pet_type) }} {{ s.name }}</span>
            <span style="font-size:12px;color:#64748b;margin-left:8px;">{{ s.student_no }}</span>
          </div>
          <el-tag type="success" size="large">{{ s.points }} 分</el-tag>
        </div>
      </div>
      <div v-else-if="thresholdChecked" style="text-align:center;padding:20px;color:#64748b;">
        暂无积分达到 {{ thresholdPoints }} 分的学生
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { useClassStore } from '../stores/class'

const classStore = useClassStore()

const tools = [
  { id: 'random', icon: '🎲', name: '随机点名', desc: '公平随机，支持多轮不重复' },
  { id: 'timer', icon: '⏱️', name: '计时器', desc: '课堂计时，到时提醒' },
  { id: 'group', icon: '👥', name: '随机分组', desc: '均衡分组，支持设置组数' },
  { id: 'lottery', icon: '🎰', name: '积分抽奖', desc: '消耗积分抽奖，激励学生' },
  { id: 'exchange', icon: '🎁', name: '积分兑换', desc: '积分兑换奖品，实物激励' },
  { id: 'threshold', icon: '🔔', name: '积分提醒', desc: '设置阈值，达标自动提醒' },
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
  else if (id === 'lottery') { lotteryResult.value = null; lotteryRunning.value = false; showLottery.value = true; loadLotteryStudents() }
  else if (id === 'exchange') { showExchange.value = true; loadExchangeStudents() }
  else if (id === 'threshold') { showThreshold.value = true; loadThresholdStudents() }
}

// 积分抽奖
const showLottery = ref(false)
const lotteryResult = ref(null)
const lotteryRunning = ref(false)
const lotteryCost = ref(10)
const lotteryStudents = ref([])
const lotterySpinning = ref(false)
const showPrizeEdit = ref(false)

// 奖项配置（从 localStorage 加载，可编辑）
const defaultPrizes = [
  { name: '🥇 一等奖', text: '积分 ×3', color: '#f59e0b', weight: 5 },
  { name: '🥈 二等奖', text: '积分 ×2', color: '#6366f1', weight: 15 },
  { name: '🥉 三等奖', text: '积分 ×1', color: '#10b981', weight: 30 },
  { name: '🎁 参与奖', text: '积分不变', color: '#94a3b8', weight: 50 },
]

const lotteryPrizes = ref(JSON.parse(localStorage.getItem('lottery_prizes') || 'null') || defaultPrizes)

function savePrizes() {
  // 校验：名称和权重必填，权重总和建议为100
  for (const p of lotteryPrizes.value) {
    if (!p.name || !p.weight) { ElMessage.warning('奖项名称和权重不能为空'); return }
  }
  localStorage.setItem('lottery_prizes', JSON.stringify(lotteryPrizes.value))
  showPrizeEdit.value = false
  ElMessage.success('奖项已保存')
}

function resetPrizes() {
  lotteryPrizes.value = JSON.parse(JSON.stringify(defaultPrizes))
  localStorage.removeItem('lottery_prizes')
  ElMessage.success('已恢复默认')
}

function addPrize() {
  lotteryPrizes.value.push({ name: '🎊 新奖项', text: '积分 ×1', color: '#8b5cf6', weight: 10 })
}

function removePrize(idx) {
  if (lotteryPrizes.value.length <= 2) { ElMessage.warning('至少保留2个奖项'); return }
  lotteryPrizes.value.splice(idx, 1)
}

const totalWeight = computed(() => lotteryPrizes.value.reduce((s, p) => s + (Number(p.weight) || 0), 0))

// 积分兑换
const showExchange = ref(false)
const exchangeStudents = ref([])
const exchangeStudentId = ref(null)
const exchangeItemIdx = ref(null)
const exchangeHistory = ref([])

const defaultExchangeItems = [
  { name: '📐 文具套装', cost: 50 },
  { name: '📒 笔记本', cost: 30 },
  { name: '✏️ 铅笔礼包', cost: 20 },
]
const exchangeItems = ref(JSON.parse(localStorage.getItem('exchange_items') || 'null') || defaultExchangeItems)

function addExchangeItem() { exchangeItems.value.push({ name: '🎁 新奖品', cost: 10 }) }
function saveExchangeItems() {
  localStorage.setItem('exchange_items', JSON.stringify(exchangeItems.value))
  ElMessage.success('奖品已保存')
}
function resetExchangeItems() {
  exchangeItems.value = JSON.parse(JSON.stringify(defaultExchangeItems))
  localStorage.removeItem('exchange_items')
  ElMessage.success('已恢复默认')
}

async function loadExchangeStudents() {
  try {
    const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } })
    exchangeStudents.value = res.data
  } catch (e) { console.error(e) }
}

async function doExchange() {
  const student = exchangeStudents.value.find(s => s.id === exchangeStudentId.value)
  const item = exchangeItems.value[exchangeItemIdx.value]
  if (!student || !item) return
  if (student.points < item.cost) {
    ElMessage.warning(`${student.name} 积分不足（当前${student.points}分，需要${item.cost}分）`)
    return
  }
  try {
    await api.post('/api/students/points', {
      student_id: student.id,
      points: -item.cost,
      reason: `积分兑换：${item.name}`,
      category: 'exchange'
    })
    exchangeHistory.value.unshift({ student: student.name, item: item.name, cost: item.cost })
    student.points -= item.cost
    ElMessage.success(`${student.name} 成功兑换 ${item.name}！`)
    exchangeStudentId.value = null
    exchangeItemIdx.value = null
    loadExchangeStudents()
  } catch (e) {
    ElMessage.error('兑换失败')
  }
}

// 积分阈值提醒
const showThreshold = ref(false)
const thresholdPoints = ref(100)
const thresholdStudents = ref([])
const thresholdChecked = ref(false)

async function loadThresholdStudents() {
  thresholdStudents.value = []
  thresholdChecked.value = false
}

async function checkThreshold() {
  try {
    const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } })
    thresholdStudents.value = res.data.filter(s => s.points >= thresholdPoints.value)
    thresholdChecked.value = true
    if (thresholdStudents.value.length) {
      ElMessage.success(`发现 ${thresholdStudents.value.length} 名学生积分达标！`)
    }
  } catch (e) { console.error(e) }
}

async function loadLotteryStudents() {
  try {
    const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } })
    lotteryStudents.value = res.data.filter(s => s.points >= lotteryCost.value)
  } catch { lotteryStudents.value = [] }
}

function rollPrize() {
  const total = lotteryPrizes.value.reduce((s, p) => s + (Number(p.weight) || 0), 0)
  let r = Math.random() * total
  for (const p of lotteryPrizes.value) { r -= (Number(p.weight) || 0); if (r <= 0) return p }
  return lotteryPrizes.value[lotteryPrizes.value.length - 1]
}

async function startLottery() {
  if (!lotteryStudents.value.length) {
    ElMessage.warning(`没有积分≥${lotteryCost.value}的学生`)
    return
  }
  lotteryRunning.value = true
  lotteryResult.value = null
  lotterySpinning.value = true

  // 抽奖动画
  let count = 0
  const student = lotteryStudents.value[Math.floor(Math.random() * lotteryStudents.value.length)]
  const prize = rollPrize()
  const interval = setInterval(() => {
    lotteryResult.value = {
      student: lotteryStudents.value[Math.floor(Math.random() * lotteryStudents.value.length)],
      prize: lotteryPrizes.value[Math.floor(Math.random() * lotteryPrizes.value.length)],
      rolling: true
    }
    count++
    if (count > 20) {
      clearInterval(interval)
      lotteryResult.value = { student, prize, rolling: false }
      lotterySpinning.value = false

      // 扣积分
      const pointsMap = { '积分 ×3': lotteryCost.value * 2, '积分 ×2': lotteryCost.value, '积分 ×1': 0, '积分不变': -lotteryCost.value }
      const delta = pointsMap[prize.text] ?? 0
      if (delta !== 0) {
        api.post(`/api/students/${student.id}/points`, {
          points: delta,
          reason: `抽奖${prize.name}`,
          category: 'lottery'
        }).catch(() => {})
      } else {
        // 参与奖只扣不加
        api.post(`/api/students/${student.id}/points`, {
          points: -lotteryCost.value,
          reason: '抽奖参与奖',
          category: 'lottery'
        }).catch(() => {})
      }
      loadLotteryStudents()
    }
  }, 80)
}
</script>

<style scoped>
.tools-page { max-width: 900px; }
.page-header h1 { margin: 0 0 20px; font-size: 22px; }

.tool-card {
  text-align: center;
  cursor: pointer;
  border-radius: 16px;
  transition: transform 0.2s;
  margin-bottom: 16px;
}
.tool-card:hover { transform: translateY(-4px); }
.tool-card :deep(.el-card__body) { padding: 20px 12px; }
.tool-icon { font-size: 40px; margin-bottom: 8px; }
.tool-card h3 { margin: 0 0 4px; font-size: 15px; }
.tool-card p { color: #94a3b8; font-size: 13px; margin: 0; }

.random-result { text-align: center; padding: 24px 0; }
.random-pet { font-size: 56px; }
.random-name { font-size: 24px; font-weight: 700; color: #6366f1; margin-top: 8px; }
.random-no { color: #94a3b8; }

.timer-display {
  font-size: 56px;
  font-weight: 700;
  text-align: center;
  color: #6366f1;
  font-variant-numeric: tabular-nums;
  padding: 20px 0;
}

.timer-presets {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.group-row { margin-bottom: 12px; }

@media (max-width: 767px) {
  .tool-card :deep(.el-card__body) { padding: 14px 8px; }
  .tool-icon { font-size: 32px; }
  .tool-card h3 { font-size: 13px; }
  .tool-card p { font-size: 12px; }
  .random-pet { font-size: 44px; }
  .random-name { font-size: 20px; }
  .timer-display { font-size: 44px; }
}
</style>
