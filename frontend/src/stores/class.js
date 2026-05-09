import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useClassStore = defineStore('class', () => {
  const classes = ref([])
  const currentClassId = ref(localStorage.getItem('currentClassId') ? Number(localStorage.getItem('currentClassId')) : null)

  const currentClass = computed(() => classes.value.find(c => c.id === currentClassId.value) || null)

  async function fetchClasses() {
    const res = await api.get('/api/classes/')
    classes.value = res.data
    // 如果当前选择的班级不在列表中，选第一个
    if (classes.value.length && !classes.value.find(c => c.id === currentClassId.value)) {
      setCurrentClass(classes.value[0].id)
    }
  }

  function setCurrentClass(id) {
    currentClassId.value = id
    localStorage.setItem('currentClassId', String(id))
  }

  return { classes, currentClassId, currentClass, fetchClasses, setCurrentClass }
})
