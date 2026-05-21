<template>
  <div class="screen-page">
    <div class="screen-header">
      <h1>📊 班级大屏</h1>
      <div class="header-actions">
        <el-dropdown trigger="click" @command="addCard">
          <el-button type="primary">+ 添加卡片</el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="(entry, type) in CARD_REGISTRY"
                :key="type"
                :command="type"
              >
                {{ entry.icon }} {{ entry.title }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button @click="layoutStore.resetLayout()">重置布局</el-button>
        <el-button @click="$router.push('/')">返回首页</el-button>
      </div>
    </div>

    <div class="screen-grid">
      <ScreenCard
        v-for="card in layoutStore.cards"
        :key="card.id"
        :size="card.size"
        @remove="layoutStore.removeCard(card.id)"
      >
        <component
          :is="getComponent(card.type)"
          v-bind="getProps(card)"
          :ref="el => setRef(card.id, el)"
        />
      </ScreenCard>
    </div>

    <!-- 积分变化特效 -->
    <div v-if="effect.show" class="points-effect" :class="effect.type">
      <span class="effect-name">{{ effect.name }}</span>
      <span class="effect-points">{{ effect.points > 0 ? '+' : '' }}{{ effect.points }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useScreenStore } from '../stores/screen'
import { useClassStore } from '../stores/class'
import { useScreenLayoutStore, CARD_REGISTRY } from '../stores/screenLayout'
import { sseClient } from '../api/sse'
import ScreenCard from '../components/screen/ScreenCard.vue'

const screenStore = useScreenStore()
const classStore = useClassStore()
const layoutStore = useScreenLayoutStore()

const refs = {}

const effect = reactive({
  show: false,
  type: '',
  name: '',
  points: 0
})

function getComponent(type) {
  return CARD_REGISTRY[type]?.component
}

function getProps(card) {
  if (card.type === 'rank') return { rankList: screenStore.rankList }
  if (card.type === 'dynamic') return { dynamics: screenStore.dynamics }
  if (card.type === 'lottery' || card.type === 'exchange' || card.type === 'threshold') {
    const entry = CARD_REGISTRY[card.type]
    return { title: entry.title, icon: entry.icon, desc: entry.desc, dialogComponent: entry.dialog }
  }
  // B 类工具：传入 mode='card' 使用卡片模式渲染
  if (['dice', 'traffic', 'noise', 'stopwatch', 'randomNum', 'group'].includes(card.type)) {
    return { mode: 'card' }
  }
  return {}
}

function setRef(id, el) {
  if (el) refs[id] = el
}

function addCard(type) {
  layoutStore.addCard(type)
}

function showPointsEffect(data) {
  effect.show = true
  effect.type = data.points > 0 ? 'add' : 'sub'
  effect.name = data.student_name
  effect.points = data.points

  // 找到 rank 卡片并触发 flash
  const rankCard = layoutStore.cards.find(c => c.type === 'rank')
  if (rankCard && refs[rankCard.id]) {
    refs[rankCard.id].flashStudent(data.student_id)
  }

  setTimeout(() => {
    effect.show = false
  }, 1000)
}

function handlePointsChange(data) {
  screenStore.handlePointsChange(data)
  showPointsEffect(data)
}

function handleStudentAdd(data) {
  screenStore.handleStudentAdd(data)
}

function handleStudentDelete(data) {
  screenStore.handleStudentDelete(data)
}

onMounted(async () => {
  if (classStore.currentClassId) {
    await screenStore.fetchRankList(classStore.currentClassId)
    await screenStore.fetchTodayLogs(classStore.currentClassId)
  }

  sseClient.connect()
  sseClient.on('points_change', handlePointsChange)
  sseClient.on('student_add', handleStudentAdd)
  sseClient.on('student_delete', handleStudentDelete)

  // 找到 random 卡片并加载学生
  const randomCard = layoutStore.cards.find(c => c.type === 'random')
  if (randomCard && refs[randomCard.id]) {
    refs[randomCard.id].loadStudents()
  }
})

onUnmounted(() => {
  sseClient.off('points_change', handlePointsChange)
  sseClient.off('student_add', handleStudentAdd)
  sseClient.off('student_delete', handleStudentDelete)
  sseClient.disconnect()
  screenStore.clear()
})
</script>

<style scoped>
.screen-page {
  background: #0f0f23;
  color: #fff;
  padding: 20px;
  min-height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.screen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.screen-header h1 {
  margin: 0;
  font-size: 24px;
  color: #fff;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.screen-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-auto-rows: minmax(250px, 1fr);
  gap: 16px;
  min-height: 0;
  overflow-y: auto;
}

.points-effect {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: effectIn 0.5s ease-out;
}

.points-effect.add {
  color: #10b981;
}

.points-effect.sub {
  color: #ef4444;
}

.effect-name {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.effect-points {
  font-size: 48px;
  font-weight: 700;
}

@keyframes effectIn {
  from {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.5);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
}
</style>

<style>
/* Override AppLayout constraints for full-screen page */
.app-layout .el-main {
  overflow: auto !important;
}
</style>
