<template>
  <div class="main-layout">
    <el-container>
      <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
        <div class="logo" :class="{ collapse: isCollapse }">
          <h2 v-if="!isCollapse" class="logo-text">资产管理系统</h2>
          <span v-else class="logo-text">资系</span>
        </div>
        
        <el-menu :default-active="activeMenu" :collapse="isCollapse" :router="true"
          background-color="#304156" text-color="#bfcbd9" active-text-color="#409EFF">
          <el-menu-item index="/"><el-icon><HomeFilled /></el-icon><template #title>首页</template></el-menu-item>
          <el-menu-item index="/assets"><el-icon><Box /></el-icon><template #title>资产管理</template></el-menu-item>
          <el-menu-item index="/departments"><el-icon><OfficeBuilding /></el-icon><template #title>部门管理</template></el-menu-item>
          <el-menu-item index="/map"><el-icon><Location /></el-icon><template #title>资产地图</template></el-menu-item>
          <el-menu-item v-if="authStore.isAdmin" index="/users"><el-icon><Setting /></el-icon><template #title>用户管理</template></el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
              <Fold v-if="!isCollapse" /><Expand v-else />
            </el-icon>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-icon><Avatar /></el-icon>
                <span>{{ authStore.user?.full_name || authStore.user?.username }}</span>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout" divided><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { HomeFilled, Box, OfficeBuilding, Setting, Fold, Expand, Avatar, SwitchButton, Location } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isCollapse = ref(false)

const activeMenu = computed(() => route.path)

const roleName = computed(() => {
  const roles = { 'admin': '管理员', 'section_chief': '科长', 'staff': '员工' }
  return roles[authStore.user?.role] || authStore.user?.role
})

const handleCommand = async (command) => {
  if (command === 'logout') {
    await authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}

// 初始化用户信息
onMounted(async () => {
  if (!authStore.user) {
    try {
      await authStore.fetchCurrentUser()
    } catch (e) {
      console.error('获取用户信息失败')
    }
  }
})
</script>

<style scoped>
.main-layout { height: 100vh; min-width: 0; }
.el-container { min-width: 0; }
.aside { background-color: #304156; transition: width 0.3s; overflow: hidden; flex-shrink: 0; }
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4d;
  color: white;
  font-size: 18px;
  font-weight: bold;
  transition: all 0.3s;
  white-space: nowrap;
  overflow: hidden;
}
.logo-text { color: white; font-size: 18px; margin: 0; text-align: center; }
.logo.collapse .logo-text { font-size: 16px; }
.header { display: flex; align-items: center; justify-content: space-between; background-color: white; box-shadow: 0 1px 4px rgba(0,0,0,0.08); padding: 0 20px; flex-shrink: 0; }
.header-left { display: flex; align-items: center; }
.collapse-btn { font-size: 20px; cursor: pointer; color: #606266; }
.collapse-btn:hover { color: #409EFF; }
.header-right { display: flex; align-items: center; }
.user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; padding: 0 10px; }
.main-content { padding: 20px; background-color: #f5f7fa; overflow: auto; min-width: 0; flex: 1; display: flex; flex-direction: column; }
:deep(.el-menu--collapse) { width: 64px; }
:deep(.el-menu) { border-right: none; }
</style>
