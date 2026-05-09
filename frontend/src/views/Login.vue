<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">🐾</div>
        <h1>班级OK萌宠</h1>
        <p>趣味班级积分管理系统</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </div>

      <div class="login-pets">🐱 🐶 🐰 🐼 🐧</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  try {
    await formRef.value.validate()
  } catch { return }

  loading.value = true
  try {
    await authStore.login(form.username, form.password)
    ElMessage.success('登录成功！')
    router.push('/dashboard')
  } catch (e) {
    // 错误已在 api 拦截器中处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
  position: relative;
  overflow: hidden;
}

.login-page::before,
.login-page::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
}

.login-page::before {
  width: 300px; height: 300px;
  background: #fbbf24;
  top: -80px; left: -80px;
  animation: float 6s ease-in-out infinite;
}

.login-page::after {
  width: 200px; height: 200px;
  background: #34d399;
  bottom: -60px; right: -60px;
  animation: float 8s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.login-card {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 40px 32px;
  width: 380px;
  box-shadow: 0 25px 60px rgba(0,0,0,0.15);
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 48px;
  margin-bottom: 8px;
}

.login-header h1 {
  font-size: 24px;
  background: linear-gradient(135deg, #6366f1, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}

.login-header p {
  color: #94a3b8;
  font-size: 14px;
  margin-top: 4px;
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: #94a3b8;
}

.login-footer a {
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
}

.login-pets {
  text-align: center;
  margin-top: 24px;
  font-size: 20px;
  letter-spacing: 8px;
}
</style>
