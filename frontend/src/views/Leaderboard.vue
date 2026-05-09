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

    <!-- 完整列表 -->
    <el-table :data="data" stripe v-loading="loading" style="margin-top: 20px">
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

    <el-empty v-if="!loading && data.length === 0" description="暂无数据" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api'
import { useClassStore } from '../stores/class'

const classStore = useClassStore()
const activeTab = ref('points')
const data = ref([])
const loading = ref(false)

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
.podium { display: flex; align-items: flex-end; justify-content: center; gap: 16px; padding: 24px 0; }
.podium-item { text-align: center; background: #fff; border-radius: 16px; padding: 16px 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.podium-item.first { transform: translateY(-20px); border: 2px solid #fbbf24; }
.podium-item.second { border: 2px solid #d1d5db; }
.podium-item.third { border: 2px solid #d97706; }
.podium-rank { font-size: 32px; }
.podium-pet { font-size: 40px; margin: 4px 0; }
.podium-name { font-weight: 600; color: #1e293b; }
.podium-pts { font-size: 13px; color: #6366f1; font-weight: 600; }
</style>
