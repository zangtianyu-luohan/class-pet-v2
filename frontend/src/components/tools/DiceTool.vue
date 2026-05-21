<template>
  <!-- Dialog 模式 -->
  <el-dialog v-if="mode === 'dialog'" v-model="visible" title="🎲 骰子" :close-on-click-modal="false" width="400px" @close="$emit('update:modelValue', false)">
    <div style="text-align:center;padding:20px 0;">
      <div v-if="rolling" class="dice-rolling">
        <svg viewBox="0 0 100 100" width="120" height="120">
          <rect x="7" y="7" width="86" height="86" rx="11" fill="white" stroke="#6366f1" stroke-width="4"/>
          <template v-for="(pos, i) in pips(displayVal)" :key="i">
            <circle :cx="pos[0]" :cy="pos[1]" r="7" fill="#6366f1"/>
          </template>
        </svg>
      </div>
      <div v-else-if="result !== null" class="dice-result">
        <svg viewBox="0 0 100 100" width="120" height="120">
          <rect x="7" y="7" width="86" height="86" rx="11" fill="white" stroke="#10b981" stroke-width="4"/>
          <template v-for="(pos, i) in pips(Math.min(6, result))" :key="i">
            <circle :cx="pos[0]" :cy="pos[1]" r="7" fill="#10b981"/>
          </template>
        </svg>
        <div style="font-size:24px;font-weight:700;color:#10b981;margin-top:12px;">{{ result }} 点</div>
      </div>
      <div v-else style="color:#94a3b8;font-size:16px;">点击掷骰子</div>
    </div>
    <div style="display:flex;justify-content:center;gap:12px;margin-bottom:12px;">
      <span style="font-size:14px;line-height:32px;">骰子数：</span>
      <el-input-number v-model="count" :min="1" :max="6" size="small" />
    </div>
    <template #footer>
      <el-button type="primary" size="large" @click="roll" :disabled="rolling">🎲 掷骰子</el-button>
    </template>
  </el-dialog>

  <!-- Card 模式 -->
  <div v-else class="dice-card">
    <div class="card-header"><h3>🎲 骰子</h3></div>
    <div class="card-body">
      <div style="text-align:center;padding:10px 0;">
        <div v-if="rolling" class="dice-rolling">
          <svg viewBox="0 0 100 100" width="100" height="100">
            <rect x="7" y="7" width="86" height="86" rx="11" fill="white" stroke="#6366f1" stroke-width="4"/>
            <template v-for="(pos, i) in pips(displayVal)" :key="i">
              <circle :cx="pos[0]" :cy="pos[1]" r="7" fill="#6366f1"/>
            </template>
          </svg>
        </div>
        <div v-else-if="result !== null" class="dice-result">
          <svg viewBox="0 0 100 100" width="100" height="100">
            <rect x="7" y="7" width="86" height="86" rx="11" fill="white" stroke="#10b981" stroke-width="4"/>
            <template v-for="(pos, i) in pips(Math.min(6, result))" :key="i">
              <circle :cx="pos[0]" :cy="pos[1]" r="7" fill="#10b981"/>
            </template>
          </svg>
          <div style="font-size:20px;font-weight:700;color:#10b981;margin-top:8px;">{{ result }} 点</div>
        </div>
        <div v-else style="color:#94a3b8;font-size:14px;">点击掷骰子</div>
      </div>
      <div style="display:flex;justify-content:center;gap:8px;align-items:center;">
        <span style="font-size:13px;color:#94a3b8;">骰子数：</span>
        <el-input-number v-model="count" :min="1" :max="6" size="small" />
      </div>
      <div style="text-align:center;margin-top:12px;">
        <el-button type="primary" @click="roll" :disabled="rolling">🎲 掷骰子</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  mode: { type: String, default: 'dialog' }
})
const emit = defineEmits(['update:modelValue'])

const visible = ref(props.modelValue)
const count = ref(1)
const result = ref(null)
const displayVal = ref(1)
const rolling = ref(false)
let timer = null

watch(() => props.modelValue, v => { visible.value = v; if (v) { result.value = null; rolling.value = false } })
watch(visible, v => emit('update:modelValue', v))

const PIPS = {
  1: [[50,50]], 2: [[30,30],[70,70]], 3: [[30,30],[50,50],[70,70]],
  4: [[30,30],[70,30],[30,70],[70,70]], 5: [[30,30],[70,30],[50,50],[30,70],[70,70]],
  6: [[30,26],[70,26],[30,50],[70,50],[30,74],[70,74]]
}
function pips(v) { return PIPS[Math.max(1, Math.min(6, v))] || PIPS[1] }

function roll() {
  if (rolling.value) return
  rolling.value = true
  result.value = null
  let c = 0
  const total = 900
  const tick = () => {
    const elapsed = c * 50
    displayVal.value = Math.floor(Math.random() * 6) + 1
    c++
    if (elapsed >= total) {
      let sum = 0
      for (let i = 0; i < count.value; i++) sum += Math.floor(Math.random() * 6) + 1
      result.value = sum
      rolling.value = false
      return
    }
    timer = setTimeout(tick, 50 + Math.pow(elapsed / total, 2.2) * 160)
  }
  tick()
}
onUnmounted(() => clearTimeout(timer))
</script>

<style scoped>
.dice-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px; padding: 20px; height: 100%;
  display: flex; flex-direction: column;
}
.card-header { margin-bottom: 12px; }
.card-header h3 { margin: 0; font-size: 18px; color: #fff; }
.card-body { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.dice-rolling { animation: diceShake 0.1s infinite alternate; display: inline-block; }
@keyframes diceShake { from { transform: rotate(-5deg) scale(1.05); } to { transform: rotate(5deg) scale(0.95); } }
.dice-result { animation: dicePop 0.3s ease-out; display: inline-block; }
@keyframes dicePop { from { transform: scale(0.5); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>
