<template>
  <!-- Dialog 模式 -->
  <el-dialog v-if="mode === 'dialog'" v-model="visible" title="🔇 噪音检测" :close-on-click-modal="false" width="420px" @close="stopNoise(); $emit('update:modelValue', false)">
    <div style="text-align:center;padding:10px 0;">
      <div v-if="status === 'idle'" style="color:#94a3b8;padding:30px 0;">点击开始检测环境噪音</div>
      <div v-else-if="status === 'requesting'" style="color:#f59e0b;padding:30px 0;">正在请求麦克风权限...</div>
      <div v-else-if="status === 'denied'" style="color:#ef4444;padding:30px 0;">麦克风权限被拒绝<br>请在浏览器设置中允许</div>
      <div v-else-if="status === 'error'" style="color:#ef4444;padding:30px 0;">无法访问麦克风</div>
      <div v-else>
        <div style="margin-bottom:16px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span style="font-size:13px;color:#64748b;">当前音量</span>
            <span style="font-size:13px;font-weight:600;" :style="{color: level > threshold ? '#ef4444' : '#10b981'}">{{ Math.round(level * 100) }}%</span>
          </div>
          <div style="height:24px;background:#f1f5f9;border-radius:12px;overflow:hidden;position:relative;">
            <div :style="{ width: Math.min(100, level * 100) + '%', height: '100%', borderRadius: '12px', transition: 'width 0.1s, background 0.3s', background: level > threshold ? 'linear-gradient(90deg, #f59e0b, #ef4444)' : 'linear-gradient(90deg, #10b981, #34d399)' }"></div>
            <div :style="{ position: 'absolute', left: (threshold * 100) + '%', top: 0, bottom: 0, width: '2px', background: '#6366f1' }"></div>
          </div>
        </div>
        <div style="display:flex;align-items:end;justify-content:center;gap:3px;height:80px;margin:16px 0;">
          <div v-for="(bar, i) in bars" :key="i" :style="{ width: '8px', height: Math.max(4, bar * 80) + 'px', borderRadius: '4px', transition: 'height 0.08s', background: bar > 0.7 ? '#ef4444' : bar > 0.4 ? '#f59e0b' : '#10b981' }"></div>
        </div>
        <div style="font-size:18px;font-weight:700;padding:8px 0;" :style="{color: level > threshold ? '#ef4444' : '#10b981'}">
          {{ level > threshold ? '🤫 安静！太吵了！' : '✅ 很好，保持安静' }}
        </div>
        <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-top:12px;">
          <span style="font-size:13px;color:#64748b;">提醒阈值：</span>
          <el-slider v-model="thresholdDisplay" :min="10" :max="90" :step="5" style="width:160px;" @change="v => threshold = v / 100" />
          <span style="font-size:13px;color:#64748b;">{{ thresholdDisplay }}%</span>
        </div>
      </div>
    </div>
    <template #footer>
      <el-button v-if="status !== 'running'" type="primary" @click="startNoise">▶ 开始检测</el-button>
      <el-button v-if="status === 'running'" type="danger" @click="stopNoise">⏹ 停止</el-button>
    </template>
  </el-dialog>

  <!-- Card 模式 -->
  <div v-else class="noise-card">
    <div class="card-header"><h3>🔇 噪音检测</h3></div>
    <div class="card-body">
      <div v-if="status === 'idle'" style="text-align:center;color:#94a3b8;padding:10px 0;">
        <div style="font-size:13px;margin-bottom:12px;">点击开始检测环境噪音</div>
        <el-button type="primary" @click="startNoise">▶ 开始检测</el-button>
      </div>
      <div v-else-if="status === 'requesting'" style="text-align:center;color:#f59e0b;padding:20px 0;">正在请求麦克风权限...</div>
      <div v-else-if="status === 'denied'" style="text-align:center;color:#ef4444;padding:20px 0;font-size:13px;">麦克风权限被拒绝<br>请在浏览器设置中允许</div>
      <div v-else-if="status === 'error'" style="text-align:center;color:#ef4444;padding:20px 0;">无法访问麦克风</div>
      <div v-else>
        <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
          <span style="font-size:12px;color:#64748b;">当前音量</span>
          <span style="font-size:12px;font-weight:600;" :style="{color: level > threshold ? '#ef4444' : '#10b981'}">{{ Math.round(level * 100) }}%</span>
        </div>
        <div style="height:20px;background:rgba(255,255,255,0.1);border-radius:10px;overflow:hidden;position:relative;">
          <div :style="{ width: Math.min(100, level * 100) + '%', height: '100%', borderRadius: '10px', transition: 'width 0.1s, background 0.3s', background: level > threshold ? 'linear-gradient(90deg, #f59e0b, #ef4444)' : 'linear-gradient(90deg, #10b981, #34d399)' }"></div>
          <div :style="{ position: 'absolute', left: (threshold * 100) + '%', top: 0, bottom: 0, width: '2px', background: '#6366f1' }"></div>
        </div>
        <div style="display:flex;align-items:end;justify-content:center;gap:2px;height:60px;margin:10px 0;">
          <div v-for="(bar, i) in bars" :key="i" :style="{ width: '6px', height: Math.max(3, bar * 60) + 'px', borderRadius: '3px', transition: 'height 0.08s', background: bar > 0.7 ? '#ef4444' : bar > 0.4 ? '#f59e0b' : '#10b981' }"></div>
        </div>
        <div style="text-align:center;font-size:14px;font-weight:700;" :style="{color: level > threshold ? '#ef4444' : '#10b981'}">
          {{ level > threshold ? '🤫 安静！太吵了！' : '✅ 很好，保持安静' }}
        </div>
        <div style="display:flex;align-items:center;justify-content:center;gap:6px;margin-top:8px;">
          <span style="font-size:12px;color:#64748b;">阈值：</span>
          <el-slider v-model="thresholdDisplay" :min="10" :max="90" :step="5" style="width:100px;" @change="v => threshold = v / 100" />
          <span style="font-size:12px;color:#64748b;">{{ thresholdDisplay }}%</span>
        </div>
        <div style="text-align:center;margin-top:8px;">
          <el-button type="danger" size="small" @click="stopNoise">⏹ 停止</el-button>
        </div>
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
const status = ref('idle')
const level = ref(0)
const bars = ref(Array(16).fill(0))
const threshold = ref(0.5)
const thresholdDisplay = ref(50)
let cleanup = null

watch(() => props.modelValue, v => { visible.value = v; if (!v) stopNoise() })
watch(visible, v => { emit('update:modelValue', v); if (!v) stopNoise() })

async function startNoise() {
  if (status.value === 'running') return
  status.value = 'requesting'
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const AudioCtx = window.AudioContext || window.webkitAudioContext
    if (!AudioCtx) { status.value = 'error'; return }
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

    status.value = 'running'
    let raf = 0
    const tick = () => {
      analyser.getByteTimeDomainData(timeBuf)
      let sum = 0
      for (let i = 0; i < timeBuf.length; i++) { const v = (timeBuf[i] - 128) / 128; sum += v * v }
      level.value = Math.min(1, Math.sqrt(sum / timeBuf.length) * 1.6)

      analyser.getByteFrequencyData(freqBuf)
      const next = []
      for (let b = 0; b < 16; b++) {
        const start = b * binsPerBar
        const end = Math.min(usefulBins, start + binsPerBar)
        let bsum = 0
        for (let i = start; i < end; i++) bsum += freqBuf[i]
        next.push(Math.min(1, bsum / (end - start) / 255 * 1.4))
      }
      bars.value = next
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    cleanup = () => { cancelAnimationFrame(raf); stream.getTracks().forEach(t => t.stop()); ctx.close() }
  } catch (e) {
    status.value = (e.name === 'NotAllowedError' || e.name === 'PermissionDeniedError') ? 'denied' : 'error'
  }
}

function stopNoise() {
  if (cleanup) { cleanup(); cleanup = null }
  status.value = 'idle'
  level.value = 0
  bars.value = Array(16).fill(0)
}

onUnmounted(() => { if (cleanup) cleanup() })
</script>

<style scoped>
.noise-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px; padding: 20px; height: 100%;
  display: flex; flex-direction: column;
}
.card-header { margin-bottom: 12px; }
.card-header h3 { margin: 0; font-size: 18px; color: #fff; }
.card-body { flex: 1; display: flex; flex-direction: column; justify-content: center; }
</style>
