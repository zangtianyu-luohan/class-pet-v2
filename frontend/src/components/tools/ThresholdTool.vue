<template>
  <el-dialog v-model="visible" title="🔔 积分阈值提醒" @close="$emit('update:modelValue', false)">
    <el-form label-width="100px">
      <el-form-item label="目标分数">
        <el-input-number v-model="points" :min="10" :max="9999" />
      </el-form-item>
      <el-form-item label="自动提醒">
        <el-switch v-model="autoCheck" />
      </el-form-item>
    </el-form>
    <el-button type="primary" @click="check" style="margin-bottom:12px;">检查达标学生</el-button>
    <div v-if="matched.length" style="margin-top:8px;">
      <div v-for="s in matched" :key="s.id" style="padding:6px 0;border-bottom:1px solid #f1f5f9;">
        {{ s.name }} — <span style="color:#6366f1;font-weight:600;">{{ s.points }}分</span>
      </div>
    </div>
    <div v-else-if="checked" style="text-align:center;padding:20px;color:#64748b;">
      暂无积分达到 {{ points }} 分的学生
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../../api'
import { useClassStore } from '../../stores/class'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])
const classStore = useClassStore()

const visible = ref(props.modelValue)
const points = ref(parseInt(localStorage.getItem('threshold_points') || '100'))
const autoCheck = ref(localStorage.getItem('threshold_auto') !== 'false')
const matched = ref([])
const checked = ref(false)

watch(() => props.modelValue, v => { visible.value = v; if (v) { matched.value = []; checked.value = false } })
watch(visible, v => emit('update:modelValue', v))
watch(points, v => localStorage.setItem('threshold_points', String(v)))
watch(autoCheck, v => localStorage.setItem('threshold_auto', String(v)))

async function check() {
  try {
    const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } })
    matched.value = res.data.filter(s => s.points >= points.value)
    checked.value = true
    if (matched.value.length) ElMessage.success(`发现 ${matched.value.length} 名学生积分达标！`)
  } catch { /* handled */ }
}
</script>
