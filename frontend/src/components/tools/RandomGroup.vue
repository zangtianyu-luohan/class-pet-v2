<template>
  <!-- Dialog 模式 -->
  <el-dialog v-if="mode === 'dialog'" v-model="visible" title="👥 随机分组" @close="$emit('update:modelValue', false)">
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

  <!-- Card 模式 -->
  <div v-else class="group-card">
    <div class="card-header"><h3>👥 随机分组</h3></div>
    <div class="card-body">
      <div style="display:flex;align-items:center;justify-content:center;gap:8px;">
        <span style="font-size:13px;color:#94a3b8;">分几组：</span>
        <el-input-number v-model="groupCount" :min="2" :max="10" size="small" />
        <el-button type="primary" size="small" @click="doGroup">开始分组</el-button>
      </div>
      <div v-if="groups.length" style="margin-top:12px;flex:1;overflow-y:auto;">
        <div v-for="(group, i) in groups" :key="i" style="margin-bottom:8px;">
          <el-tag size="small" type="primary" style="margin-right:6px;">第{{ i + 1 }}组</el-tag>
          <el-tag v-for="s in group" :key="s.id" size="small" style="margin:2px;">{{ s.name }}</el-tag>
        </div>
      </div>
      <div v-else style="text-align:center;color:#94a3b8;padding:20px 0;font-size:13px;">点击开始分组</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '../../api'
import { useClassStore } from '../../stores/class'

const props = defineProps({
  modelValue: Boolean,
  mode: { type: String, default: 'dialog' }
})
const emit = defineEmits(['update:modelValue'])
const classStore = useClassStore()

const visible = ref(props.modelValue)
const groupCount = ref(3)
const groups = ref([])

watch(() => props.modelValue, v => { visible.value = v; if (v) groups.value = [] })
watch(visible, v => emit('update:modelValue', v))

async function doGroup() {
  const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } })
  const list = [...res.data].sort(() => Math.random() - 0.5)
  groups.value = Array.from({ length: groupCount.value }, () => [])
  list.forEach((s, i) => groups.value[i % groupCount.value].push(s))
}
</script>

<style scoped>
.group-card {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px; padding: 20px; height: 100%;
  display: flex; flex-direction: column;
}
.card-header { margin-bottom: 12px; }
.card-header h3 { margin: 0; font-size: 18px; color: #fff; }
.card-body { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.group-row { margin-bottom: 12px; }
</style>
