import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useScreenStore = defineStore('screen', () => {
  const rankList = ref([])
  const dynamics = ref([])
  const maxDynamics = 100

  async function fetchRankList(classId) {
    try {
      const res = await api.get('/api/leaderboard/points', {
        params: { class_id: classId }
      })
      rankList.value = res.data
    } catch (e) {
      console.error('获取排行榜失败:', e)
    }
  }

  async function fetchTodayLogs(classId) {
    try {
      const res = await api.get('/api/students/points-logs', {
        params: { class_id: classId, page_size: 50 }
      })
      dynamics.value = res.data.items || []
    } catch (e) {
      console.error('获取积分日志失败:', e)
    }
  }

  function handlePointsChange(data) {
    const student = rankList.value.find(s => s.id === data.student_id)
    if (student) {
      student.points = (student.points || 0) + data.points
      rankList.value.sort((a, b) => b.points - a.points)
    }

    dynamics.value.unshift({
      id: Date.now(),
      student_name: data.student_name,
      points: data.points,
      reason: data.reason,
      created_at: data.timestamp || new Date().toISOString()
    })

    if (dynamics.value.length > maxDynamics) {
      dynamics.value = dynamics.value.slice(0, maxDynamics)
    }
  }

  function handleStudentAdd(data) {
    rankList.value.push({
      id: data.student_id,
      name: data.student_name,
      student_no: data.student_no,
      points: 0
    })
  }

  function handleStudentDelete(data) {
    rankList.value = rankList.value.filter(s => s.id !== data.student_id)
  }

  function clear() {
    rankList.value = []
    dynamics.value = []
  }

  return {
    rankList,
    dynamics,
    fetchRankList,
    fetchTodayLogs,
    handlePointsChange,
    handleStudentAdd,
    handleStudentDelete,
    clear
  }
})
