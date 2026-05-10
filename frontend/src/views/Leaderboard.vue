<template>
  <div class="leaderboard-page">
    <div class="page-header">
      <h1>🏆 排行榜</h1>
    </div>

    <el-tabs v-model="activeTab" @tab-change="fetchData">
      <el-tab-pane label="⭐ 积分榜" name="points" />
      <el-tab-pane label="📈 等级榜" name="level" />
      <el-tab-pane label="🔥 本周榜" name="week" />
    </el-tabs>

    <!-- 前三名领奖台 -->
    <div class="podium" v-if="data.length >= 3">
      <div class="podium-item second">
        <div class="podium-rank">🥈</div>
        <div class="podium-pet">{{ petEmoji(data[1].pet_type) }}</div>
        <div class="podium-name">{{ data[1].name }}</div>
        <div class="podium-pts">{{ activeTab === 'week' ? data[1].week_points : data[1].points }} 积分</div>
      </div>
      <div class="podium-item first">
        <div class="podium-rank">🥇</div>
        <div class="podium-pet">{{ petEmoji(data[0].pet_type) }}</div>
        <div class="podium-name">{{ data[0].name }}</div>
        <div class="podium-pts">{{ activeTab === 'week' ? data[0].week_points : data[0].points }} 积分</div>
      </div>
      <div class="podium-item third">
        <div class="podium-rank">🥉</div>
        <div class="podium-pet">{{ petEmoji(data[2].pet_type) }}</div>
        <div class="podium-name">{{ data[2].name }}</div>
        <div class="podium-pts">{{ activeTab === 'week' ? data[2].week_points : data[2].points }} 积分</div>
      </div>
    </div>

    <!-- 桌面端表格 -->
    <el-table v-if="!isMobile" :data="data" stripe v-loading="loading" style="margin-top: 20px">
      <el-table-column prop="rank" label="排名" width="80">
        <template #default="{ row }">
          <span v-if="row.rank <= 3" style="font-size: 20px">{{ ['', '🥇', '🥈', '🥉'][row.rank] }}</span>
          <span v-else>{{ row.rank }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="学生" />
      <el-table-column label="萌宠" width="80">
        <template #default="{ row }">{{ petEmoji(row.pet_type) }}</template>
      </el-table-column>
      <el-table-column label="等级" width="80">
        <template #default="{ row }">Lv.{{ row.level }}</template>
      </el-table-column>
      <el-table-column label="积分" width="100">
        <template #default="{ row }">
          {{ activeTab === 'week' ? row.week_points : row.points }}
        </template>
      </el-table-column>
    </el-table>

    <!-- 移动端卡片列表 -->
    <div v-else class="rank-list">
      <div v-for="item in data" :key="item.rank" class="rank-card" :class="{ 'top3': item.rank <= 3 }">
        <div class="rank-badge">
          <span v-if="item.rank <= 3" class="rank-medal">{{ ['', '🥇', '🥈', '🥉'][item.rank] }}</span>
          <span v-else class="rank-num">{{ item.rank }}</span>
        </div>
        <div class="rank-pet">{{ petEmoji(item.pet_type) }}</div>
        <div class="rank-info">
          <div class="rank-name">{{ item.name }}</div>
          <div class="rank-meta">Lv.{{ item.level }}</div>
        </div>
        <div class="rank-points">{{ activeTab === 'week' ? item.week_points : item.points }} 分</div>
      </div>
    </div>

    <el-empty v-if="!loading && data.length === 0" description="暂无数据" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api'
import { useClassStore } from '../stores/class'

const classStore = useClassStore()
const activeTab = ref('points')
const data = ref([])
const loading = ref(false)

const isMobile = computed(() => window.innerWidth < 768)

const petEmojis = { cat: '🐱', dog: '🐶', rabbit: '🐰', panda: '🐼', penguin: '🐧' }
function petEmoji(type) { return petEmojis[type] || '🐱' }

async function fetchData() {
  if (!classStore.currentClassId) return
  loading.value = true
  try {
    const endpoint = activeTab.value === 'level' ? '/api/leaderboard/points' : `/api/leaderboard/${activeTab.value}`
    const params = { class_id: classStore.currentClassId }
    if (activeTab.value === 'level') params.sort_by = 'level'
    const res = await api.get(endpoint, { params })
    data.value = res.data
  } catch (e) { /* handled */ } finally { loading.value = false }
}

onMounted(fetchData)
watch(() => classStore.currentClassId, fetchData)
</script>

<style scoped>
.leaderboard-page { max-width: 800px; }
.page-header h1 { margin: 0 0 16px; font-size: 22px; }

.podium { display: flex; align-items: flex-end; justify-content: center; gap: 12px; padding: 24px 0; }
.podium-item { text-align: center; background: #fff; border-radius: 16px; padding: 16px 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); flex: 1; max-width: 180px; }
.podium-item.first { transform: translateY(-20px); border: 2px solid #fbbf24; }
.podium-item.second { border: 2px solid #d1d5db; }
.podium-item.third { border: 2px solid #d97706; }
.podium-rank { font-size: 28px; }
.podium-pet { font-size: 36px; margin: 4px 0; }
.podium-name { font-weight: 600; color: #1e293b; font-size: 14px; }
.podium-pts { font-size: 12px; color: #6366f1; font-weight: 600; }

/* 移动端排名卡片 */
.rank-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 16px;
}

.rank-card {
  background: #fff;
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.rank-card.top3 {
  border-left: 3px solid #fbbf24;
}

.rank-badge {
  width: 36px;
  text-align: center;
  flex-shrink: 0;
}

.rank-medal { font-size: 22px; }
.rank-num { font-size: 16px; font-weight: 700; color: #94a3b8; }

.rank-pet { font-size: 28px; flex-shrink: 0; }

.rank-info { flex: 1; min-width: 0; }
.rank-name { font-weight: 600; font-size: 15px; color: #1e293b; }
.rank-meta { font-size: 12px; color: #94a3b8; margin-top: 2px; }

.rank-points { font-weight: 700; color: #6366f1; font-size: 15px; flex-shrink: 0; }

@media (max-width: 767px) {
  .podium {
    gap: 8px;
    padding: 16px 0;
  }
  .podium-item {
    padding: 10px 8px;
    border-radius: 12px;
  }
  .podium-rank { font-size: 22px; }
  .podium-pet { font-size: 28px; }
  .podium-name { font-size: 12px; }
  .podium-pts { font-size: 11px; }
}
</style>
