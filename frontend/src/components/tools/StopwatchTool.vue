<template>
  <!-- Dialog 模式 -->
  <el-dialog v-if="mode === 'dialog'" v-model="visible" title="⏳ 秒表" :close-on-click-modal="false" @close="$emit('update:modelValue', false)">
    <div class="stopwatch-display">{{ display }}</div>
    <div v-if="laps.length" style="margin:12px 0;max-height:200px;overflow-y:auto;">
      <div v-for="(lap, i) in laps" :key="i" style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #f1f5f9;font-size:14px;">
        <span style="color:#64748b;">第{{ laps.length - i }}圈</span>
        <span style="font-variant-numeric:tabular-nums;">{{ lap }}</span>
      </div>
    </div>
    <template #footer>
      <el-button v-if="!running" type="primary" @click="start">▶ 开始</el-button>
      <el-button v-else type="warning" @click="pause">⏸ 暂停</el-button>
      <el-button v-if="running" @click="lap">📍 计圈</el-button>
      <el-button @click="reset">🔄 重置</el-button>
    </template>
  </el-dialog>

  <!-- Card 模式 -->
  <div v-else class="stopwatch-card">
    <div class="card-header"><h3>⏱️ 秒表</h3></div>
    <div class="card-body">
      <div class="stopwatch-display stopwatch-display--card">{{ display }}</div>
      <div v-if="laps.length" class="laps-list">
        <div v-for="(lap, i) in laps" :key="i" class="lap-item">
          <span style="color:#64748b;">第{{ laps.length - i }}圈</span>
          <span style="font-variant-numeric:tabular-nums;">{{ lap }}</span>
        </div>
      </div>
      <div style="display:flex;justify-content:center;gap:8px;margin-top:12px;">
        <el-button v-if="!running" type="primary" @click="start">▶ 开始</el-button>
        <el-button v-else type="warning" @click="pause">⏸ 暂停</el-button>
        <el-button v-if="running" @click="lap">📍 计圈</el-button>
        <el-button @click="reset">🔄 重置</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  mode: { type: String, default: 'dialog' }
})
const emit = defineEmits(['update:modelValue'])

const visible = ref(props.modelValue)
const running = ref(false)
const elapsed = ref(0)
const laps = ref([])
let interval = null
let startTs = 0

watch(() => props.modelValue, v => { visible.value = v; if (v) reset() })
watch(visible, v => emit('update:modelValue', v))

const display = computed(() => {
  const ms = elapsed.value
  const m = Math.floor(ms / 60000)
  const s = Math.floor((ms % 60000) / 1000)
  const cs = Math.floor((ms % 1000) / 10)
  return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}.${String(cs).padStart(2,'0')}`
})

function start() {
  startTs = Date.now() - elapsed.value
  running.value = true
  interval = setInterval(() => { elapsed.value = Date.now() - startTs }, 10)
}
function pause() { clearInterval(interval); running.value = false }
function lap() { laps.value.unshift(display.value) }
function reset() { clearInterval(interval); running.value = false; elapsed.value = 0; laps.value = [] }
onUnmounted(() => clearInterval(interval))
</script>

<style scoped>
.stopwatch-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px; padding: 20px; height: 100%;
  display: flex; flex-direction: column;
}
.card-header { margin-bottom: 12px; }
.card-header h3 { margin: 0; font-size: 18px; color: #fff; }
.card-body { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.stopwatch-display {
  font-size: 56px; font-weight: 700; text-align: center;
  color: #6366f1; font-variant-numeric: tabular-nums; padding: 20px 0; letter-spacing: 2px;
}
.stopwatch-display--card {
  font-size: 48px; padding: 10px 0;
}
.laps-list {
  max-height: 120px; overflow-y: auto; margin: 8px 0;
}
.lap-item {
  display: flex; justify-content: space-between; padding: 4px 0;
  border-bottom: 1px solid rgba(255,255,255,0.1); font-size: 13px;
}
</style>
