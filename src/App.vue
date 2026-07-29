<template>
  <router-view />
</template>

<script setup>
import { onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const IDLE_TIMEOUT_MS = 30 * 60 * 1000
const ACTIVITY_WRITE_INTERVAL_MS = 10 * 1000
const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart']

const router = useRouter()
const authStore = useAuthStore()
let idleTimer = null
let lastActivityWrite = 0

const clearIdleTimer = () => {
  if (idleTimer) {
    window.clearTimeout(idleTimer)
    idleTimer = null
  }
}

const handleIdleLogout = async () => {
  if (!authStore.isAuthenticated) return
  await authStore.logout()
  ElMessage.warning('长时间未操作，已自动退出登录')
  await router.replace('/login')
}

const scheduleIdleLogout = () => {
  clearIdleTimer()
  if (!authStore.isAuthenticated) return

  const lastActivity = Number(sessionStorage.getItem('last_activity_at')) || Date.now()
  const remaining = IDLE_TIMEOUT_MS - (Date.now() - lastActivity)
  if (remaining <= 0) {
    handleIdleLogout()
    return
  }
  idleTimer = window.setTimeout(handleIdleLogout, remaining)
}

const recordActivity = () => {
  if (!authStore.isAuthenticated) return
  const now = Date.now()
  if (now - lastActivityWrite < ACTIVITY_WRITE_INTERVAL_MS) return
  lastActivityWrite = now
  sessionStorage.setItem('last_activity_at', String(now))
  scheduleIdleLogout()
}

const handleSessionCleared = () => authStore.clearSession()

activityEvents.forEach((eventName) => window.addEventListener(eventName, recordActivity, { passive: true }))
window.addEventListener('auth-session-cleared', handleSessionCleared)
document.addEventListener('visibilitychange', scheduleIdleLogout)

watch(
  () => authStore.token,
  (token) => {
    if (token && !sessionStorage.getItem('last_activity_at')) {
      sessionStorage.setItem('last_activity_at', String(Date.now()))
    }
    scheduleIdleLogout()
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  clearIdleTimer()
  activityEvents.forEach((eventName) => window.removeEventListener(eventName, recordActivity))
  window.removeEventListener('auth-session-cleared', handleSessionCleared)
  document.removeEventListener('visibilitychange', scheduleIdleLogout)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
}

body {
  background-color: #f5f7fa;
}
</style>
