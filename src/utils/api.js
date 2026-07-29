import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('[API Error]', error.config?.url, error.message, error.response?.data)
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 401:
          if (router.currentRoute.value.path !== '/login') {
            sessionStorage.removeItem('token')
            sessionStorage.removeItem('user')
            sessionStorage.removeItem('last_activity_at')
            window.dispatchEvent(new Event('auth-session-cleared'))
            router.push('/login')
          }
          break
        case 403:
          ElMessage.error('权限不足')
          break
        default:
          ElMessage.error(data?.error || '请求失败，请检查网络连接')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default api
