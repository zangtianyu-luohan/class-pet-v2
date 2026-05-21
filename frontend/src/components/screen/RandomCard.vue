<template>
  <div class="random-card">
    <div class="card-header">
      <h3>🎲 随机点名</h3>
    </div>
    <div class="card-body">
      <div class="random-result">
        <div v-if="result" class="result-name">{{ result.name }}</div>
        <div v-else class="result-placeholder">点击开始</div>
      </div>
      <div class="random-controls">
        <el-button
          type="primary"
          size="large"
          @click="pick"
          :loading="spinning"
          :disabled="students.length > 0 && pickedNames.length >= students.length"
        >
          {{ pickedNames.length >= students.length && students.length > 0 ? '已点完' : '开始抽取' }}
        </el-button>
        <el-button v-if="pickedNames.length" @click="reset">
          重置
        </el-button>
      </div>
      <div v-if="pickedNames.length" class="picked-list">
        <div class="picked-header">已点过 ({{ pickedNames.length }}/{{ students.length }})</div>
        <div class="picked-tags">
          <el-tag
            v-for="name in pickedNames"
            :key="name"
            size="small"
            style="margin: 2px;"
          >
            {{ name }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../../api'
import { useClassStore } from '../../stores/class'

const classStore = useClassStore()
const students = ref([])
const result = ref(null)
const spinning = ref(false)
const pickedNames = ref([])

async function loadStudents() {
  if (!classStore.currentClassId) return
  try {
    const res = await api.get('/api/students/', {
      params: { class_id: classStore.currentClassId }
    })
    students.value = res.data
  } catch (e) {
    console.error('加载学生失败:', e)
  }
}

async function pick() {
  if (!students.value.length) {
    await loadStudents()
  }
  if (!students.value.length) return

  const available = students.value.filter(s => !pickedNames.value.includes(s.name))
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
      if (result.value) {
        pickedNames.value.push(result.value.name)
      }
    }
  }, 100)
}

function reset() {
  pickedNames.value = []
  result.value = null
}

defineExpose({ loadStudents })
</script>

<style scoped>
.random-card {
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
}

.random-result {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100px;
}

.result-name {
  font-size: 36px;
  font-weight: 700;
  color: #6366f1;
}

.result-placeholder {
  font-size: 18px;
  color: #94a3b8;
}

.random-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.picked-list {
  width: 100%;
}

.picked-header {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.picked-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
</style>
