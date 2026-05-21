<template>
  <el-dialog v-model="visible" title="🎲 随机点名" :close-on-click-modal="false" @close="close">
    <div class="random-result" v-if="result">
      <div class="random-name">{{ result.name }}</div>
      <div class="random-no">{{ result.student_no }}</div>
    </div>
    <div class="random-result" v-else>
      <div style="font-size: 18px; color: #94a3b8">点击按钮随机抽取</div>
    </div>
    <div v-if="pickedNames.length" style="margin-top:12px;text-align:center;">
      <div style="font-size:13px;color:#64748b;margin-bottom:6px;">已点过（{{ pickedNames.length }}/{{ allStudents.length }}）</div>
      <el-tag v-for="name in pickedNames" :key="name" style="margin:2px;" size="small">{{ name }}</el-tag>
    </div>
    <template #footer>
      <el-button type="primary" size="large" @click="pick" :loading="spinning" :disabled="allStudents.length > 0 && pickedNames.length >= allStudents.length">
        🎲 {{ pickedNames.length >= allStudents.length && allStudents.length > 0 ? '已点完全部' : '开始抽取' }}
      </el-button>
      <el-button v-if="pickedNames.length" @click="reset">🔄 重置</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '../../api'
import { useClassStore } from '../../stores/class'

const props = defineProps({ modelValue: Boolean })
const emit = defineEmits(['update:modelValue'])

const classStore = useClassStore()
const visible = ref(props.modelValue)
const result = ref(null)
const spinning = ref(false)
let allStudents = []
const pickedNames = ref([])

watch(() => props.modelValue, v => { visible.value = v; if (v) { result.value = null; allStudents = []; pickedNames.value = [] } })
watch(visible, v => emit('update:modelValue', v))

function close() {
  emit('update:modelValue', false)
}

function reset() {
  pickedNames.value = []
  result.value = null
}

async function pick() {
  if (!allStudents.length) {
    const res = await api.get('/api/students/', { params: { class_id: classStore.currentClassId } })
    allStudents = res.data
  }
  if (!allStudents.length) return

  // 从未点过的学生中选择
  const available = allStudents.filter(s => !pickedNames.value.includes(s.name))
  if (!available.length) return

  spinning.value = true
  result.value = null
  let count = 0
  const interval = setInterval(() => {
    result.value = available[Math.floor(Math.random() * available.length)]
    count++
    if (count > 15) {
      clearInterval(interval)
      spinning.value = false
      if (result.value) pickedNames.value.push(result.value.name)
    }
  }, 100)
}
</script>

<style scoped>
.random-result { text-align: center; padding: 24px 0; }
.random-name { font-size: 24px; font-weight: 700; color: #6366f1; margin-top: 8px; }
.random-no { color: #94a3b8; }
</style>
