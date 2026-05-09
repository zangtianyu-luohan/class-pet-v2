<template>
  <el-container class="app-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapsed ? '64px' : '240px'" class="sidebar">
      <div class="sidebar-header">
        <span class="logo-icon">🐾</span>
        <span v-if="!isCollapsed" class="logo-text">班级OK萌宠</span>
      </div>

      <!-- 班级切换 -->
      <div v-if="!isCollapsed && classStore.classes.length" class="class-switcher">
        <el-select
          :model-value="classStore.currentClassId"
          @update:model-value="classStore.setCurrentClass"
          size="small"
          style="width: 100%"
        >
          <el-option
            v-for="c in classStore.classes"
            :key="c.id"
            :label="c.name"
            :value="c.id"
          />
        </el-select>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        router
        background-color="transparent"
        text-color="rgba(255,255,255,0.7)"
        active-text-color="#fff"
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>班级总览</span>
        </el-menu-item>
        <el-menu-item index="/students">
          <el-icon><User /></el-icon>
          <span>学生管理</span>
        </el-menu-item>
        <el-menu-item index="/leaderboard">
          <el-icon><Trophy /></el-icon>
          <span>排行榜</span>
        </el-menu-item>
        <el-menu-item index="/badges">
          <el-icon><Medal /></el-icon>
          <span>勋章管理</span>
        </el-menu-item>
        <el-menu-item index="/tools">
          <el-icon><MagicStick /></el-icon>
          <span>课堂工具</span>
        </el-menu-item>
        <el-menu-item index="/classes">
          <el-icon><School /></el-icon>
          <span>班级管理</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <div v-if="!isCollapsed" class="user-info">
          <el-avatar :size="32">{{ authStore.user?.display_name?.[0] || '?' }}</el-avatar>
          <span class="user-name">{{ authStore.user?.display_name }}</span>
        </div>
        <el-button text size="small" @click="handleLogout" style="color: rgba(255,255,255,0.6)">
          <el-icon><SwitchButton /></el-icon>
        </el-button>
      </div>
    </el-aside>

    <!-- 主内容 -->
    <el-main class="main-content">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useClassStore } from '../stores/class'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const classStore = useClassStore()

const isCollapsed = ref(false)

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/students/')) return '/students'
  return path
})

onMounted(async () => {
  try {
    await classStore.fetchClasses()
  } catch (e) {
    // 静默失败
  }
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>



<style scoped>
.app-layout {
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background: linear-gradient(180deg, #312e81 0%, #1e1b4b 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  overflow: hidden;
}

.sidebar-header {
  padding: 20px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  white-space: nowrap;
}

.class-switcher {
  padding: 12px 16px;
}

.sidebar-menu {
  flex: 1;
  border-right: none !important;
  padding: 8px 0;
}

.sidebar-menu .el-menu-item {
  border-radius: 8px;
  margin: 2px 8px;
  height: 44px;
}

.sidebar-menu .el-menu-item.is-active {
  background: rgba(255,255,255,0.15) !important;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(255,255,255,0.08) !important;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  font-size: 14px;
  white-space: nowrap;
}

.main-content {
  background: #f5f7fa;
  padding: 24px;
  overflow-y: auto;
}
</style>
