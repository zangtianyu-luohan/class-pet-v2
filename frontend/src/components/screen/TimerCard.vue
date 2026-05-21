<template>
  <div class="timer-card">
    <div class="card-header">
      <h3>⏱️ 课堂计时</h3>
    </div>
    <div class="card-body">
      <div class="timer-display">
        {{ formatTime(elapsed) }}
      </div>
      <div class="timer-controls">
        <el-button
          v-if="!isRunning"
          type="primary"
          @click="start"
        >
          开始
        </el-button>
        <el-button
          v-else
          type="warning"
          @click="pause"
        >
          暂停
        </el-button>
        <el-button @click="reset">
          重置
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

const elapsed = ref(0)
const isRunning = ref(false)
let timer = null

function formatTime(seconds) {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hrs > 0) {
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

function start() {
  if (isRunning.value) return

  isRunning.value = true
  timer = setInterval(() => {
    elapsed.value++
  }, 1000)
}

function pause() {
  isRunning.value = false
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function reset() {
  pause()
  elapsed.value = 0
}

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})

defineExpose({ start, pause, reset })
</script>

<style scoped>
.timer-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #fff;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.timer-display {
  font-size: 48px;
  font-weight: 700;
  color: #fff;
  font-variant-numeric: tabular-nums;
  margin-bottom: 24px;
}

.timer-controls {
  display: flex;
  gap: 12px;
}
</style>
