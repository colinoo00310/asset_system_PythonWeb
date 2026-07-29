<template>
  <div class="users-page">
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showAddDialog"><el-icon><Plus /></el-icon> 添加用户</el-button>
      </div>
    </div>
    
    <el-card class="table-card">
      <el-table :data="users" v-loading="loading" stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="100" align="center" />
        <el-table-column prop="username" label="用户名" min-width="180" />
        <el-table-column prop="role" label="角色" width="140" align="center">
          <template #default="{ row }"><el-tag :type="getRoleType(row.role)">{{ getRoleName(row.role) }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="full_name" label="姓名" min-width="180" />
        <el-table-column prop="department_name" label="所属部门" min-width="220"><template #default="{ row }">{{ row.department_name || '-' }}</template></el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="editUser(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteUser(row)" :disabled="row.id === currentUserId">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="用户名" prop="username"><el-input v-model="formData.username" :disabled="isEdit" /></el-form-item>
        <el-form-item :label="isEdit ? '新密码' : '密码'" prop="password"><el-input v-model="formData.password" type="password" show-password :placeholder="isEdit ? '不修改请留空' : ''" /></el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" style="width: 100%">
            <el-option label="管理员" value="admin" /><el-option label="科长" value="section_chief" /><el-option label="员工" value="staff" />
          </el-select>
        </el-form-item>
        <el-form-item label="姓名"><el-input v-model="formData.full_name" /></el-form-item>
        <el-form-item label="所属部门">
          <el-select v-model="formData.department_id" placeholder="选择部门" clearable style="width: 100%">
            <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const loading = ref(false), dialogVisible = ref(false), submitting = ref(false), dialogTitle = ref('添加用户'), isEdit = ref(false), formRef = ref(null)
const users = ref([]), departments = ref([])
const currentUserId = computed(() => authStore.user?.id)
const formData = reactive({ username: '', password: '', role: 'staff', full_name: '', department_id: null })
const formRules = computed(() => ({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: !isEdit.value, message: '请输入密码', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}))

const getRoleName = (role) => ({ 'admin': '管理员', 'section_chief': '科长', 'staff': '员工' })[role] || role
const getRoleType = (role) => ({ 'admin': 'danger', 'section_chief': 'warning', 'staff': 'success' })[role] || 'info'

const fetchUsers = async () => { loading.value = true; try { const res = await api.get('/users'); users.value = res.users || [] } catch (error) { console.error('获取用户列表失败:', error) } finally { loading.value = false } }
const fetchDepartments = async () => { try { const res = await api.get('/departments'); departments.value = res.departments || [] } catch (error) { console.error('获取部门列表失败:', error) } }

const showAddDialog = () => { isEdit.value = false; dialogTitle.value = '添加用户'; Object.assign(formData, { username: '', password: '', role: 'staff', full_name: '', department_id: null }); dialogVisible.value = true }
const editUser = (row) => { isEdit.value = true; dialogTitle.value = '编辑用户'; Object.assign(formData, { username: row.username, password: '', role: row.role, full_name: row.full_name || '', department_id: row.department_id }); dialogVisible.value = true }
const deleteUser = async (row) => { if (row.id === currentUserId.value) { ElMessage.error('不能删除当前登录的用户'); return } try { await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '提示', { type: 'warning' }); await api.delete(`/users/${row.id}`); ElMessage.success('删除成功'); fetchUsers() } catch (error) { if (error !== 'cancel') ElMessage.error('删除失败') } }

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const data = { ...formData }
        if (!data.password) delete data.password
        if (isEdit.value) { await api.put(`/users/${users.value.find(u => u.username === formData.username)?.id}`, data); ElMessage.success('更新成功') }
        else { await api.post('/users', data); ElMessage.success('添加成功') }
        dialogVisible.value = false; fetchUsers()
      } catch (error) { ElMessage.error(error.response?.data?.error || '操作失败') } finally { submitting.value = false }
    }
  })
}

onMounted(() => { fetchUsers(); fetchDepartments() })
</script>

<style scoped>
.users-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { margin: 0; color: #303133; font-size: 24px; }
.table-card { margin-bottom: 20px; }
.table-card :deep(.el-card__body) { padding: 20px; }
.el-table { width: 100%; }
.el-table :deep(.el-table__body-wrapper) { overflow-y: auto; }
.el-table :deep(.el-table__cell) { padding: 12px 16px !important; }
</style>
