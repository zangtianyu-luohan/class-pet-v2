<template>
  <div class="rank-card">
    <div class="card-header">
      <h3>🏆 排行榜</h3>
    </div>
    <div class="card-body">
      <div class="rank-list" ref="rankListRef">
        <div
          v-for="(student, index) in rankList"
          :key="student.id"
          class="rank-item"
          :class="{ 'top3': index < 3 }"
        >
          <span class="rank-num">{{ index + 1 }}</span>
          <span class="rank-name">{{ student.name }}</span>
          <span class="rank-points" :class="{ 'flash': student._flash }">
            {{ student.points }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  rankList: {
    type: Array,
    default: () => []
  }
})

const rankListRef = ref(null)

watch(() => props.rankList, (newList) => {
  newList.forEach(student => {
    if (student._flash) {
      setTimeout(() => {
        student._flash = false
      }, 500)
    }
  })
}, { deep: true })

function flashStudent(studentId) {
  const student = props.rankList.find(s => s.id === studentId)
  if (student) {
    student._flash = true
  }
}

defineExpose({ flashStudent })
</script>

<style scoped>
.rank-card {
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

.rank-list {
  height: 100%;
  overflow-y: auto;
}

.rank-list::-webkit-scrollbar {
  width: 4px;
}

.rank-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.rank-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  transition: background 0.2s;
}

.rank-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.rank-item.top3 {
  background: rgba(255, 215, 0, 0.1);
  border-left: 3px solid #ffd700;
}

.rank-num {
  width: 30px;
  font-size: 14px;
  font-weight: 600;
  color: #ffd700;
}

.rank-name {
  flex: 1;
  font-size: 14px;
  color: #fff;
}

.rank-points {
  font-size: 16px;
  font-weight: 700;
  color: #10b981;
  transition: all 0.3s;
}

.rank-points.flash {
  animation: flash 0.5s ease-in-out;
}

@keyframes flash {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}
</style>
