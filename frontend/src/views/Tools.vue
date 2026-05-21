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

    <!-- 工具组件 -->
    <RandomPick v-model="showRandom" />
    <TimerTool v-model="showTimer" />
    <RandomGroup v-model="showGroup" />
    <LotteryTool v-model="showLottery" />
    <ExchangeTool v-model="showExchange" />
    <ThresholdTool v-model="showThreshold" />
    <DiceTool v-model="showDice" />
    <NoiseDetector v-model="showNoise" />
    <StopwatchTool v-model="showStopwatch" />
    <TrafficLight v-model="showTraffic" />
    <RandomNum v-model="showRandomNum" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import RandomPick from '../components/tools/RandomPick.vue'
import TimerTool from '../components/tools/TimerTool.vue'
import RandomGroup from '../components/tools/RandomGroup.vue'
import LotteryTool from '../components/tools/LotteryTool.vue'
import ExchangeTool from '../components/tools/ExchangeTool.vue'
import ThresholdTool from '../components/tools/ThresholdTool.vue'
import DiceTool from '../components/tools/DiceTool.vue'
import NoiseDetector from '../components/tools/NoiseDetector.vue'
import StopwatchTool from '../components/tools/StopwatchTool.vue'
import TrafficLight from '../components/tools/TrafficLight.vue'
import RandomNum from '../components/tools/RandomNum.vue'

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

const showRandom = ref(false)
const showTimer = ref(false)
const showGroup = ref(false)
const showLottery = ref(false)
const showExchange = ref(false)
const showThreshold = ref(false)
const showDice = ref(false)
const showNoise = ref(false)
const showStopwatch = ref(false)
const showTraffic = ref(false)
const showRandomNum = ref(false)

function openTool(id) {
  const map = {
    random: showRandom, timer: showTimer, group: showGroup,
    lottery: showLottery, exchange: showExchange, threshold: showThreshold,
    dice: showDice, noise: showNoise, stopwatch: showStopwatch,
    traffic: showTraffic, randomNum: showRandomNum,
  }
  const ref_ = map[id]
  if (ref_) ref_.value = true
}
</script>

<style scoped>
.tools-page { width: 100%; }
.page-header h1 { margin: 0 0 20px; font-size: 22px; }

.tool-card {
  text-align: center; cursor: pointer; border-radius: 16px;
  transition: transform 0.2s; margin-bottom: 16px;
}
.tool-card:hover { transform: translateY(-4px); }
.tool-card :deep(.el-card__body) { padding: 20px 12px; }
.tool-icon { font-size: 40px; margin-bottom: 8px; }
.tool-card h3 { margin: 0 0 4px; font-size: 15px; }
.tool-card p { color: #94a3b8; font-size: 13px; margin: 0; }

@media (max-width: 767px) {
  .tool-card :deep(.el-card__body) { padding: 14px 8px; }
  .tool-icon { font-size: 32px; }
  .tool-card h3 { font-size: 13px; }
  .tool-card p { font-size: 12px; }
}
</style>
