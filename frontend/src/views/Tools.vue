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

    <!-- ========== 随机点名 ========== -->
    <el-dialog v-model="showRandom" title="🎲 随机点名" :close-on-click-modal="false">
      <div class="random-result" v-if="randomResult">
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

    <!-- ========== 计时器 ========== -->
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

    <!-- ========== 随机分组 ========== -->
    <el-dialog v-model="showGroup" title="👥 随机分组">
      <el-form inline>
        <el-form-item label="分几组">
          <el-input-number v-model="groupCount" :min="2" :max="10" />
        </el-form-item>
      </el-form>
      <div v-if="groups.length" style="margin-top: 16px">
        <div v-for="(group, i) in groups" :key="i" class="group-row">
          <el-tag size="large" type="primary" style="margin-right: 8px">第{{ i + 1 }}组</el-tag>
          <el-tag v-for="s in group" :key="s.id" style="margin: 2px">{{ s.name }}</el-tag>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="doGroup">开始分组</el-button>
      </template>
    </el-dialog>

    <!-- ========== 积分抽奖 ========== -->
    <el-dialog v-model="showLottery" title="🎰 积分抽奖" :close-on-click-modal="false" width="460px">
      <!-- 奖项编辑面板 -->
      <div v-if="showPrizeEdit" style="margin-bottom:12px;">
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
          <span style="font-weight:600;">奖项设置（权重总和: {{ totalWeight }}）</span>
          <el-button size="small" @click="addPrize">+ 添加奖项</el-button>
        </div>
        <div v-for="(prize, idx) in lotteryPrizes" :key="idx" style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">
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

      <!-- 正常抽奖界面 -->
      <div v-else>
        <div style="margin-bottom:12px;text-align:center;">
          <el-button size="small" @click="showPrizeEdit=true">⚙️ 奖项设置</el-button>
        </div>
        <div v-if="lotteryResult && !lotteryResult.rolling" style="text-align:center;padding:20px 0;">
          <div style="font-size:20px;font-weight:700;margin:8px 0;">{{ lotteryResult.student.name }}</div>
          <el-tag size="large" :color="lotteryResult.prize.color" style="color:#fff;font-size:16px;padding:8px 20px;">
            {{ lotteryResult.prize.name }}：{{ lotteryResult.prize.text }}
          </el-tag>
        </div>
        <div v-else-if="lotteryResult && lotteryResult.rolling" style="text-align:center;padding:20px 0;">
          <div style="font-size:20px;color:#6366f1;font-weight:600;">
            {{ lotteryResult.student.name }}
          </div>
        </div>
        <div v-else style="text-align:center;color:#94a3b8;padding:20px 0;">点击开始抽奖</div>
      </div>

      <template #footer>
        <el-button type="primary" size="large" @click="startLottery" :loading="lotterySpinning">
          🎰 {{ lotteryRunning ? '抽奖中...' : '开始抽奖' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- ========== 积分兑换 ========== -->
    <el-dialog v-model="showExchange" title="🎁 积分兑换" width="480px">
      <div style="margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-weight:600;">奖品设置</span>
          <el-button size="small" @click="addExchangeItem">+ 添加</el-button>
        </div>
        <div v-for="(item, idx) in exchangeItems" :key="idx" style="display:flex;gap:8px;align-items:center;margin-bottom:6px;">
          <el-input v-model="item.name" style="flex:1;" placeholder="奖品名称" />
          <el-input-number v-model="item.cost" :min="1" style="width:120px;" />
          <el-button type="danger" size="small" circle @click="exchangeItems.splice(idx,1)">×</el-button>
        </div>
        <div style="text-align:right;margin-top:8px;">
          <el-button size="small" @click="resetExchangeItems">恢复默认</el-button>
          <el-button type="primary" size="small" @click="saveExchangeItems">保存</el-button>
        </div>
      </div>

      <el-divider />
      <el-form label-width="80px">
        <el-form-item label="学生">
          <el-select v-model="exchangeStudentId" filterable placeholder="选择学生" style="width:100%;">
            <el-option v-for="s in exchangeStudents" :key="s.id" :label="`${s.name} (${s.points}分)`" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="奖品">
          <el-select v-model="exchangeItemIdx" placeholder="选择奖品" style="width:100%;">
            <el-option v-for="(item, idx) in exchangeItems" :key="idx" :label="`${item.name} (${item.cost}分)`" :value="idx" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="doExchange">确认兑换</el-button>
      </template>
    </el-dialog>

    <!-- ========== 积分阈值提醒 ========== -->
    <el-dialog v-model="showThreshold" title="🔔 积分阈值提醒">
      <el-form label-width="100px">
        <el-form-item label="目标分数">
          <el-input-number v-model="thresholdPoints" :min="10" :max="9999" />
        </el-form-item>
        <el-form-item label="自动提醒">
          <el-switch v-model="thresholdAuto" />
        </el-form-item>
      </el-form>
      <el-button type="primary" @click="checkThreshold" style="margin-bottom:12px;">检查达标学生</el-button>
      <div v-if="thresholdStudents.length" style="margin-top:8px;">
        <div v-for="s in thresholdStudents" :key="s.id" style="padding:6px 0;border-bottom:1px solid #f1f5f9;">
          {{ s.name }} — <span style="color:#6366f1;font-weight:600;">{{ s.points }}分</span>
        </div>
      </div>
      <div v-else-if="thresholdChecked" style="text-align:center;padding:20px;color:#64748b;">
        暂无积分达到 {{ thresholdPoints }} 分的学生
      </div>
    </el-dialog>

    <!-- ========== 🎲 骰子 ========== -->
    <el-dialog v-model="showDice" title="🎲 骰子" :close-on-click-modal="false" width="400px">
      <div style="text-align:center;padding:20px 0;">
        <div v-if="diceRolling" class="dice-rolling">
          <svg viewBox="0 0 100 100" width="120" height="120">
            <rect x="7" y="7" width="86" height="86" rx="11" fill="white" stroke="#6366f1" stroke-width="4"/>
            <template v-for="(pos, i) in dicePipPositions(diceDisplay)" :key="i">
              <circle :cx="pos[0]" :cy="pos[1]" r="7" fill="#6366f1"/>
            </template>
          </svg>
        </div>
        <div v-else-if="diceResult !== null" class="dice-result">
          <svg viewBox="0 0 100 100" width="120" height="120">
            <rect x="7" y="7" width="86" height="86" rx="11" fill="white" stroke="#10b981" stroke-width="4"/>
            <template v-for="(pos, i) in dicePipPositions(diceResult)" :key="i">
              <circle :cx="pos[0]" :cy="pos[1]" r="7" fill="#10b981"/>
            </template>
          </svg>
          <div style="font-size:24px;font-weight:700;color:#10b981;margin-top:12px;">{{ diceResult }} 点</div>
        </div>
        <div v-else style="color:#94a3b8;font-size:16px;">点击掷骰子</div>
      </div>

      <div style="display:flex;justify-content:center;gap:12px;margin-bottom:12px;">
        <span style="font-size:14px;line-height:32px;">骰子数：</span>
        <el-input-number v-model="diceCount" :min="1" :max="6" size="small" />
      </div>

      <template #footer>
        <el-button type="primary" size="large" @click="rollDice" :disabled="diceRolling">
          🎲 掷骰子
        </el-button>
      </template>
    </el-dialog>

    <!-- ========== 🔇 噪音检测 ========== -->
    <el-dialog v-model="showNoise" title="🔇 噪音检测" :close-on-click-modal="false" width="420px">
      <div style="text-align:center;padding:10px 0;">
        <div v-if="noiseStatus === 'idle'" style="color:#94a3b8;padding:30px 0;">点击开始检测环境噪音</div>
        <div v-else-if="noiseStatus === 'requesting'" style="color:#f59e0b;padding:30px 0;">正在请求麦克风权限...</div>
        <div v-else-if="noiseStatus === 'denied'" style="color:#ef4444;padding:30px 0;">麦克风权限被拒绝<br>请在浏览器设置中允许</div>
        <div v-else-if="noiseStatus === 'error'" style="color:#ef4444;padding:30px 0;">无法访问麦克风</div>
        <div v-else>
          <!-- 噪音等级条 -->
          <div style="margin-bottom:16px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
              <span style="font-size:13px;color:#64748b;">当前音量</span>
              <span style="font-size:13px;font-weight:600;" :style="{color: noiseLevel > noiseThreshold ? '#ef4444' : '#10b981'}">
                {{ Math.round(noiseLevel * 100) }}%
              </span>
            </div>
            <div style="height:24px;background:#f1f5f9;border-radius:12px;overflow:hidden;position:relative;">
              <div :style="{
                width: Math.min(100, noiseLevel * 100) + '%',
                height: '100%',
                borderRadius: '12px',
                transition: 'width 0.1s, background 0.3s',
                background: noiseLevel > noiseThreshold ? 'linear-gradient(90deg, #f59e0b, #ef4444)' : 'linear-gradient(90deg, #10b981, #34d399)'
              }"></div>
              <!-- 阈值线 -->
              <div :style="{
                position: 'absolute',
                left: (noiseThreshold * 100) + '%',
                top: 0,
                bottom: 0,
                width: '2px',
                background: '#6366f1'
              }"></div>
            </div>
          </div>

          <!-- 频谱可视化 -->
          <div style="display:flex;align-items:end;justify-content:center;gap:3px;height:80px;margin:16px 0;">
            <div v-for="(bar, i) in noiseBars" :key="i" :style="{
              width: '8px',
              height: Math.max(4, bar * 80) + 'px',
              borderRadius: '4px',
              transition: 'height 0.08s',
              background: bar > 0.7 ? '#ef4444' : bar > 0.4 ? '#f59e0b' : '#10b981'
            }"></div>
          </div>

          <!-- 状态提示 -->
          <div style="font-size:18px;font-weight:700;padding:8px 0;" :style="{color: noiseLevel > noiseThreshold ? '#ef4444' : '#10b981'}">
            {{ noiseLevel > noiseThreshold ? '🤫 安静！太吵了！' : '✅ 很好，保持安静' }}
          </div>

          <!-- 阈值设置 -->
          <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-top:12px;">
            <span style="font-size:13px;color:#64748b;">提醒阈值：</span>
            <el-slider v-model="noiseThresholdDisplay" :min="10" :max="90" :step="5" style="width:160px;"
              @change="v => noiseThreshold = v / 100" />
            <span style="font-size:13px;color:#64748b;">{{ noiseThresholdDisplay }}%</span>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button v-if="noiseStatus !== 'running'" type="primary" @click="startNoise">▶ 开始检测</el-button>
        <el-button v-if="noiseStatus === 'running'" type="danger" @click="stopNoise">⏹ 停止</el-button>
      </template>
    </el-dialog>

    <!-- ========== ⏳ 秒表 ========== -->
    <el-dialog v-model="showStopwatch" title="⏳ 秒表" :close-on-click-modal="false">
      <div class="stopwatch-display">{{ stopwatchDisplay }}</div>
      <div v-if="stopwatchLaps.length" style="margin:12px 0;max-height:200px;overflow-y:auto;">
        <div v-for="(lap, i) in stopwatchLaps" :key="i" style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f1f5f9;font-size:14px;">
          <span style="color:#64748b;">第{{ stopwatchLaps.length - i }}圈</span>
          <span style="font-variant-numeric:tabular-nums;">{{ lap }}</span>
        </div>
      </div>
      <template #footer>
        <el-button v-if="!stopwatchRunning" type="primary" @click="startStopwatch">▶ 开始</el-button>
        <el-button v-else type="warning" @click="pauseStopwatch">⏸ 暂停</el-button>
        <el-button v-if="stopwatchRunning" @click="lapStopwatch">📍 计圈</el-button>
        <el-button @click="resetStopwatch">🔄 重置</el-button>
      </template>
    </el-dialog>

    <!-- ========== 🚦 红绿灯 ========== -->
    <el-dialog v-model="showTraffic" title="🚦 红绿灯" :close-on-click-modal="false" width="340px">
      <div style="display:flex;justify-content:center;padding:20px 0;">
        <div class="traffic-pole">
          <div class="traffic-light red" :class="{active: trafficLight === 'red'}" @click="trafficLight = 'red'">
            🔴
          </div>
          <div class="traffic-light yellow" :class="{active: trafficLight === 'yellow'}" @click="trafficLight = 'yellow'">
            🟡
          </div>
          <div class="traffic-light green" :class="{active: trafficLight === 'green'}" @click="trafficLight = 'green'">
            🟢
          </div>
        </div>
      </div>
      <div style="text-align:center;font-size:18px;font-weight:700;margin-top:8px;">
        <span v-if="trafficLight === 'red'" style="color:#ef4444;">🚫 全班安静！</span>
        <span v-else-if="trafficLight === 'yellow'" style="color:#f59e0b;">⚠️ 注意！</span>
        <span v-else style="color:#10b981;">✅ 自由活动</span>
      </div>
      <template #footer>
        <div style="display:flex;justify-content:center;gap:12px;">
          <el-button :type="trafficLight==='red'?'danger':''" @click="trafficLight='red'">🔴 安静</el-button>
          <el-button :type="trafficLight==='yellow'?'warning':''" @click="trafficLight='yellow'">🟡 注意</el-button>
          <el-button :type="trafficLight==='green'?'success':''" @click="trafficLight='green'">🟢 自由</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- ========== 🔢 随机数 ========== -->
    <el-dialog v-model="showRandomNum" title="🔢 随机数" :close-on-click-modal="false" width="380px">
      <el-form label-width="80px">
        <el-form-item label="最小值">
          <el-input-number v-model="randomNumMin" :min="-9999" :max="9999" />
        </el-form-item>
        <el-form-item label="最大值">
          <el-input-number v-model="randomNumMax" :min="-9999" :max="9999" />
        </el-form-item>
        <el-form-item label="个数">
          <el-input-number v-model="randomNumCount" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="不重复">
          <el-switch v-model="randomNumUnique" />
        </el-form-item>
      </el-form>

      <div v-if="randomNumResults.length" style="text-align:center;margin:16px 0;">
        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:12px;">
          <div v-for="(num, i) in randomNumResults" :key="i"
            style="width:64px;height:64px;display:flex;align-items:center;justify-content:center;background:#6366f1;color:#fff;border-radius:12px;font-size:24px;font-weight:700;">
            {{ num }}
          </div>
        </div>
      </div>
      <div v-else style="text-align:center;color:#94a3b8;padding:20px 0;">设置范围后点击生成</div>

      <template #footer>
        <el-button type="primary" size="large" @click="generateRandomNum">🎲 生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch } from 'vue'
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
  { id: 'dice', icon: '🎲', name: '骰子', desc: '掷骰子，支持多颗同时掷' },
  { id: 'noise', icon: '🔇', name: '噪音检测', desc: '实时检测环境音量，维持纪律' },
  { id: 'stopwatch', icon: '⏳', name: '秒表', desc: '正计时，可记录分圈' },
  { id: 'traffic', icon: '🚦', name: '红绿灯', desc: '纪律信号灯，全班安静' },
  { id: 'randomNum', icon: '🔢', name: '随机数', desc: '自定义范围，生成随机数字' },
]

// ========== 随机点名 ==========
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

// ========== 计时器 ==========
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

// ========== 随机分组 ==========
const showGroup = ref(false)
const groupCount = ref(3)
const groups = ref([])

async function doGroup() {
  const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } })
  const list = [...res.data].sort(() => Math.random() - 0.5)
  groups.value = Array.from({ length: groupCount.value }, () => [])
  list.forEach((s, i) => groups.value[i % groupCount.value].push(s))
}

// ========== 积分抽奖 ==========
const showLottery = ref(false)
const lotteryResult = ref(null)
const lotteryRunning = ref(false)
const lotteryCost = ref(10)
const lotteryStudents = ref([])
const lotterySpinning = ref(false)
const showPrizeEdit = ref(false)

const defaultPrizes = [
  { name: '🥇 一等奖', text: '积分 ×3', color: '#f59e0b', weight: 5 },
  { name: '🥈 二等奖', text: '积分 ×2', color: '#6366f1', weight: 15 },
  { name: '🥉 三等奖', text: '积分 ×1', color: '#10b981', weight: 30 },
  { name: '🎁 参与奖', text: '积分不变', color: '#94a3b8', weight: 50 },
]

const lotteryPrizes = ref(JSON.parse(localStorage.getItem('lottery_prizes') || 'null') || defaultPrizes)

function savePrizes() {
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

// ========== 积分兑换 ==========
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
    await api.post('/api/students/points/adjust', {
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

// ========== 积分阈值提醒 ==========
const showThreshold = ref(false)
const thresholdPoints = ref(parseInt(localStorage.getItem('threshold_points') || '100'))
const thresholdAuto = ref(localStorage.getItem('threshold_auto') !== 'false')
const thresholdStudents = ref([])
const thresholdChecked = ref(false)

watch(thresholdPoints, (v) => { localStorage.setItem('threshold_points', String(v)) })
watch(thresholdAuto, (v) => { localStorage.setItem('threshold_auto', String(v)) })

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

      const pointsMap = { '积分 ×3': lotteryCost.value * 2, '积分 ×2': lotteryCost.value, '积分 ×1': 0, '积分不变': -lotteryCost.value }
      const delta = pointsMap[prize.text] ?? 0
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
          points: -lotteryCost.value,
          reason: '抽奖参与奖',
          category: 'lottery'
        }).catch(() => {})
      }
      loadLotteryStudents()
    }
  }, 80)
}

function openTool(id) {
  if (id === 'random') { randomResult.value = null; showRandom.value = true }
  else if (id === 'timer') { resetTimer(); showTimer.value = true }
  else if (id === 'group') { groups.value = []; showGroup.value = true }
  else if (id === 'lottery') { lotteryResult.value = null; lotteryRunning.value = false; showLottery.value = true; loadLotteryStudents() }
  else if (id === 'exchange') { showExchange.value = true; loadExchangeStudents() }
  else if (id === 'threshold') { showThreshold.value = true; loadThresholdStudents() }
  else if (id === 'dice') { diceResult.value = null; showDice.value = true }
  else if (id === 'noise') { showNoise.value = true }
  else if (id === 'stopwatch') { showStopwatch.value = true }
  else if (id === 'traffic') { trafficLight.value = 'red'; showTraffic.value = true }
  else if (id === 'randomNum') { randomNumResults.value = []; showRandomNum.value = true }
}

// ========== 🎲 骰子 ==========
const showDice = ref(false)
const diceCount = ref(1)
const diceResult = ref(null)
const diceDisplay = ref(1)
const diceRolling = ref(false)
let diceTimer = null

const DICE_PIPS = {
  1: [[50,50]],
  2: [[30,30],[70,70]],
  3: [[30,30],[50,50],[70,70]],
  4: [[30,30],[70,30],[30,70],[70,70]],
  5: [[30,30],[70,30],[50,50],[30,70],[70,70]],
  6: [[30,26],[70,26],[30,50],[70,50],[30,74],[70,74]]
}
function dicePipPositions(v) { return DICE_PIPS[Math.max(1, Math.min(6, v))] || DICE_PIPS[1] }

function rollDice() {
  if (diceRolling.value) return
  diceRolling.value = true
  diceResult.value = null
  let count = 0
  const total = 900
  const tick = () => {
    const elapsed = count * 50
    diceDisplay.value = Math.floor(Math.random() * 6) + 1
    count++
    if (elapsed >= total) {
      // 多颗骰子显示总点数
      let sum = 0
      for (let i = 0; i < diceCount.value; i++) sum += Math.floor(Math.random() * 6) + 1
      diceResult.value = sum
      diceRolling.value = false
      return
    }
    diceTimer = setTimeout(tick, 50 + Math.pow(elapsed / total, 2.2) * 160)
  }
  tick()
}
onUnmounted(() => clearTimeout(diceTimer))

// ========== 🔇 噪音检测 ==========
const showNoise = ref(false)
const noiseStatus = ref('idle') // idle, requesting, running, denied, error
const noiseLevel = ref(0)
const noiseBars = ref(Array(16).fill(0))
const noiseThreshold = ref(0.5)
const noiseThresholdDisplay = ref(50)
let noiseCleanup = null

async function startNoise() {
  if (noiseStatus.value === 'running') return
  noiseStatus.value = 'requesting'
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    if (!AudioCtx) { noiseStatus.value = 'error'; return }
    const ctx = new AudioCtx()
    const src = ctx.createMediaStreamSource(stream)
    const analyser = ctx.createAnalyser()
    analyser.fftSize = 512
    analyser.smoothingTimeConstant = 0.7
    src.connect(analyser)

    const timeBuf = new Uint8Array(analyser.fftSize)
    const freqBuf = new Uint8Array(analyser.frequencyBinCount)
    const usefulBins = Math.floor(analyser.frequencyBinCount * 0.55)
    const binsPerBar = Math.max(1, Math.floor(usefulBins / 16))

    noiseStatus.value = 'running'
    let raf = 0
    const tick = () => {
      analyser.getByteTimeDomainData(timeBuf)
      let sum = 0
      for (let i = 0; i < timeBuf.length; i++) {
        const v = (timeBuf[i] - 128) / 128
        sum += v * v
      }
      noiseLevel.value = Math.min(1, Math.sqrt(sum / timeBuf.length) * 1.6)

      analyser.getByteFrequencyData(freqBuf)
      const next = []
      for (let b = 0; b < 16; b++) {
        const start = b * binsPerBar
        const end = Math.min(usefulBins, start + binsPerBar)
        let bsum = 0
        for (let i = start; i < end; i++) bsum += freqBuf[i]
        next.push(Math.min(1, bsum / (end - start) / 255 * 1.4))
      }
      noiseBars.value = next
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)

    noiseCleanup = () => {
      cancelAnimationFrame(raf)
      stream.getTracks().forEach(t => t.stop())
      ctx.close()
    }
  } catch (e) {
    if (e.name === 'NotAllowedError' || e.name === 'PermissionDeniedError') {
      noiseStatus.value = 'denied'
    } else {
      noiseStatus.value = 'error'
    }
  }
}

function stopNoise() {
  if (noiseCleanup) { noiseCleanup(); noiseCleanup = null }
  noiseStatus.value = 'idle'
  noiseLevel.value = 0
  noiseBars.value = Array(16).fill(0)
}

onUnmounted(() => { if (noiseCleanup) noiseCleanup() })

// ========== ⏳ 秒表 ==========
const showStopwatch = ref(false)
const stopwatchRunning = ref(false)
const stopwatchElapsed = ref(0)
const stopwatchLaps = ref([])
let stopwatchInterval = null
let stopwatchStart = 0

const stopwatchDisplay = computed(() => {
  const totalMs = stopwatchElapsed.value
  const m = Math.floor(totalMs / 60000)
  const s = Math.floor((totalMs % 60000) / 1000)
  const ms = Math.floor((totalMs % 1000) / 10)
  return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}.${String(ms).padStart(2,'0')}`
})

function startStopwatch() {
  stopwatchStart = Date.now() - stopwatchElapsed.value
  stopwatchRunning.value = true
  stopwatchInterval = setInterval(() => {
    stopwatchElapsed.value = Date.now() - stopwatchStart
  }, 10)
}
function pauseStopwatch() {
  clearInterval(stopwatchInterval)
  stopwatchRunning.value = false
}
function lapStopwatch() {
  stopwatchLaps.value.unshift(stopwatchDisplay.value)
}
function resetStopwatch() {
  clearInterval(stopwatchInterval)
  stopwatchRunning.value = false
  stopwatchElapsed.value = 0
  stopwatchLaps.value = []
}
onUnmounted(() => clearInterval(stopwatchInterval))

// ========== 🚦 红绿灯 ==========
const showTraffic = ref(false)
const trafficLight = ref('red')

// ========== 🔢 随机数 ==========
const showRandomNum = ref(false)
const randomNumMin = ref(1)
const randomNumMax = ref(100)
const randomNumCount = ref(1)
const randomNumUnique = ref(false)
const randomNumResults = ref([])

function generateRandomNum() {
  const min = Math.min(randomNumMin.value, randomNumMax.value)
  const max = Math.max(randomNumMin.value, randomNumMax.value)
  const count = Math.min(randomNumCount.value, max - min + 1)

  if (randomNumUnique.value) {
    const pool = []
    for (let i = min; i <= max; i++) pool.push(i)
    // Fisher-Yates shuffle
    for (let i = pool.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [pool[i], pool[j]] = [pool[j], pool[i]]
    }
    randomNumResults.value = pool.slice(0, count)
  } else {
    randomNumResults.value = Array.from({ length: count }, () =>
      Math.floor(Math.random() * (max - min + 1)) + min
    )
  }
}
</script>

<style scoped>
.tools-page { width: 100%; }
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

/* 秒表 */
.stopwatch-display {
  font-size: 56px;
  font-weight: 700;
  text-align: center;
  color: #6366f1;
  font-variant-numeric: tabular-nums;
  padding: 20px 0;
  letter-spacing: 2px;
}

/* 骰子 */
.dice-rolling { animation: diceShake 0.1s infinite alternate; }
@keyframes diceShake {
  from { transform: rotate(-5deg) scale(1.05); }
  to { transform: rotate(5deg) scale(0.95); }
}
.dice-result { animation: dicePop 0.3s ease-out; }
@keyframes dicePop {
  from { transform: scale(0.5); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

/* 红绿灯 */
.traffic-pole {
  background: #1e293b;
  border-radius: 24px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.traffic-light {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  cursor: pointer;
  transition: all 0.3s;
  opacity: 0.3;
  filter: grayscale(1);
}
.traffic-light.active {
  opacity: 1;
  filter: grayscale(0);
  transform: scale(1.1);
}
.traffic-light.red.active { box-shadow: 0 0 30px rgba(239,68,68,0.6); }
.traffic-light.yellow.active { box-shadow: 0 0 30px rgba(245,158,11,0.6); }
.traffic-light.green.active { box-shadow: 0 0 30px rgba(16,185,129,0.6); }

@media (max-width: 767px) {
  .tool-card :deep(.el-card__body) { padding: 14px 8px; }
  .tool-icon { font-size: 32px; }
  .tool-card h3 { font-size: 13px; }
  .tool-card p { font-size: 12px; }
  .random-name { font-size: 20px; }
  .timer-display { font-size: 44px; }
  .stopwatch-display { font-size: 40px; }
}
</style>
