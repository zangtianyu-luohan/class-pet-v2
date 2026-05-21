<template>
  <!-- Dialog 模式 -->
  <el-dialog v-if="mode === 'dialog'" v-model="visible" title="🚦 红绿灯" :close-on-click-modal="false" width="340px" @close="$emit('update:modelValue', false)">
    <div style="display:flex;justify-content:center;padding:20px 0;">
      <div class="traffic-pole">
        <div class="traffic-light red" :class="{active: light === 'red'}" @click="light = 'red'">🔴</div>
        <div class="traffic-light yellow" :class="{active: light === 'yellow'}" @click="light = 'yellow'">🟡</div>
        <div class="traffic-light green" :class="{active: light === 'green'}" @click="light = 'green'">🟢</div>
      </div>
    </div>
    <div style="text-align:center;font-size:18px;font-weight:700;margin-top:8px;">
      <span v-if="light === 'red'" style="color:#ef4444;">🚫 全班安静！</span>
      <span v-else-if="light === 'yellow'" style="color:#f59e0b;">⚠️ 注意！</span>
      <span v-else style="color:#10b981;">✅ 自由活动</span>
    </div>
    <template #footer>
      <div style="display:flex;justify-content:center;gap:12px;">
        <el-button :type="light==='red'?'danger':''" @click="light='red'">🔴 安静</el-button>
        <el-button :type="light==='yellow'?'warning':''" @click="light='yellow'">🟡 注意</el-button>
        <el-button :type="light==='green'?'success':''" @click="light='green'">🟢 自由</el-button>
      </div>
    </template>
  </el-dialog>

  <!-- Card 模式 -->
  <div v-else class="traffic-card">
    <div class="card-header"><h3>🚦 红绿灯</h3></div>
    <div class="card-body">
      <div style="display:flex;justify-content:center;padding:10px 0;">
        <div class="traffic-pole">
          <div class="traffic-light red" :class="{active: light === 'red'}" @click="light = 'red'">🔴</div>
          <div class="traffic-light yellow" :class="{active: light === 'yellow'}" @click="light = 'yellow'">🟡</div>
          <div class="traffic-light green" :class="{active: light === 'green'}" @click="light = 'green'">🟢</div>
        </div>
      </div>
      <div style="text-align:center;font-size:18px;font-weight:700;margin-top:8px;">
        <span v-if="light === 'red'" style="color:#ef4444;">🚫 全班安静！</span>
        <span v-else-if="light === 'yellow'" style="color:#f59e0b;">⚠️ 注意！</span>
        <span v-else style="color:#10b981;">✅ 自由活动</span>
      </div>
      <div style="display:flex;justify-content:center;gap:8px;margin-top:12px;">
        <el-button :type="light==='red'?'danger':''" size="small" @click="light='red'">🔴 安静</el-button>
        <el-button :type="light==='yellow'?'warning':''" size="small" @click="light='yellow'">🟡 注意</el-button>
        <el-button :type="light==='green'?'success':''" size="small" @click="light='green'">🟢 自由</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  mode: { type: String, default: 'dialog' }
})
const emit = defineEmits(['update:modelValue'])

const visible = ref(props.modelValue)
const light = ref('red')

watch(() => props.modelValue, v => { visible.value = v; if (v) light.value = 'red' })
watch(visible, v => emit('update:modelValue', v))
</script>

<style scoped>
.traffic-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px; padding: 20px; height: 100%;
  display: flex; flex-direction: column;
}
.card-header { margin-bottom: 12px; }
.card-header h3 { margin: 0; font-size: 18px; color: #fff; }
.card-body { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.traffic-pole { background: #1e293b; border-radius: 24px; padding: 12px; display: flex; flex-direction: column; gap: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
.traffic-light { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; cursor: pointer; transition: all 0.3s; opacity: 0.3; filter: grayscale(1); }
.traffic-light.active { opacity: 1; filter: grayscale(0); transform: scale(1.1); }
.traffic-light.red.active { box-shadow: 0 0 30px rgba(239,68,68,0.6); }
.traffic-light.yellow.active { box-shadow: 0 0 30px rgba(245,158,11,0.6); }
.traffic-light.green.active { box-shadow: 0 0 30px rgba(16,185,129,0.6); }
</style>
