import { defineStore } from 'pinia'
import { ref } from 'vue'
import { defineAsyncComponent } from 'vue'

// 卡片注册表
export const CARD_REGISTRY = {
  rank: {
    title: '排行榜',
    icon: '🏆',
    size: 'tall',
    component: defineAsyncComponent(() => import('../components/screen/RankCard.vue'))
  },
  dynamic: {
    title: '实时动态',
    icon: '📊',
    size: 'tall',
    component: defineAsyncComponent(() => import('../components/screen/DynamicCard.vue'))
  },
  timer: {
    title: '课堂计时',
    icon: '⏱️',
    size: 'normal',
    component: defineAsyncComponent(() => import('../components/screen/TimerCard.vue'))
  },
  random: {
    title: '随机点名',
    icon: '🎯',
    size: 'normal',
    component: defineAsyncComponent(() => import('../components/screen/RandomCard.vue'))
  },
  dice: {
    title: '骰子',
    icon: '🎲',
    size: 'normal',
    component: defineAsyncComponent(() => import('../components/tools/DiceTool.vue'))
  },
  traffic: {
    title: '红绿灯',
    icon: '🚦',
    size: 'normal',
    component: defineAsyncComponent(() => import('../components/tools/TrafficLight.vue'))
  },
  noise: {
    title: '噪音检测',
    icon: '🔇',
    size: 'normal',
    component: defineAsyncComponent(() => import('../components/tools/NoiseDetector.vue'))
  },
  stopwatch: {
    title: '秒表',
    icon: '⏱️',
    size: 'normal',
    component: defineAsyncComponent(() => import('../components/tools/StopwatchTool.vue'))
  },
  randomNum: {
    title: '随机数',
    icon: '🔢',
    size: 'normal',
    component: defineAsyncComponent(() => import('../components/tools/RandomNum.vue'))
  },
  group: {
    title: '随机分组',
    icon: '👥',
    size: 'wide',
    component: defineAsyncComponent(() => import('../components/tools/RandomGroup.vue'))
  },
  lottery: {
    title: '积分抽奖',
    icon: '🎰',
    size: 'normal',
    component: defineAsyncComponent(() => import('../components/screen/LauncherCard.vue')),
    dialog: defineAsyncComponent(() => import('../components/tools/LotteryTool.vue')),
    desc: '消耗积分抽奖，激励学生'
  },
  exchange: {
    title: '积分兑换',
    icon: '🎁',
    size: 'normal',
    component: defineAsyncComponent(() => import('../components/screen/LauncherCard.vue')),
    dialog: defineAsyncComponent(() => import('../components/tools/ExchangeTool.vue')),
    desc: '积分兑换奖品'
  },
  threshold: {
    title: '积分提醒',
    icon: '🔔',
    size: 'normal',
    component: defineAsyncComponent(() => import('../components/screen/LauncherCard.vue')),
    dialog: defineAsyncComponent(() => import('../components/tools/ThresholdTool.vue')),
    desc: '积分达标提醒'
  }
}

// 默认布局
const DEFAULT_CARDS = [
  { id: 'rank-1', type: 'rank', size: 'tall' },
  { id: 'dynamic-1', type: 'dynamic', size: 'tall' },
  { id: 'timer-1', type: 'timer', size: 'normal' },
  { id: 'random-1', type: 'random', size: 'normal' }
]

const STORAGE_KEY = 'screen_layout_v1'

export const useScreenLayoutStore = defineStore('screenLayout', () => {
  const cards = ref([])

  function loadLayout() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed) && parsed.length > 0) {
          // 验证每个卡片的 type 在注册表中存在
          cards.value = parsed.filter(c => CARD_REGISTRY[c.type])
          return
        }
      }
    } catch {}
    cards.value = JSON.parse(JSON.stringify(DEFAULT_CARDS))
  }

  function saveLayout() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cards.value))
  }

  function addCard(type) {
    if (!CARD_REGISTRY[type]) return
    // 生成唯一 id
    const existing = cards.value.filter(c => c.type === type)
    const num = existing.length + 1
    const id = `${type}-${num}`
    cards.value.push({
      id,
      type,
      size: CARD_REGISTRY[type].size
    })
    saveLayout()
  }

  function removeCard(id) {
    cards.value = cards.value.filter(c => c.id !== id)
    saveLayout()
  }

  function resetLayout() {
    cards.value = JSON.parse(JSON.stringify(DEFAULT_CARDS))
    saveLayout()
  }

  // 初始化时加载
  loadLayout()

  return {
    cards,
    addCard,
    removeCard,
    resetLayout,
    loadLayout,
    saveLayout
  }
})
