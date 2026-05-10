import axios from 'axios'
import { ElMessage } from 'element-plus'

// 生产环境用环境变量，开发环境走 Vite 代理
const baseURL = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截：自动加 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：统一错误处理
api.interceptors.response.use(
  res => res,
  err => {
    const status = err.response?.status
    const detail = err.response?.data?.detail || '请求失败'
    const url = err.config?.url || ''

    // 登录接口的错误不拦截，交给登录页自己处理
    if (url.includes('/api/auth/login')) {
      ElMessage.error(detail)
      return Promise.reject(err)
    }

    if (status === 401 || status === 403) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
      return Promise.reject(err)
    }
    ElMessage.error(detail)
    return Promise.reject(err)
  }
)

export default api
