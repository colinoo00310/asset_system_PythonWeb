<template>
  <div class="asset-detail" v-loading="loading">
    <div class="detail-header">
      <el-button @click="goBack"><el-icon><ArrowLeft /></el-icon> 返回</el-button>
      <h2>{{ asset.name || '资产详情' }}</h2>
      <div class="header-actions"><el-button type="primary" @click="editAsset"><el-icon><Edit /></el-icon> 编辑</el-button></div>
    </div>

    <el-card v-if="asset.id">
      <template #header>
        <div class="section-title">基本信息</div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="资产名称" :span="2">{{ asset.name }}</el-descriptions-item>
        <el-descriptions-item label="资产编号">{{ asset.asset_number }}</el-descriptions-item>
        <el-descriptions-item label="分类">{{ asset.category }}</el-descriptions-item>
        <el-descriptions-item label="管理类型">{{ asset.management_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="数量">{{ asset.quantity }} 个</el-descriptions-item>
        <el-descriptions-item label="型号">{{ asset.model || '-' }}</el-descriptions-item>
        <el-descriptions-item label="资产价值">
          <span v-if="asset.market_value">¥{{ Number(asset.market_value).toLocaleString() }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="购置日期">{{ asset.purchase_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ asset.responsible_person }}</el-descriptions-item>
        <el-descriptions-item label="资产地址">
          <template v-if="asset.location">
            <el-popover placement="bottom" :width="220" trigger="click">
              <template #reference>
                <el-link type="primary" :underline="true">{{ asset.location }}</el-link>
              </template>
              <div class="location-popover">
                <el-button type="primary" size="small" @click="openMapBaidu">百度地图</el-button>
                <el-button type="success" size="small" @click="openMapAmap">高德地图</el-button>
              </div>
            </el-popover>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(asset.status)">{{ asset.status || '未设置' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="所属部门">{{ asset.department_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ asset.created_by || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ asset.created_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="3">{{ asset.notes || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 房屋信息 -->
    <el-card v-if="asset.category === '房屋资产' || asset.building_area || asset.certificate_status" class="info-card">
      <template #header>
        <div class="section-title">房屋信息</div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="产证情况">{{ asset.certificate_status || '-' }}</el-descriptions-item>
        <el-descriptions-item label="产权单位">{{ asset.property_unit || '-' }}</el-descriptions-item>
        <el-descriptions-item label="建筑面积">{{ asset.building_area ? asset.building_area + ' m²' : '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 租赁信息 -->
    <el-card v-if="asset.management_type === '租赁管理' || asset.tenant_name || asset.lease_start_date" class="info-card">
      <template #header>
        <div class="section-title">租赁信息</div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="租赁开始日期">{{ asset.lease_start_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="租赁结束日期">{{ asset.lease_end_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="提前提醒天数">{{ asset.lease_reminder_days ? asset.lease_reminder_days + ' 天' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="承租方名称">{{ asset.tenant_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="承租方联系方式">{{ asset.tenant_contact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="承租方性质">{{ asset.tenant_nature || '-' }}</el-descriptions-item>
        <el-descriptions-item label="承租方用途">{{ asset.tenant_purpose || '-' }}</el-descriptions-item>
        <el-descriptions-item label="租金金额">
          <span v-if="asset.rent_amount">¥{{ Number(asset.rent_amount).toLocaleString() }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="租金交付方式">{{ asset.rent_payment_method || '-' }}</el-descriptions-item>
        <el-descriptions-item label="公开招拍租情况">{{ asset.bidding_situation || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 托管信息 -->
    <el-card v-if="asset.management_type === '托管管理' || asset.trusteeship_contract_type" class="info-card">
      <template #header>
        <div class="section-title">托管信息</div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="合同类型">{{ asset.trusteeship_contract_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="合同金额">
          <span v-if="asset.trusteeship_contract_amount">{{ asset.trusteeship_contract_amount }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="合同相对方">{{ asset.trusteeship_counterparty || '-' }}</el-descriptions-item>
        <el-descriptions-item label="合同编号">{{ asset.trusteeship_contract_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="合同开始日期">{{ asset.trusteeship_start_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="合同结束日期">{{ asset.trusteeship_end_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="签署日期">{{ asset.trusteeship_sign_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="是否归档">{{ asset.trusteeship_is_archived || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 资产图片 -->
    <el-card v-if="hasImages" class="info-card">
      <template #header>
        <div class="section-title">资产图片</div>
      </template>
      <div class="image-gallery">
        <el-image
          v-for="(img, idx) in imageList"
          :key="idx"
          :src="img"
          :preview-src-list="imageList"
          fit="cover"
          class="image-item"
          @error="onImageError"
        >
          <template #error>
            <div class="image-fallback"><el-icon><Picture /></el-icon></div>
          </template>
        </el-image>
        <div v-if="!hasImages" class="no-image">暂无图片</div>
      </div>
    </el-card>

    <!-- 地理位置 -->
    <el-card v-if="asset.longitude && asset.latitude" class="info-card">
      <template #header>
        <div class="section-title">地理位置</div>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="经度">{{ asset.longitude }}</el-descriptions-item>
        <el-descriptions-item label="纬度">{{ asset.latitude }}</el-descriptions-item>
        <el-descriptions-item label="坐标类型">{{ asset.coord_type || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Edit, Picture } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const asset = ref({})

const getStatusType = (status) => ({
  '使用中': 'success', '闲置': 'warning', '已报废': 'danger', '正常': 'success'
})[status] || 'info'

const fetchAsset = async () => {
  loading.value = true
  try {
    asset.value = await api.get(`/assets/${route.params.id}`)
  } catch (error) {
    ElMessage.error('获取资产详情失败')
  } finally {
    loading.value = false
  }
}

const hasImages = computed(() => !!(asset.value.image_path1 || asset.value.image_path2 || asset.value.image_path3))

const imageList = computed(() => {
  const list = []
  const add = (path) => {
    if (!path) return
    const apiPath = path.startsWith('http') ? path : `/api/images/${path}`
    list.push(apiPath)
  }
  add(asset.value.image_path1)
  add(asset.value.image_path2)
  add(asset.value.image_path3)
  return list
})

const goBack = () => router.push({ name: 'Assets', query: route.query })
const editAsset = () => router.push({
  name: 'Assets',
  query: { ...route.query, edit: String(route.params.id) }
})

const openMapBaidu = () => {
  const addr = (asset.value.location || '').trim()
  if (!addr) return
  window.open(`https://map.baidu.com/search?querytype=s&wd=${encodeURIComponent(addr)}`, '_blank')
}

const openMapAmap = () => {
  const addr = (asset.value.location || '').trim()
  if (!addr) return
  window.open(`https://uri.amap.com/search?keyword=${encodeURIComponent(addr)}&view=map`, '_blank')
}
const onImageError = (e) => {
  e.target.style.display = 'none'
}

onMounted(() => { fetchAsset() })
</script>

<style scoped>
.asset-detail { padding: 0; }
.detail-header { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
.detail-header h2 { flex: 1; margin: 0; color: #303133; }
.header-actions { display: flex; gap: 10px; }
.info-card { margin-top: 16px; }
.section-title { font-weight: 600; font-size: 15px; color: #303133; }
.image-gallery { display: flex; flex-wrap: wrap; gap: 16px; justify-content: center; }
.image-item { flex: 0 0 auto; width: 320px; height: 240px; border-radius: 8px; border: 1px solid #eee; overflow: hidden; }
.image-fallback { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: #909399; background: #f5f7fa; }
.location-popover { display: flex; gap: 8px; justify-content: center; }
</style>
