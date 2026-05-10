import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    component: () => import('../components/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'students', name: 'Students', component: () => import('../views/Students.vue') },
      { path: 'students/:id', name: 'StudentDetail', component: () => import('../views/StudentDetail.vue') },
      { path: 'leaderboard', name: 'Leaderboard', component: () => import('../views/Leaderboard.vue') },
      { path: 'badges', name: 'Badges', component: () => import('../views/Badges.vue') },
      { path: 'tools', name: 'Tools', component: () => import('../views/Tools.vue') },
      { path: 'points-logs', name: 'PointsLogs', component: () => import('../views/PointsLogs.vue') },
      { path: 'classes', name: 'Classes', component: () => import('../views/Classes.vue') },
      { path: 'settings', name: 'Settings', component: () => import('../views/Settings.vue') },
    ]
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.guest && authStore.isLoggedIn) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
