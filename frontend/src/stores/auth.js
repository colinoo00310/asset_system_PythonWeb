import { defineStore } from 'pinia'
import api from '@/utils/api'

// 旧版本使用 localStorage 持久保存登录状态。升级后清除旧记录，
// 避免关闭浏览器后仍自动登录。
localStorage.removeItem('token')
localStorage.removeItem('user')

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: sessionStorage.getItem('token') || null,
    user: JSON.parse(sessionStorage.getItem('user') || 'null'),
    permissions: {},
    captchaId: null,
    captchaAnswer: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
    isSectionChief: (state) => state.user?.role === 'section_chief',
    isStaff: (state) => state.user?.role === 'staff'
  },

  actions: {
    clearSession() {
      this.token = null
      this.user = null
      this.permissions = {}
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('user')
      sessionStorage.removeItem('last_activity_at')
    },

    async refreshCaptcha() {
      console.log('[Auth Store] Refreshing captcha...')
      const response = await api.get('/auth/captcha')
      console.log('[Auth Store] Captcha response:', response)
      this.captchaId = response.captcha_id
      return { question: response.question }
    },

    async login(username, password, captchaInput) {
      const response = await api.post('/auth/login', { 
        username, 
        password,
        captcha_id: this.captchaId,
        captcha: captchaInput
      })
      this.token = response.token
      this.user = response.user
      sessionStorage.setItem('token', response.token)
      sessionStorage.setItem('user', JSON.stringify(response.user))
      sessionStorage.setItem('last_activity_at', String(Date.now()))
    },

    async logout() {
      try { await api.post('/auth/logout') } catch (e) {}
      this.clearSession()
    },

    async fetchCurrentUser() {
      const response = await api.get('/auth/me')
      this.user = response
      this.permissions = response.permissions || {}
      sessionStorage.setItem('user', JSON.stringify(response))
      return response
    }
  }
})
