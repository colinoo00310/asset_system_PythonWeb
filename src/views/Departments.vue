<template>
  <div class="departments-page">
    <div class="page-header">
      <h2 class="page-title">部门管理</h2>
      <div class="header-actions" v-if="authStore.isAdmin">
        <el-button type="primary" @click="showAddDialog"><el-icon><Plus /></el-icon> 添加部门</el-button>
        <el-button @click="exportExcel"><el-icon><Download /></el-icon> 导出Excel</el-button>
        <el-button @click="importExcel"><el-icon><Upload /></el-icon> 导入Excel</el-button>
        <el-button @click="downloadImportTemplate">下载导入模板</el-button>
        <input ref="excelImportInput" type="file" accept=".xlsx" style="display:none" @change="onExcelFileChange" />
      </div>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="关键词"><el-input v-model="searchKeyword" placeholder="搜索名称/地址/负责人" clearable /></el-form-item>
        <el-form-item><el-button type="primary" @click="fetchDepartments">搜索</el-button><el-button @click="searchKeyword = ''; fetchDepartments()">重置</el-button></el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="departments" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="部门名称" width="200" />
        <el-table-column prop="manager" label="负责人" width="100" align="center" />
        <el-table-column prop="contact" label="联系方式" width="150" />
        <el-table-column prop="address" label="地址" width="450" show-overflow-tooltip />
        <el-table-column prop="employee_count" label="员工数" width="90" align="center" />
        <el-table-column label="操作" width="310" align="center" fixed="right">
          <template #default="{ row }">
            <div class="operation-buttons">
              <el-button type="primary" link @click="viewDetail(row)">查看</el-button>
              <el-button type="primary" link @click="manageEmployees(row)">管理员工</el-button>
              <el-button v-if="authStore.isAdmin || authStore.isSectionChief" type="primary" link @click="editDepartment(row)">编辑</el-button>
              <el-button v-if="authStore.isAdmin" type="danger" link @click="deleteDepartment(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 部门添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="部门名称" prop="name"><el-input v-model="formData.name" :disabled="isEdit && !authStore.isAdmin" /></el-form-item>
        <el-form-item label="负责人" prop="manager"><el-input v-model="formData.manager" :disabled="isEdit && !authStore.isAdmin" /></el-form-item>
        <el-form-item label="联系方式" prop="contact"><el-input v-model="formData.contact" /></el-form-item>
        <el-form-item label="地址" prop="address"><el-input v-model="formData.address" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button></template>
    </el-dialog>

    <!-- 部门详情对话框 -->
    <el-dialog v-model="detailVisible" :title="`部门详情 - ${currentDept?.name}`" width="600px">
      <el-descriptions v-if="currentDept" :column="1" border>
        <el-descriptions-item label="部门名称">{{ currentDept.name }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ currentDept.manager }}</el-descriptions-item>
        <el-descriptions-item label="联系方式">{{ currentDept.contact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="地址">{{ currentDept.address }}</el-descriptions-item>
        <el-descriptions-item label="员工数量">{{ currentDept.employee_count }} 人</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentDept.created_at || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="manageEmployeesFromDetail">管理员工</el-button>
      </template>
    </el-dialog>

    <!-- 员工管理对话框 -->
    <el-dialog v-model="empDialogVisible" :title="`员工管理 - ${currentDept?.name}`" width="800px" destroy-on-close>
      <div class="emp-toolbar">
        <el-button type="primary" size="small" @click="showAddEmployee" v-if="authStore.isAdmin || authStore.isSectionChief">
          <el-icon><Plus /></el-icon> 添加员工
        </el-button>
        <el-button size="small" @click="fetchDeptEmployees">刷新</el-button>
      </div>
      <el-table :data="deptEmployees" v-loading="empLoading" stripe size="small">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="position" label="职位" width="150" />
        <el-table-column prop="contact" label="联系方式" width="150" />
        <el-table-column prop="sort_order" label="排序号" width="80" align="center" />
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editEmployee(row)">编辑</el-button>
            <el-button v-if="authStore.isAdmin" type="danger" link size="small" @click="deleteEmployee(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- 员工添加/编辑对话框 -->
      <el-dialog v-model="empFormVisible" :title="empDialogTitle" width="450px" append-to-body>
        <el-form ref="empFormRef" :model="empFormData" :rules="empFormRules" label-width="90px">
          <el-form-item label="姓名" prop="name"><el-input v-model="empFormData.name" /></el-form-item>
          <el-form-item label="职位" prop="position"><el-input v-model="empFormData.position" /></el-form-item>
          <el-form-item label="联系方式"><el-input v-model="empFormData.contact" /></el-form-item>
          <el-form-item label="排序号"><el-input-number v-model="empFormData.sort_order" :min="0" style="width: 100%" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="empFormVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEmployee" :loading="empSubmitting">保存</el-button>
        </template>
      </el-dialog>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Upload } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const loading = ref(false), dialogVisible = ref(false), detailVisible = ref(false)
const submitting = ref(false), empDialogVisible = ref(false), empLoading = ref(false)
const empFormVisible = ref(false), empSubmitting = ref(false)
const dialogTitle = ref('添加部门'), empDialogTitle = ref('添加员工')
const isEdit = ref(false), isEmpEdit = ref(false), formRef = ref(null), empFormRef = ref(null)
const departments = ref([]), searchKeyword = ref(''), currentDept = ref(null), currentDeptId = ref(null)
const deptEmployees = ref([]), currentEmpId = ref(null)
const excelImportInput = ref(null)

const formData = reactive({ name: '', manager: '', contact: '', address: '' })
const formRules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
  manager: [{ required: true, message: '请输入负责人', trigger: 'blur' }],
  address: [{ required: true, message: '请输入地址', trigger: 'blur' }]
}

const empFormData = reactive({ name: '', position: '', contact: '', sort_order: 0 })
const empFormRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }]
}

const fetchDepartments = async () => {
  loading.value = true
  try {
    const res = await api.get('/departments', { params: { search: searchKeyword.value } })
    departments.value = res.departments || []
  } catch (error) {
    console.error('获取部门列表失败:', error)
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  dialogTitle.value = '添加部门'
  currentDeptId.value = null
  Object.assign(formData, { name: '', manager: '', contact: '', address: '' })
  dialogVisible.value = true
}

const editDepartment = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑部门'
  currentDeptId.value = row.id
  Object.assign(formData, { name: row.name, manager: row.manager, contact: row.contact || '', address: row.address })
  dialogVisible.value = true
}

const viewDetail = (row) => {
  currentDept.value = row
  currentDeptId.value = row.id
  detailVisible.value = true
}

const manageEmployees = (row) => {
  currentDept.value = row
  currentDeptId.value = row.id
  empDialogVisible.value = true
  fetchDeptEmployees()
}

const manageEmployeesFromDetail = () => {
  detailVisible.value = false
  empDialogVisible.value = true
  fetchDeptEmployees()
}

const fetchDeptEmployees = async () => {
  empLoading.value = true
  try {
    const res = await api.get('/employees', { params: { department_id: currentDeptId.value } })
    deptEmployees.value = res.employees || []
  } catch (error) {
    console.error('获取员工列表失败:', error)
  } finally {
    empLoading.value = false
  }
}

const showAddEmployee = () => {
  isEmpEdit.value = false
  empDialogTitle.value = '添加员工'
  currentEmpId.value = null
  Object.assign(empFormData, { name: '', position: '', contact: '', sort_order: 0 })
  empFormVisible.value = true
}

const editEmployee = (row) => {
  isEmpEdit.value = true
  empDialogTitle.value = '编辑员工'
  currentEmpId.value = row.id
  Object.assign(empFormData, {
    name: row.name,
    position: row.position || '',
    contact: row.contact || '',
    sort_order: row.sort_order || 0
  })
  empFormVisible.value = true
}

const deleteEmployee = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除员工 "${row.name}" 吗？`, '提示', { type: 'warning' })
    await api.delete(`/employees/${row.id}`)
    ElMessage.success('删除成功')
    fetchDeptEmployees()
    fetchDepartments()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

const submitEmployee = async () => {
  if (!empFormRef.value) return
  await empFormRef.value.validate(async (valid) => {
    if (valid) {
      empSubmitting.value = true
      try {
        const data = { ...empFormData, department_id: currentDeptId.value }
        if (isEmpEdit.value) {
          await api.put(`/employees/${currentEmpId.value}`, data)
          ElMessage.success('更新成功')
        } else {
          await api.post('/employees', data)
          ElMessage.success('添加成功')
        }
        empFormVisible.value = false
        fetchDeptEmployees()
        fetchDepartments()
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '操作失败')
      } finally {
        empSubmitting.value = false
      }
    }
  })
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await api.put(`/departments/${currentDeptId.value}`, formData)
          ElMessage.success('更新成功')
        } else {
          await api.post('/departments', formData)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        fetchDepartments()
      } catch (error) {
        ElMessage.error(error.response?.data?.error || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const deleteDepartment = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除部门“${row.name}”吗？部门下存在员工时系统会阻止删除。`,
      '删除部门',
      { type: 'warning' }
    )
    await api.delete(`/departments/${row.id}`)
    ElMessage.success('部门删除成功')
    await fetchDepartments()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error(error.response?.data?.error || '删除失败')
  }
}

const exportExcel = async () => {
  try {
    const blob = await api.get('/departments/export', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([blob]))
    const link = document.createElement('a')
    link.href = url
    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14)
    link.download = `部门员工列表_${timestamp}.xlsx`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '导出失败')
  }
}

const importExcel = () => {
  excelImportInput.value?.click()
}

const downloadImportTemplate = async () => {
  try {
    const blob = await api.get('/departments/import-template', { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([blob])); const link = document.createElement('a')
    link.href = url; link.download = '部门员工导入模板.xlsx'; link.click(); URL.revokeObjectURL(url)
  } catch (error) { ElMessage.error('模板下载失败') }
}

const onExcelFileChange = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return

  const data = new FormData()
  data.append('file', file)
  try {
    const result = await api.post('/departments/import', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success(
      `导入完成：新增部门 ${result.departments_imported || 0} 个，新增员工 ${result.employees_imported || 0} 名`
    )
    const duplicates = (result.duplicate_departments || 0) + (result.duplicate_employees || 0)
    if (duplicates) ElMessage.info(`已跳过重复数据 ${duplicates} 条`)
    await fetchDepartments()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '导入失败')
  } finally {
    event.target.value = ''
  }
}

onMounted(() => { fetchDepartments() })
</script>

<style scoped>
.departments-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { margin: 0; color: #303133; font-size: 24px; }
.filter-card, .table-card { margin-bottom: 20px; }
.emp-toolbar { display: flex; gap: 10px; margin-bottom: 16px; }
.operation-buttons { display: flex; align-items: center; justify-content: center; flex-wrap: nowrap; white-space: nowrap; }
.operation-buttons :deep(.el-button + .el-button) { margin-left: 14px; }
</style>
