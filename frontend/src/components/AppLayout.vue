<template>
  <el-container class="app-layout">
    <!-- 移动端顶栏 -->
    <div class="mobile-header" v-if="isMobile">
      <el-button text @click="drawerVisible = true" class="menu-btn">
        <el-icon size="24"><Expand /></el-icon>
      </el-button>
      <span class="mobile-logo">🐾 学生积分管理系统</span>
      <el-select
        v-if="classStore.classes.length"
        :model-value="classStore.currentClassId"
        @update:model-value="classStore.setCurrentClass"
        size="small"
        class="mobile-class-select"
        placeholder="切换班级"
      >
        <el-option
          v-for="c in classStore.classes"
          :key="c.id"
          :label="c.name"
          :value="c.id"
        />
      </el-select>
      <el-dropdown @command="handleCommand" trigger="click">
        <el-avatar :size="32" class="mobile-avatar">{{ authStore.user?.display_name?.[0] || '?' }}</el-avatar>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="settings">⚙️ 设置</el-dropdown-item>
            <el-dropdown-item command="logout" divided>🚪 退出</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 移动端抽屉侧边栏 -->
    <el-drawer
      v-model="drawerVisible"
      direction="ltr"
      size="260px"
      :show-close="false"
      class="mobile-drawer"
      v-if="isMobile"
    >
      <template #header>
        <div class="drawer-header">
          <span class="logo-icon">🐾</span>
          <span class="logo-text">学生积分管理系统</span>
        </div>
      </template>
      <SidebarContent
        :is-collapsed="false"
        @navigate="drawerVisible = false"
      />
    </el-drawer>

    <!-- 桌面端侧边栏 -->
    <el-aside :width="isCollapsed ? '64px' : '240px'" class="sidebar" v-if="!isMobile">
      <div class="sidebar-header" :class="{ 'sidebar-header-collapsed': isCollapsed }">
        <span class="logo-icon">🐾</span>
        <span v-if="!isCollapsed" class="logo-text">学生积分管理系统</span>
        <el-button
          text
          size="small"
          @click="isCollapsed = !isCollapsed"
          class="collapse-btn"
        >
          <el-icon :size="18"><Fold v-if="!isCollapsed" /><Expand v-else /></el-icon>
        </el-button>
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

      <SidebarContent :is-collapsed="isCollapsed" />

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
    <el-main class="main-content" :class="{ 'mobile-main': isMobile }">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useClassStore } from '../stores/class'
import SidebarContent from './SidebarContent.vue'
import { Fold, Expand } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const classStore = useClassStore()

const isCollapsed = ref(false)
const drawerVisible = ref(false)
const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value < 768)
const isTablet = computed(() => windowWidth.value >= 768 && windowWidth.value < 1024)

// 平板自动折叠
if (isTablet.value) {
  isCollapsed.value = true
}

function onResize() {
  windowWidth.value = window.innerWidth
  if (windowWidth.value < 768) {
    isCollapsed.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  try {
    classStore.fetchClasses()
  } catch (e) {
    // 静默失败
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})

// 路由变化时关闭移动端抽屉
watch(() => route.path, () => {
  if (isMobile.value) {
    drawerVisible.value = false
  }
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function handleCommand(cmd) {
  if (cmd === 'settings') router.push('/settings')
  if (cmd === 'logout') handleLogout()
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
  overflow: hidden;
}

/* 移动端顶栏 */
.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  background: linear-gradient(90deg, #312e81, #1e1b4b);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  z-index: 1000;
  color: #fff;
}

.mobile-class-select {
  flex: 1;
  min-width: 0;
  max-width: 160px;
}

.mobile-class-select :deep(.el-input__wrapper) {
  background: rgba(255,255,255,0.15);
  border: none;
  box-shadow: none;
  border-radius: 6px;
}

.mobile-class-select :deep(.el-input__inner) {
  color: #fff;
  font-size: 13px;
}

.mobile-class-select :deep(.el-input__suffix) {
  color: rgba(255,255,255,0.7);
}

.menu-btn {
  color: #fff !important;
  padding: 8px;
}

.mobile-logo {
  font-size: 18px;
  font-weight: 700;
}

.mobile-avatar {
  cursor: pointer;
  background: rgba(255,255,255,0.2);
  color: #fff;
}

/* 抽屉样式 */
.drawer-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

:deep(.mobile-drawer .el-drawer__header) {
  background: linear-gradient(180deg, #312e81 0%, #1e1b4b 100%);
  color: #fff;
  margin-bottom: 0;
  padding: 16px;
}

:deep(.mobile-drawer .el-drawer__body) {
  padding: 0;
  background: linear-gradient(180deg, #312e81 0%, #1e1b4b 100%);
}

/* 桌面端侧边栏 */
.sidebar {
  background: linear-gradient(180deg, #312e81 0%, #1e1b4b 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  overflow: hidden;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 20px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  position: relative;
}

.sidebar-header-collapsed {
  padding: 16px 8px;
  flex-direction: column;
  gap: 8px;
}

.sidebar-header-collapsed .logo-icon {
  font-size: 24px;
}

.sidebar-header-collapsed .collapse-btn {
  margin-left: 0;
  padding: 6px;
  width: 100%;
  display: flex;
  justify-content: center;
}

.logo-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  white-space: nowrap;
}

.collapse-btn {
  margin-left: auto;
  color: rgba(255,255,255,0.6) !important;
}

.class-switcher {
  padding: 12px 16px;
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

/* 移动端主内容 */
.mobile-main {
  padding: 16px;
  padding-top: 72px; /* 顶栏高度 + 间距 */
}

/* 平板适配 */
@media (min-width: 768px) and (max-width: 1023px) {
  .main-content {
    padding: 16px;
  }
}
</style>
