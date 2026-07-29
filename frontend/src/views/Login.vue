<template>
  <div class="login-container">
    <div class="bg-gradient"></div>
    
    <div class="login-box">
      <div class="login-header">
        <h1>资产管理系统</h1>
        <p>Asset Management System</p>
      </div>
      
      <el-form ref="loginFormRef" :model="loginForm" :rules="rules" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名" size="large" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="密码" size="large" :prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item prop="captcha">
          <div class="captcha-wrapper">
            <el-input 
              v-model="loginForm.captcha" 
              placeholder="验证码" 
              size="large" 
              class="captcha-input"
              @keyup.enter="handleLogin"
            />
            <div class="captcha-display" @click="refreshCaptcha">
              <span class="captcha-text">{{ captchaText }}</span>
              <el-icon class="refresh-icon"><RefreshRight /></el-icon>
            </div>
          </div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" class="login-button" @click="handleLogin">登 录</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="page-footer">
      <p>开源资产管理模板 · 数据均为虚构示例</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { User, Lock, RefreshRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref(null)
const loading = ref(false)
const captchaText = ref('')

const loginForm = reactive({ username: '', password: '', captcha: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
}

const refreshCaptcha = async () => {
  try {
    console.log('[Login] Refreshing captcha...')
    const data = await authStore.refreshCaptcha()
    console.log('[Login] Captcha data received:', data)
    captchaText.value = data.question
    console.log('[Login] captchaText updated to:', captchaText.value)
  } catch (error) {
    console.error('[Login] Captcha refresh failed:', error)
    ElMessage.error('获取验证码失败，请检查网络连接')
  }
}

const handleLogin = async () => {
  if (!loginFormRef.value || loading.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      const response = await authStore.login(loginForm.username, loginForm.password, loginForm.captcha)
      ElMessage.success('登录成功')
      // 使用 setTimeout 确保 token 已保存到 localStorage
      setTimeout(() => {
        router.replace('/')
      }, 100)
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '登录失败')
      refreshCaptcha()
      loginForm.captcha = ''
    } finally {
      loading.value = false
    }
  })
}

onMounted(async () => {
  await refreshCaptcha()
})
</script>

<style scoped>
.login-container {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  overflow: hidden;
}

.bg-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 0;
}

.login-box {
  position: relative;
  z-index: 1;
  width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.login-header { text-align: center; margin-bottom: 30px; }
.login-header h1 { font-size: 28px; color: #333; margin-bottom: 8px; }
.login-header p { font-size: 14px; color: #999; }
.login-form { margin-top: 20px; }
.login-button { width: 100%; height: 45px; font-size: 16px; }

.page-footer {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1;
  text-align: center;
}

.page-footer p {
  font-size: 15px;
  color: #fff;
  margin: 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3), 0 0 8px rgba(0, 0, 0, 0.2);
  font-weight: 500;
  letter-spacing: 1px;
}

.captcha-wrapper {
  display: flex;
  width: 100%;
  gap: 10px;
}

.captcha-input {
  flex: 1;
}

.captcha-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 15px;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
  min-width: 120px;
  justify-content: center;
}

.captcha-display:hover {
  background: #ebeaea;
}

.captcha-text {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  letter-spacing: 2px;
}

.refresh-icon {
  color: #999;
  font-size: 16px;
}

.captcha-display:hover .refresh-icon {
  color: #667eea;
}
</style>
