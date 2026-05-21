<template>
  <div class="dynamic-card">
    <div class="card-header">
      <h3>📊 实时动态</h3>
    </div>
    <div class="card-body">
      <div class="dynamic-list" ref="listRef">
        <div
          v-for="item in dynamics"
          :key="item.id"
          class="dynamic-item"
          :class="{ 'points-add': item.points > 0, 'points-sub': item.points < 0 }"
        >
          <span class="dynamic-name">{{ item.student_name }}</span>
          <span class="dynamic-points" :class="{ 'positive': item.points > 0, 'negative': item.points < 0 }">
            {{ item.points > 0 ? '+' : '' }}{{ item.points }}
          </span>
          <span class="dynamic-reason">{{ item.reason }}</span>
          <span class="dynamic-time">{{ formatTime(item.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  dynamics: {
    type: Array,
    default: () => []
  }
})

const listRef = ref(null)

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

watch(() => props.dynamics.length, async () => {
  await nextTick()
  if (listRef.value) {
    listRef.value.scrollTop = 0
  }
})
</script>

<style scoped>
.dynamic-card {
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
  overflow: hidden;
}

.dynamic-list {
  height: 100%;
  overflow-y: auto;
}

.dynamic-list::-webkit-scrollbar {
  width: 4px;
}

.dynamic-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.dynamic-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  animation: slideIn 0.3s ease-out;
}

.dynamic-item.points-add {
  border-left: 3px solid #10b981;
}

.dynamic-item.points-sub {
  border-left: 3px solid #ef4444;
}

.dynamic-name {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  min-width: 60px;
}

.dynamic-points {
  font-size: 16px;
  font-weight: 700;
  min-width: 50px;
  text-align: center;
}

.dynamic-points.positive {
  color: #10b981;
}

.dynamic-points.negative {
  color: #ef4444;
}

.dynamic-reason {
  flex: 1;
  font-size: 13px;
  color: #94a3b8;
}

.dynamic-time {
  font-size: 12px;
  color: #64748b;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
