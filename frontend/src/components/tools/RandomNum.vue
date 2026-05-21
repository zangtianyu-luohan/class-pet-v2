<template>
  <!-- Dialog 模式 -->
  <el-dialog v-if="mode === 'dialog'" v-model="visible" title="🔢 随机数" :close-on-click-modal="false" width="380px" @close="$emit('update:modelValue', false)">
    <el-form label-width="80px">
      <el-form-item label="最小值"><el-input-number v-model="min" :min="-9999" :max="9999" /></el-form-item>
      <el-form-item label="最大值"><el-input-number v-model="max" :min="-9999" :max="9999" /></el-form-item>
      <el-form-item label="个数"><el-input-number v-model="numCount" :min="1" :max="20" /></el-form-item>
      <el-form-item label="不重复"><el-switch v-model="unique" /></el-form-item>
    </el-form>
    <div v-if="results.length" style="text-align:center;margin:16px 0;">
      <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:12px;">
        <div v-for="(num, i) in results" :key="i"
          style="width:64px;height:64px;display:flex;align-items:center;justify-content:center;background:#6366f1;color:#fff;border-radius:12px;font-size:24px;font-weight:700;">
          {{ num }}
        </div>
      </div>
    </div>
    <div v-else style="text-align:center;color:#94a3b8;padding:20px 0;">设置范围后点击生成</div>
    <template #footer>
      <el-button type="primary" size="large" @click="generate">🎲 生成</el-button>
    </template>
  </el-dialog>

  <!-- Card 模式 -->
  <div v-else class="random-num-card">
    <div class="card-header"><h3>🔢 随机数</h3></div>
    <div class="card-body">
      <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:center;">
        <span style="font-size:13px;color:#94a3b8;">最小</span>
        <el-input-number v-model="min" :min="-9999" :max="9999" size="small" controls-position="right" style="width:90px;" />
        <span style="font-size:13px;color:#94a3b8;">最大</span>
        <el-input-number v-model="max" :min="-9999" :max="9999" size="small" controls-position="right" style="width:90px;" />
        <span style="font-size:13px;color:#94a3b8;">个数</span>
        <el-input-number v-model="numCount" :min="1" :max="20" size="small" controls-position="right" style="width:80px;" />
        <el-checkbox v-model="unique" style="color:#94a3b8;">不重复</el-checkbox>
      </div>
      <div v-if="results.length" style="text-align:center;margin-top:12px;">
        <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:8px;">
          <div v-for="(num, i) in results" :key="i" class="num-box">{{ num }}</div>
        </div>
      </div>
      <div v-else style="text-align:center;color:#94a3b8;padding:16px 0;font-size:13px;">设置范围后点击生成</div>
      <div style="text-align:center;margin-top:8px;">
        <el-button type="primary" @click="generate">🎲 生成</el-button>
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
const min = ref(1)
const max = ref(100)
const numCount = ref(1)
const unique = ref(false)
const results = ref([])

watch(() => props.modelValue, v => { visible.value = v; if (v) results.value = [] })
watch(visible, v => emit('update:modelValue', v))

function generate() {
  const lo = Math.min(min.value, max.value)
  const hi = Math.max(min.value, max.value)
  const count = Math.min(numCount.value, hi - lo + 1)
  if (unique.value) {
    const pool = []
    for (let i = lo; i <= hi; i++) pool.push(i)
    for (let i = pool.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [pool[i], pool[j]] = [pool[j], pool[i]] }
    results.value = pool.slice(0, count)
  } else {
    results.value = Array.from({ length: count }, () => Math.floor(Math.random() * (hi - lo + 1)) + lo)
  }
}
</script>

<style scoped>
.random-num-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px; padding: 20px; height: 100%;
  display: flex; flex-direction: column;
}
.card-header { margin-bottom: 12px; }
.card-header h3 { margin: 0; font-size: 18px; color: #fff; }
.card-body { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.num-box {
  width: 50px; height: 50px; display: flex; align-items: center; justify-content: center;
  background: #6366f1; color: #fff; border-radius: 10px; font-size: 18px; font-weight: 700;
}
</style>
