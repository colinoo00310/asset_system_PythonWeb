<template>
  <div class="assets-page">
    <div class="page-header">
      <h2 class="page-title">资产管理</h2>
        <div class="header-actions">
          <el-button type="primary" @click="showAddDialog"><el-icon><Plus /></el-icon> 添加资产</el-button>
          <el-button @click="exportExcel"><el-icon><Download /></el-icon> 导出Excel</el-button>
          <el-button @click="importExcel"><el-icon><Upload /></el-icon> 导入Excel</el-button>
          <el-button @click="downloadImportTemplate">下载导入模板</el-button>
          <el-button @click="showReminders('lease')"><el-icon><Bell /></el-icon> 租赁提醒</el-button>
          <el-button @click="showReminders('trusteeship')"><el-icon><Bell /></el-icon> 托管提醒</el-button>
          <input id="excelImport" type="file" accept=".xlsx,.xls" style="display:none" @change="onExcelFileChange" />
        </div>
    </div>
    
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="关键词"><el-input v-model="filterForm.search" placeholder="搜索资产信息" clearable /></el-form-item>
        <el-form-item label="分类" style="width: 220px; flex: 0 0 220px;">
          <el-select v-model="filterForm.category" placeholder="选择分类" clearable style="width: 100%;">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item><el-button type="primary" @click="searchAssets">搜索</el-button><el-button @click="resetFilter">重置</el-button></el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="table-card">
      <el-table :data="assets" v-loading="loading" stripe>
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="资产名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="management_type" label="管理类型" width="110" align="center" />
        <el-table-column prop="lease_status" label="租赁状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.management_type === '租赁管理'" :type="getLeaseStatusType(row.lease_status)">{{ row.lease_status || '租赁中' }}</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100" align="center" />
        <el-table-column prop="quantity" label="数量" width="70" align="center" />
        <el-table-column prop="responsible_person" label="负责人" width="100" align="center" />
        <el-table-column prop="location" label="资产地址" min-width="220">
          <template #default="{ row }">
            <el-link v-if="row.location" type="primary" @click.prevent="openMapFromList(row)">{{ row.location }}</el-link>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }"><el-tag :type="getStatusType(row.status)">{{ row.status || '未设置' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="department_name" label="所属部门" width="120" align="center" />
        <el-table-column prop="asset_number" label="资产编号" width="120" />
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">查看</el-button>
            <el-button type="primary" link @click="editAsset(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteAsset(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.per_page" :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" @size-change="handleSizeChange" @current-change="handlePageChange" />
      </div>
    </el-card>
    
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="960px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <div class="form-section">
          <div class="section-title">基本信息</div>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="资产名称" prop="name"><el-input v-model="formData.name" /></el-form-item></el-col>
            <el-col :span="12">
              <el-form-item label="资产分类" prop="category">
                <el-select v-model="formData.category" style="width: 100%" @change="onCategoryChange">
                  <el-option label="房屋资产" value="房屋资产" />
                  <el-option label="办公资产" value="办公资产" />
                  <el-option label="其他资产" value="其他资产" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="资产编号" prop="asset_number"><el-input v-model="formData.asset_number" /></el-form-item></el-col>
            <el-col :span="12">
              <el-form-item label="管理类型">
                <el-select v-model="formData.management_type" style="width: 100%" @change="onManagementTypeChange">
                  <el-option label="自主管理" value="自主管理" />
                  <el-option label="租赁管理" value="租赁管理" />
                  <el-option label="托管管理" value="托管管理" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="数量"><el-input-number v-model="formData.quantity" :min="1" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="资产价值"><el-input v-model="formData.market_value" placeholder="请输入金额" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="负责人" prop="responsible_person"><el-input v-model="formData.responsible_person" /></el-form-item></el-col>
            <el-col :span="12">
              <el-form-item label="资产地址" prop="location">
                <el-input v-model="formData.location" placeholder="请输入资产详细地址" clearable />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="购置日期"><el-date-picker v-model="formData.purchase_date" type="date" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="12">
              <el-form-item label="状态">
                <el-select v-model="formData.status" style="width: 100%">
                  <el-option label="使用中" value="使用中" /><el-option label="闲置" value="闲置" /><el-option label="已报废" value="已报废" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="经度" prop="longitude">
                <el-input v-model="formData.longitude" placeholder="如：120.293000（-180～180）" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="纬度" prop="latitude">
                <el-input v-model="formData.latitude" placeholder="如：30.243000（-90～90）" clearable />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="备注"><el-input v-model="formData.notes" type="textarea" :rows="3" /></el-form-item>
        </div>

        <div v-if="formData.category === '房屋资产'" class="form-section">
          <div class="section-title">房屋信息</div>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="产证情况"><el-input v-model="formData.certificate_status" placeholder="如房产证、土地证信息" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="产权单位"><el-input v-model="formData.property_unit" placeholder="请输入产权单位名称" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="建筑面积">
                <div class="unit-input">
                  <el-input v-model="formData.building_area" placeholder="请输入建筑面积" style="width: calc(100% - 60px)" />
                  <span class="input-unit">平方米</span>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div v-if="formData.management_type === '租赁管理'" class="form-section">
          <div class="section-title">租赁信息</div>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="租赁开始日期"><el-date-picker v-model="formData.lease_start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="租赁结束日期"><el-date-picker v-model="formData.lease_end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="租赁状态">
                <el-select v-model="formData.lease_status" style="width: 100%" clearable>
                  <el-option label="未开始" value="未开始" />
                  <el-option label="租赁中" value="租赁中" />
                  <el-option label="已到期" value="已到期" />
                  <el-option label="已解约" value="已解约" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12"><el-form-item label="提前提醒天数"><el-input-number v-model="formData.lease_reminder_days" :min="1" :max="365" style="width: 100%" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="承租方联系方式"><el-input v-model="formData.tenant_contact" placeholder="输入电话或手机号" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="公开招拍租情况"><el-input v-model="formData.bidding_situation" placeholder="如：公开拍租/公开拍租中" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="承租方性质">
                <el-select v-model="formData.tenant_nature" style="width: 100%" clearable>
                  <el-option label="个人" value="个人" />
                  <el-option label="公司" value="公司" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12"><el-form-item label="承租方用途"><el-input v-model="formData.tenant_purpose" placeholder="如经营XX店铺等" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="租金金额">
                <div class="unit-input">
                  <el-input v-model="formData.rent_amount" placeholder="请输入租金金额" style="width: calc(100% - 40px)" />
                  <span class="input-unit">元</span>
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="12"><el-form-item label="租金交付方式"><el-input v-model="formData.rent_payment_method" placeholder="如：半年交/全年交" /></el-form-item></el-col>
          </el-row>
        </div>

        <div v-if="formData.management_type === '托管管理'" class="form-section">
          <div class="section-title">托管信息</div>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="合同类型"><el-input v-model="formData.trusteeship_contract_type" placeholder="请输入合同类型" /></el-form-item></el-col>
            <el-col :span="12">
              <el-form-item label="合同金额">
                <div class="unit-input">
                  <el-input v-model="formData.trusteeship_contract_amount" placeholder="请输入合同金额" style="width: calc(100% - 40px)" />
                  <span class="input-unit">元</span>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="合同相对方"><el-input v-model="formData.trusteeship_counterparty" placeholder="请输入合同相对方名称" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="合同编号"><el-input v-model="formData.trusteeship_contract_number" placeholder="请输入合同编号" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="合同开始日期"><el-date-picker v-model="formData.trusteeship_start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="12"><el-form-item label="合同结束日期"><el-date-picker v-model="formData.trusteeship_end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12"><el-form-item label="签署日期"><el-date-picker v-model="formData.trusteeship_sign_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item></el-col>
            <el-col :span="12">
              <el-form-item label="是否归档">
                <el-select v-model="formData.trusteeship_is_archived" style="width: 100%" clearable>
                  <el-option label="已归档" value="已归档" />
                  <el-option label="未归档" value="未归档" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
        <div class="form-section">
          <div class="section-title">资产图片（最多3张）</div>
          <el-upload v-model:file-list="imageFiles" list-type="picture-card" :auto-upload="false"
            accept=".png,.jpg,.jpeg,.gif,.bmp,.webp" :limit="3" multiple :on-preview="handleImagePreview">
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="image-tip">编辑时选择新图片会替换原有图片；不选择则保留原图片。</div>
        </div>
      </el-form>
      <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button></template>
    </el-dialog>

    <el-dialog v-model="imagePreviewVisible" title="图片预览" width="70%" append-to-body>
      <div class="image-preview-container">
        <el-image :src="imagePreviewUrl" fit="contain" :preview-src-list="[imagePreviewUrl]" />
      </div>
    </el-dialog>

    <el-dialog v-model="reminderVisible" :title="reminderType === 'lease' ? '租赁提醒' : '托管提醒'" width="760px">
      <el-table :data="reminders[reminderType]" stripe max-height="400">
        <el-table-column v-if="reminderType === 'lease'" prop="name" label="资产名称" min-width="140" />
        <el-table-column v-if="reminderType === 'lease'" prop="status" label="租赁状态" width="110" align="center" />
        <el-table-column v-if="reminderType === 'lease'" prop="end_date" label="结束日期" width="120" />
        <el-table-column v-if="reminderType === 'lease'" prop="days" label="剩余天数" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getReminderTagType(row.days)">{{ formatDays(row.days) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="reminderType === 'lease'" prop="tenant_name" label="承租方" width="140" />
        <el-table-column v-if="reminderType === 'lease'" prop="contact" label="联系方式" width="170" />

        <el-table-column v-if="reminderType === 'trusteeship'" prop="name" label="资产名称" min-width="160" />
        <el-table-column v-if="reminderType === 'trusteeship'" prop="end_date" label="结束日期" width="120" />
        <el-table-column v-if="reminderType === 'trusteeship'" prop="days" label="剩余天数" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getReminderTagType(row.days)">{{ formatDays(row.days) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="reminderType === 'trusteeship'" prop="counterparty" label="相对方" width="170" />
        <el-table-column v-if="reminderType === 'trusteeship'" prop="contract_number" label="合同编号" width="170" />
      </el-table>
      <template #footer><el-button @click="reminderVisible = false">关闭</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const loading = ref(false), dialogVisible = ref(false), submitting = ref(false)
const dialogTitle = ref('添加资产'), isEdit = ref(false), formRef = ref(null)
const assets = ref([]), categories = ref([]), currentAssetId = ref(null)

const filterForm = reactive({ search: '', category: '' })
const pagination = reactive({ page: 1, per_page: 20, total: 0 })

const queryText = (value) => Array.isArray(value) ? (value[0] || '') : (value || '')
const positiveInt = (value, fallback) => {
  const parsed = Number.parseInt(queryText(value), 10)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback
}
const listQuery = () => ({
  ...(filterForm.search ? { search: filterForm.search } : {}),
  ...(filterForm.category ? { category: filterForm.category } : {}),
  page: String(pagination.page),
  per_page: String(pagination.per_page)
})
const syncListQuery = () => router.replace({ name: 'Assets', query: listQuery() })
const reminderVisible = ref(false)
const reminderType = ref('lease')
const reminders = reactive({ lease: [], trusteeship: [] })
const imageFiles = ref([])
const imagePreviewVisible = ref(false)
const imagePreviewUrl = ref('')
const handleImagePreview = (file) => {
  imagePreviewUrl.value = file.url || (file.raw ? URL.createObjectURL(file.raw) : '')
  if (imagePreviewUrl.value) imagePreviewVisible.value = true
}
const formData = reactive({
  name: '', category: '', asset_number: '', management_type: '自主管理', quantity: 1,
  model: '', purchase_date: '', market_value: '', responsible_person: '', location: '', status: '使用中', notes: '',
  longitude: '', latitude: '', coord_type: 'gcj02',
  certificate_status: '', property_unit: '', building_area: '',
  lease_start_date: '', lease_end_date: '', lease_reminder_days: 30, lease_status: '租赁中',
  tenant_name: '', tenant_contact: '', tenant_nature: '个人', tenant_purpose: '',
  rent_amount: '', rent_payment_method: '', bidding_situation: '',
  trusteeship_contract_type: '', trusteeship_contract_amount: '',
  trusteeship_counterparty: '', trusteeship_contract_number: '',
  trusteeship_start_date: '', trusteeship_end_date: '', trusteeship_sign_date: '', trusteeship_is_archived: ''
})
const coordinateValidator = (min, max, pairedField, label) => (_rule, value, callback) => {
  const empty = value === '' || value === null || value === undefined
  const pairedEmpty = formData[pairedField] === '' || formData[pairedField] === null || formData[pairedField] === undefined
  if (empty && pairedEmpty) return callback()
  if (empty) return callback(new Error(`${label}不能为空，经纬度需要同时填写`))
  const number = Number(value)
  if (!Number.isFinite(number) || number < min || number > max) {
    return callback(new Error(`${label}必须在 ${min}～${max} 之间`))
  }
  callback()
}

const formRules = {
  name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  asset_number: [{ required: true, message: '请输入资产编号', trigger: 'blur' }],
  responsible_person: [{ required: true, message: '请输入负责人', trigger: 'blur' }],
  location: [{ required: true, message: '请输入资产地址', trigger: 'blur' }],
  longitude: [{ validator: coordinateValidator(-180, 180, 'latitude', '经度'), trigger: 'blur' }],
  latitude: [{ validator: coordinateValidator(-90, 90, 'longitude', '纬度'), trigger: 'blur' }]
}

const getStatusType = (status) => ({ '使用中': 'success', '闲置': 'warning', '已报废': 'danger' })[status] || 'info'
const getLeaseStatusType = (lease_status) => ({ '租赁中': 'success', '未开始': 'info', '已到期': 'warning', '已解约': 'danger' })[lease_status] || 'info'
const getReminderTagType = (days) => {
  if (days == null) return 'info'
  if (days < 0) return 'danger'
  if (days <= 30) return 'warning'
  return 'success'
}
const formatDays = (days) => {
  if (days == null) return '日期无效'
  if (days < 0) return `已过期 ${Math.abs(days)} 天`
  return `剩余 ${days} 天`
}

const openMapFromList = (row) => {
  const address = (row.location || '').trim()
  if (!address) {
    ElMessage.warning('该资产未填写地址')
    return
  }
  const encoded = encodeURIComponent(address)
  window.open(`https://map.baidu.com/search?querytype=s&wd=${encoded}`, '_blank')
}

const fetchAssets = async () => {
  loading.value = true
  try {
    const params = { page: pagination.page, per_page: pagination.per_page, search: filterForm.search, category: filterForm.category }
    const res = await api.get('/assets', { params })
    assets.value = res.assets
    pagination.total = res.total
  } catch (error) { console.error('获取资产列表失败:', error) } finally { loading.value = false }
}

const searchAssets = () => {
  pagination.page = 1
  syncListQuery()
  fetchAssets()
}

const handlePageChange = () => {
  syncListQuery()
  fetchAssets()
}

const handleSizeChange = () => {
  pagination.page = 1
  syncListQuery()
  fetchAssets()
}

const fetchCategories = async () => {
  try { const res = await api.get('/assets/categories'); categories.value = res.categories || [] } catch (error) { console.error('获取分类失败:', error) }
}

const exportExcel = async () => {
  try {
    const response = await api.get('/assets/export', { responseType: 'blob' })
    const blob = new Blob([response])
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14)
    a.download = `资产清单_${timestamp}.xlsx`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败', error)
    const status = error.response?.status
    const message = error.response?.data?.error || (status ? `导出失败 (${status})` : '导出失败')
    ElMessage.error(message)
  }
}

const importExcel = () => {
  document.getElementById('excelImport')?.click()
}

const downloadImportTemplate = async () => {
  try {
    const blob = await api.get('/assets/import-template', { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([blob])); const a = document.createElement('a')
    a.href = url; a.download = '资产导入模板.xlsx'; a.click(); URL.revokeObjectURL(url)
  } catch (error) { ElMessage.error('模板下载失败') }
}

const onExcelFileChange = async (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  try {
    const res = await api.post('/assets/import', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    ElMessage.success(`导入完成：成功 ${res.imported || 0} 条`)
    if (res.errors?.length) {
      console.warn('导入错误', res.errors)
      ElMessage.warning(`部分导入失败：${res.errors.length} 条`)
    }
    fetchAssets()
  } catch (error) {
    console.error(error)
  } finally {
    e.target.value = ''
  }
}

const showReminders = async (type) => {
  try {
    const res = await api.get('/assets/reminders', { params: { type } })
    const list = Array.isArray(res?.[type]) ? res[type] : []
    if (!list.length) {
      ElMessage.info('暂无提醒')
      return
    }
    reminders[type] = list
    reminderType.value = type
    reminderVisible.value = true
  } catch (error) {
    console.error('获取提醒失败', error)
    const serverMessage = error.response?.data?.error
    if (serverMessage) {
      ElMessage.error(serverMessage)
      return
    }
    if (error.response?.status === 404) {
      ElMessage.error('提醒接口不存在，请联系管理员检查后端路由')
      return
    }
    ElMessage.error('获取提醒失败，请稍后重试')
  }
}

const resetFilter = () => {
  filterForm.search = ''
  filterForm.category = ''
  pagination.page = 1
  syncListQuery()
  fetchAssets()
}

const resetFormFields = () => {
  imageFiles.value = []
  Object.assign(formData, {
    name: '', category: '', asset_number: '', management_type: '自主管理', quantity: 1,
    model: '', purchase_date: '', market_value: '', responsible_person: '', location: '', status: '使用中', notes: '',
    longitude: '', latitude: '', coord_type: 'gcj02',
    certificate_status: '', property_unit: '', building_area: '',
    lease_start_date: '', lease_end_date: '', lease_reminder_days: 30, lease_status: '租赁中',
    tenant_name: '', tenant_contact: '', tenant_nature: '个人', tenant_purpose: '',
    rent_amount: '', rent_payment_method: '', bidding_situation: '',
    trusteeship_contract_type: '', trusteeship_contract_amount: '',
    trusteeship_counterparty: '', trusteeship_contract_number: '',
    trusteeship_start_date: '', trusteeship_end_date: '', trusteeship_sign_date: '', trusteeship_is_archived: ''
  })
}

const showAddDialog = () => {
  isEdit.value = false; dialogTitle.value = '添加资产'; currentAssetId.value = null
  resetFormFields()
  dialogVisible.value = true
}

const editAsset = async (row) => {
  isEdit.value = true; dialogTitle.value = '编辑资产'; currentAssetId.value = row.id
  try {
    const res = await api.get(`/assets/${row.id}`)
    Object.assign(formData, {
      name: res.name || '',
      category: res.category || '',
      asset_number: res.asset_number || '',
      management_type: res.management_type || '自主管理',
      quantity: res.quantity ?? 1,
      model: res.model || '',
      purchase_date: res.purchase_date || '',
      market_value: res.market_value ?? '',
      responsible_person: res.responsible_person || '',
      location: res.location || '',
      longitude: res.longitude ?? '',
      latitude: res.latitude ?? '',
      coord_type: res.coord_type || 'gcj02',
      status: res.status || '使用中',
      notes: res.notes || '',
      certificate_status: res.certificate_status || '',
      property_unit: res.property_unit || '',
      building_area: res.building_area || '',
      lease_start_date: res.lease_start_date || '',
      lease_end_date: res.lease_end_date || '',
      lease_reminder_days: res.lease_reminder_days ?? 30,
      lease_status: res.lease_status || '租赁中',
      tenant_name: res.tenant_name || '',
      tenant_contact: res.tenant_contact || '',
      tenant_nature: res.tenant_nature || '个人',
      tenant_purpose: res.tenant_purpose || '',
      rent_amount: res.rent_amount ?? '',
      rent_payment_method: res.rent_payment_method || '',
      bidding_situation: res.bidding_situation || '',
      trusteeship_contract_type: res.trusteeship_contract_type || '',
      trusteeship_contract_amount: res.trusteeship_contract_amount ?? '',
      trusteeship_counterparty: res.trusteeship_counterparty || '',
      trusteeship_contract_number: res.trusteeship_contract_number || '',
      trusteeship_start_date: res.trusteeship_start_date || '',
      trusteeship_end_date: res.trusteeship_end_date || '',
      trusteeship_sign_date: res.trusteeship_sign_date || '',
      trusteeship_is_archived: res.trusteeship_is_archived || ''
    })
    imageFiles.value = [res.image_path1, res.image_path2, res.image_path3].filter(Boolean).map((path, index) => ({
      name: `资产图片${index + 1}`,
      url: path.startsWith('http') ? path : `/api/images/${path}`,
      storedPath: path,
      status: 'success'
    }))
    dialogVisible.value = true
  } catch (error) { ElMessage.error('获取资产详情失败') }
}

const viewDetail = (row) => router.push({
  name: 'AssetDetail',
  params: { id: row.id },
  query: listQuery()
})

const deleteAsset = async (row) => {
  try { await ElMessageBox.confirm(`确定要删除资产 "${row.name}" 吗？`, '提示', { type: 'warning' }); await api.delete(`/assets/${row.id}`); ElMessage.success('删除成功'); fetchAssets() } catch (error) { if (error !== 'cancel') ElMessage.error('删除失败') }
}

const onCategoryChange = () => {
  if (formData.category !== '房屋资产') {
    formData.certificate_status = ''
    formData.property_unit = ''
    formData.building_area = ''
  }
}

const onManagementTypeChange = () => {
  if (formData.management_type !== '租赁管理') {
    formData.lease_start_date = ''
    formData.lease_end_date = ''
    formData.lease_reminder_days = 30
    formData.lease_status = '租赁中'
    formData.tenant_name = ''
    formData.tenant_contact = ''
    formData.tenant_nature = '个人'
    formData.tenant_purpose = ''
    formData.rent_amount = ''
    formData.rent_payment_method = ''
    formData.bidding_situation = ''
  }
  if (formData.management_type !== '托管管理') {
    formData.trusteeship_contract_type = ''
    formData.trusteeship_contract_amount = ''
    formData.trusteeship_counterparty = ''
    formData.trusteeship_contract_number = ''
    formData.trusteeship_start_date = ''
    formData.trusteeship_end_date = ''
    formData.trusteeship_sign_date = ''
    formData.trusteeship_is_archived = ''
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const payload = { ...formData }
        payload.longitude = formData.longitude === '' ? null : Number(formData.longitude)
        payload.latitude = formData.latitude === '' ? null : Number(formData.latitude)
        if (formData.category !== '房屋资产') {
          payload.certificate_status = ''
          payload.property_unit = ''
          payload.building_area = ''
        }
        if (formData.management_type !== '租赁管理') {
          payload.lease_start_date = ''
          payload.lease_end_date = ''
          payload.lease_reminder_days = null
          payload.lease_status = ''
          payload.tenant_name = ''
          payload.tenant_contact = ''
          payload.tenant_nature = ''
          payload.tenant_purpose = ''
          payload.rent_amount = ''
          payload.rent_payment_method = ''
          payload.bidding_situation = ''
        }
        if (formData.management_type !== '托管管理') {
          payload.trusteeship_contract_type = ''
          payload.trusteeship_contract_amount = ''
          payload.trusteeship_counterparty = ''
          payload.trusteeship_contract_number = ''
          payload.trusteeship_start_date = ''
          payload.trusteeship_end_date = ''
          payload.trusteeship_sign_date = ''
          payload.trusteeship_is_archived = ''
        }
        let assetId = currentAssetId.value
        if (isEdit.value) { await api.put(`/assets/${assetId}`, payload) }
        else { const created = await api.post('/assets', payload); assetId = created.id }
        const newImages = imageFiles.value.filter(item => item.raw).map(item => item.raw)
        if (isEdit.value || newImages.length) {
          const imageData = new FormData()
          imageFiles.value.filter(item => item.storedPath).forEach(item => imageData.append('keep_images', item.storedPath))
          newImages.forEach(file => imageData.append('images', file))
          await api.post(`/assets/${assetId}/images`, imageData, { headers: { 'Content-Type': 'multipart/form-data' } })
        }
        ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
        dialogVisible.value = false; fetchAssets()
      } catch (error) { ElMessage.error(error.response?.data?.error || '操作失败') } finally { submitting.value = false }
    }
  })
}

onMounted(async () => {
  filterForm.search = queryText(route.query.search)
  filterForm.category = queryText(route.query.category)
  pagination.page = positiveInt(route.query.page, 1)
  const requestedPageSize = positiveInt(route.query.per_page, 20)
  pagination.per_page = [10, 20, 50, 100].includes(requestedPageSize) ? requestedPageSize : 20

  await Promise.all([fetchAssets(), fetchCategories()])

  const editId = positiveInt(route.query.edit, 0)
  if (editId) {
    await editAsset({ id: editId })
    await router.replace({ name: 'Assets', query: listQuery() })
  }
})
</script>

<style scoped>
.assets-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title { margin: 0; color: #303133; font-size: 24px; }
.filter-card, .table-card { margin-bottom: 20px; }
.pagination-container { display: flex; justify-content: flex-end; margin-top: 20px; }
.form-section { padding: 16px; background: #fafafa; border-radius: 8px; margin-bottom: 16px; }
.section-title { font-weight: 600; font-size: 15px; color: #303133; margin-bottom: 12px; }
.unit-input { display: flex; align-items: center; gap: 8px; }
.input-unit { color: #909399; font-size: 13px; }
.image-tip { margin-top: 8px; color: #909399; font-size: 12px; }
.image-preview-container { height: 70vh; display: flex; align-items: center; justify-content: center; }
.image-preview-container :deep(.el-image) { width: 100%; height: 100%; }
</style>
