<template>
  <div class="settings-page">
    <div class="page-header">
      <h1>⚙️ 系统设置</h1>
    </div>

    <el-card shadow="never" class="settings-card">
      <template #header><span>👤 个人信息</span></template>
      <el-form :model="profileForm" label-width="80px" style="max-width: 400px">
        <el-form-item label="用户名">
          <el-input :model-value="authStore.user?.username" disabled />
        </el-form-item>
        <el-form-item label="显示名称">
          <el-input v-model="profileForm.display_name" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="updateProfile">保存修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="settings-card">
      <template #header><span>🔒 修改密码</span></template>
      <el-form :model="pwForm" label-width="80px" style="max-width: 400px">
        <el-form-item label="原密码">
          <el-input v-model="pwForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="changePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const profileForm = reactive({ display_name: authStore.user?.display_name || '' })
const pwForm = reactive({ old_password: '', new_password: '' })

async function updateProfile() {
  try {
    const res = await api.put('/api/auth/me', { display_name: profileForm.display_name })
    authStore.user = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
    ElMessage.success('已更新')
  } catch (e) { /* handled */ }
}

async function changePassword() {
  if (!pwForm.old_password || !pwForm.new_password) { ElMessage.warning('请填写完整'); return }
  try {
    await api.put('/api/auth/password', pwForm)
    ElMessage.success('密码已修改')
    pwForm.old_password = ''
    pwForm.new_password = ''
  } catch (e) { /* handled */ }
}
</script>

<style scoped>
.settings-page { width: 100%; }
.page-header h1 { margin: 0 0 20px; font-size: 22px; }
.settings-card { border-radius: 16px; margin-bottom: 16px; }
</style>
