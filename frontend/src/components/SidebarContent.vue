<template>
  <el-menu
    :default-active="activeMenu"
    :collapse="isCollapsed"
    router
    background-color="transparent"
    text-color="rgba(255,255,255,0.7)"
    active-text-color="#fff"
    class="sidebar-menu"
    @select="$emit('navigate')"
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
    <el-menu-item index="/points-logs">
      <el-icon><Notebook /></el-icon>
      <span>积分日志</span>
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
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DataBoard, User, Trophy, Medal, MagicStick, School, Setting, Notebook } from '@element-plus/icons-vue'

defineProps({
  isCollapsed: { type: Boolean, default: false }
})

defineEmits(['navigate'])

const route = useRoute()

const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/students/')) return '/students'
  return path
})
</script>

<style scoped>
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
</style>
