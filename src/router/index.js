import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/Dashboard.vue') },
      { path: 'assets', name: 'Assets', component: () => import('@/views/Assets.vue') },
      { path: 'assets/:id', name: 'AssetDetail', component: () => import('@/views/AssetDetail.vue'), props: true },
      { path: 'departments', name: 'Departments', component: () => import('@/views/Departments.vue') },
      { path: 'employees', name: 'Employees', component: () => import('@/views/Employees.vue') },
      { path: 'map', name: 'AssetMap', component: () => import('@/views/AssetMap.vue') },
      { path: 'users', name: 'Users', component: () => import('@/views/Users.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth !== false) {
    const token = sessionStorage.getItem('token')
    if (!token) {
      next('/login')
      return
    }
  }
  if (to.path === '/login') {
    const token = sessionStorage.getItem('token')
    if (token) {
      next('/')
      return
    }
  }
  next()
})

export default router
