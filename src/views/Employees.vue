<template>
  <div class="employees-page">
    <div class="page-header">
      <h2 class="page-title">员工管理</h2>
      <div class="header-actions"><el-button type="primary" @click="showAddDialog" v-if="authStore.isAdmin"><el-icon><Plus /></el-icon> 添加员工</el-button></div>
    </div>
    
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="所属部门">
          <el-select v-model="filterDeptId" placeholder="选择部门" clearable @change="fetchEmployees">
            <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="table-card">
      <el-table :data="employees" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="position" label="职位" width="150" />
        <el-table-column prop="department_name" label="所属部门" width="150" />
        <el-table-column prop="contact" label="联系方式" width="150" />
        <el-table-column prop="sort_order" label="排序号" width="80" align="center" />
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="editEmployee(row)">编辑</el-button>
            <el-button v-if="authStore.isAdmin" type="danger" link @click="deleteEmployee(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="姓名" prop="name"><el-input v-model="formData.name" /></el-form-item>
        <el-form-item label="职位" prop="position"><el-input v-model="formData.position" /></el-form-item>
        <el-form-item label="所属部门" prop="department_id">
          <el-select v-model="formData.department_id" placeholder="选择部门" style="width: 100%">
            <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系方式"><el-input v-model="formData.contact" /></el-form-item>
        <el-form-item label="排序号"><el-input-number v-model="formData.sort_order" :min="0" style="width: 100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const loading = ref(false), dialogVisible = ref(false), submitting = ref(false), dialogTitle = ref('添加员工'), isEdit = ref(false), formRef = ref(null)
const employees = ref([]), departments = ref([]), filterDeptId = ref(null), currentEmpId = ref(null)
const formData = reactive({ name: '', position: '', department_id: null, contact: '', sort_order: 0 })
const formRules = { name: [{ required: true, message: '请输入姓名', trigger: 'blur' }], department_id: [{ required: true, message: '请选择部门', trigger: 'change' }] }

const fetchEmployees = async () => {
  loading.value = true
  try { const params = filterDeptId.value ? { department_id: filterDeptId.value } : {}; const res = await api.get('/employees', { params }); employees.value = res.employees || [] } catch (error) { console.error('获取员工列表失败:', error) } finally { loading.value = false }
}

const fetchDepartments = async () => { try { const res = await api.get('/departments'); departments.value = res.departments || [] } catch (error) { console.error('获取部门列表失败:', error) } }

const showAddDialog = () => { isEdit.value = false; dialogTitle.value = '添加员工'; currentEmpId.value = null; Object.assign(formData, { name: '', position: '', department_id: null, contact: '', sort_order: 0 }); dialogVisible.value = true }
const editEmployee = (row) => { isEdit.value = true; dialogTitle.value = '编辑员工'; currentEmpId.value = row.id; Object.assign(formData, { name: row.name, position: row.position || '', department_id: row.department_id, contact: row.contact || '', sort_order: row.sort_order || 0 }); dialogVisible.value = true }
const deleteEmployee = async (row) => { try { await ElMessageBox.confirm(`确定要删除员工 "${row.name}" 吗？`, '提示', { type: 'warning' }); await api.delete(`/employees/${row.id}`); ElMessage.success('删除成功'); fetchEmployees() } catch (error) { if (error !== 'cancel') ElMessage.error('删除失败') } }

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try { if (isEdit.value) { await api.put(`/employees/${currentEmpId.value}`, formData); ElMessage.success('更新成功') } else { await api.post('/employees', formData); ElMessage.success('添加成功') }; dialogVisible.value = false; fetchEmployees() } catch (error) { ElMessage.error(error.response?.data?.error || '操作失败') } finally { submitting.value = false }
    }
  })
}

onMounted(() => { fetchEmployees(); fetchDepartments() })
</script>

<style scoped>
.employees-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { margin: 0; color: #303133; font-size: 24px; }
.filter-card, .table-card { margin-bottom: 20px; }
</style>
