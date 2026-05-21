<template>
  <el-dialog v-model="visible" title="⏱️ 计时器" :close-on-click-modal="false" @close="$emit('update:modelValue', false)">
    <div class="timer-display">{{ display }}</div>
    <div class="timer-presets">
      <el-button @click="set(60)">1分钟</el-button>
      <el-button @click="set(180)">3分钟</el-button>
      <el-button @click="set(300)">5分钟</el-button>
    </div>
    <template #footer>
      <el-button @click="toggle">{{ running ? '⏸ 暂停' : '▶ 开始' }}</el-button>
      <el-button @click="reset">🔄 重置</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])

const visible = ref(props.modelValue)
const seconds = ref(60)
const running = ref(false)
let interval = null

watch(() => props.modelValue, v => { visible.value = v; if (v) reset() })
watch(visible, v => emit('update:modelValue', v))

const display = computed(() => {
  const m = Math.floor(seconds.value / 60)
  const s = seconds.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

function set(sec) { seconds.value = sec; running.value = false; clearInterval(interval) }
function toggle() {
  if (running.value) { clearInterval(interval); running.value = false }
  else {
    running.value = true
    interval = setInterval(() => {
      if (seconds.value <= 0) { clearInterval(interval); running.value = false; return }
      seconds.value--
    }, 1000)
  }
}
function reset() { clearInterval(interval); seconds.value = 60; running.value = false }
onUnmounted(() => clearInterval(interval))
</script>

<style scoped>
.timer-display {
  font-size: 56px; font-weight: 700; text-align: center;
  color: #6366f1; font-variant-numeric: tabular-nums; padding: 20px 0;
}
.timer-presets { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }
</style>
