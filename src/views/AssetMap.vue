<template>
  <div class="map-page">
    <el-card class="toolbar-card">
      <div class="toolbar">
        <div class="toolbar-left">
          <el-select v-model="mapType" placeholder="地图类型" style="width: 180px" @change="onMapTypeChange">
            <el-option label="OpenStreetMap（免费）" value="osm" />
            <el-option label="高德地图" value="amap" />
          </el-select>
          <el-input v-model="searchText" placeholder="搜索资产名称" style="width: 200px" clearable @input="onSearch" />
        </div>
        <div class="toolbar-right">
          <el-button @click="refreshData">刷新</el-button>
        </div>
      </div>
    </el-card>

    <div class="map-container">
      <div class="asset-list-panel">
        <div class="list-header">
          <h3>资产列表</h3>
          <span class="asset-count">{{ filteredAssets.length }} / {{ assets.length }}</span>
        </div>
        <div class="asset-list">
          <div v-if="filteredAssets.length === 0" class="no-data">暂无资产</div>
          <div
            v-for="asset in filteredAssets"
            :key="asset.id"
            :class="['asset-item', { 'has-coords': hasCoords(asset), 'no-coords': !hasCoords(asset) }]"
            @click="onAssetClick(asset)"
          >
            <div class="asset-name">{{ asset.name }}</div>
            <div class="asset-location">{{ asset.location }}</div>
            <div v-if="!hasCoords(asset)" class="no-coords-tag">未定位</div>
          </div>
        </div>
      </div>
      <div class="map-view">
        <div id="asset-map" ref="mapContainer"></div>
      </div>
    </div>

    <!-- 资产详情弹窗 -->
    <el-dialog v-model="detailVisible" :title="currentAsset?.name" width="700px" destroy-on-close>
      <template v-if="currentAsset">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="资产编号">{{ currentAsset.asset_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ currentAsset.category }}</el-descriptions-item>
          <el-descriptions-item label="管理类型">{{ currentAsset.management_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentAsset.status)">{{ currentAsset.status || '未设置' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="位置" :span="2">{{ currentAsset.location }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ currentAsset.responsible_person || '-' }}</el-descriptions-item>
          <el-descriptions-item label="建筑面积">{{ currentAsset.building_area ? currentAsset.building_area + ' m²' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="市场价值">
            <span v-if="currentAsset.market_value">¥{{ Number(currentAsset.market_value).toLocaleString() }}</span>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="年租金">
            <span v-if="currentAsset.rent_amount">¥{{ Number(currentAsset.rent_amount).toLocaleString() }}</span>
            <span v-else>-</span>
          </el-descriptions-item>
          <el-descriptions-item label="承租方" :span="2">{{ currentAsset.tenant_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="坐标" :span="2">
            <span v-if="currentAsset.longitude && currentAsset.latitude">
              {{ currentAsset.longitude }}, {{ currentAsset.latitude }}
            </span>
            <span v-else>-</span>
          </el-descriptions-item>
        </el-descriptions>
        <!-- 图片 -->
        <div v-if="currentAsset.image_path1 || currentAsset.image_path2 || currentAsset.image_path3" class="asset-images">
          <h4>资产图片</h4>
          <div class="image-list">
            <el-image
              v-for="(imageUrl, index) in mapImageList"
              :key="imageUrl"
              :src="imageUrl"
              :preview-src-list="mapImageList"
              :initial-index="index"
              fit="cover"
              class="map-image-item"
              @error="onImageError"
            >
              <template #error>
                <div class="image-fallback"><el-icon><Picture /></el-icon></div>
              </template>
            </el-image>
          </div>
        </div>
      </template>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="viewFullDetail">查看完整详情</el-button>
      </template>
    </el-dialog>

    <!-- 地图点选提示浮层已移除，功能合并到地图标记 popup -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'
import L from 'leaflet'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import 'leaflet/dist/leaflet.css'

const router = useRouter()
const mapContainer = ref(null)
const assets = ref([])
const searchText = ref('')
const mapType = ref('osm')
const detailVisible = ref(false)
const currentAsset = ref(null)
let map = null
let markers = []
let activeMarker = null
let activeCircle = null

// 使用内联CSS标记，避免Leaflet默认marker图片在生产构建后路径失效。
const assetMarkerIcon = L.divIcon({
  className: 'asset-marker-icon',
  html: '<div class="asset-marker-pin"><span>⌂</span></div>',
  iconSize: [30, 38],
  iconAnchor: [15, 36],
  popupAnchor: [0, -34]
})

const filteredAssets = computed(() => {
  if (!searchText.value) return assets.value
  const keyword = searchText.value.toLowerCase()
  return assets.value.filter(a => a.name.toLowerCase().includes(keyword))
})

const hasCoords = (asset) => asset.longitude && asset.latitude

const getStatusType = (status) => ({
  '使用中': 'success', '闲置': 'warning', '已报废': 'danger', '正常': 'success'
})[status] || 'info'

const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `/api/images/${path}`
}

const mapImageList = computed(() => {
  if (!currentAsset.value) return []
  return [currentAsset.value.image_path1, currentAsset.value.image_path2, currentAsset.value.image_path3]
    .filter(Boolean)
    .map(getImageUrl)
})

const fetchAssets = async () => {
  try {
    const res = await api.get('/assets', { params: { per_page: 1000 } })
    assets.value = res.assets || []
    updateMarkers()
  } catch (error) {
    console.error('获取资产列表失败:', error)
  }
}

const initMap = () => {
  if (!mapContainer.value) return
  if (map) {
    map.remove()
    map = null
  }

  map = L.map('asset-map').setView([30.243, 120.293], 11)

  if (mapType.value === 'osm') {
    L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
      subdomains: '1234',
      attribution: '&copy; 高德地图'
    }).addTo(map)
  }

  updateMarkers()
}

const updateMarkers = () => {
  if (!map) return

  clearMarkers()

  const coords = []
  filteredAssets.value.forEach(asset => {
    if (hasCoords(asset)) {
      const lat = parseFloat(asset.latitude || asset.lat)
      const lng = parseFloat(asset.longitude || asset.lng)
      if (!isNaN(lat) && !isNaN(lng)) {
        const marker = L.marker([lat, lng], { icon: assetMarkerIcon, riseOnHover: true }).addTo(map)
        const isRented = asset.management_type === '租赁管理'
        const statusColor = isRented ? '#409eff' : '#67c23a'
        const statusLabel = isRented ? '租赁中' : (asset.status || '正常')
        marker.bindPopup(`
          <div class="custom-popup">
            <div class="popup-header">
              <div class="popup-title">${asset.name}</div>
              <div class="popup-badge" style="background:${statusColor}">${statusLabel}</div>
            </div>
            <div class="popup-body">
              <div class="popup-row"><span class="popup-label">地址</span><span class="popup-value">${asset.location || '-'}</span></div>
              <div class="popup-row"><span class="popup-label">分类</span><span class="popup-value">${asset.category}</span></div>
              <div class="popup-row"><span class="popup-label">部门</span><span class="popup-value">${asset.department_name || '-'}</span></div>
              <div class="popup-row"><span class="popup-label">负责人</span><span class="popup-value">${asset.responsible_person || '-'}</span></div>
            </div>
            <div class="popup-footer">
              <button class="popup-btn primary" onclick="window.__openDetail('${asset.id}')">查看详情</button>
              <button class="popup-btn success" onclick="window.__openStreet('${asset.id}')">查看实景</button>
            </div>
          </div>
        `, { maxWidth: 320, minWidth: 280 })
        marker.on('click', (e) => {
          highlightMarker(marker, lat, lng)
        })
        markers.push({ marker, asset, lat, lng })
        coords.push([lat, lng])
      }
    }
  })

  if (coords.length > 0) {
    const bounds = L.latLngBounds(coords)
    map.fitBounds(bounds, { padding: [50, 50] })
  }
}

const clearMarkers = () => {
  if (map) map.closePopup()
  markers.forEach(({ marker }) => {
    if (map.hasLayer(marker)) map.removeLayer(marker)
  })
  markers = []
  activeMarker = null
  if (activeCircle && map.hasLayer(activeCircle)) {
    map.removeLayer(activeCircle)
    activeCircle = null
  }
}

const highlightMarker = (clickedMarker, lat, lng) => {
  if (activeMarker === clickedMarker) return

  if (activeCircle && map.hasLayer(activeCircle)) {
    map.removeLayer(activeCircle)
  }
  if (activeMarker) {
    activeMarker.setOpacity(1)
  }

  activeMarker = clickedMarker
  clickedMarker.setOpacity(0.3)

  activeCircle = L.circle([lat, lng], {
    color: '#409eff',
    fillColor: '#409eff',
    fillOpacity: 0.25,
    weight: 2,
    radius: 60,
    dashArray: '6, 6'
  }).addTo(map)
}

const showHoverCard = (asset) => { }

const hideHoverCard = () => { }

const onMapTypeChange = () => {
  initMap()
}

const onSearch = () => {
  updateMarkers()
}

const onAssetClick = (asset) => {
  const lat = parseFloat(asset.latitude || asset.lat)
  const lng = parseFloat(asset.longitude || asset.lng)
  if (!isNaN(lat) && !isNaN(lng) && map) {
    map.flyTo([lat, lng], 17, { duration: 1 })
    const found = markers.find(m => m.asset.id === asset.id)
    if (found) {
      highlightMarker(found.marker, lat, lng)
      setTimeout(() => found.marker.openPopup(), 1200)
    }
  }
}

const refreshData = () => {
  fetchAssets()
}

const openDetailFromHover = () => {
  const asset = getHoverAsset()
  if (!asset) return
  currentAsset.value = asset
  detailVisible.value = true
}

const openStreetFromHover = () => {
  const asset = getHoverAsset()
  if (!asset) return
  openStreetView(asset)
}

const getHoverAsset = () => {
  return activeMarker ? markers.find(m => m.marker === activeMarker)?.asset : null
}

const openStreetView = (asset) => {
  const address = (asset.location || '').trim()
  if (!address) {
    ElMessage.warning('该资产未填写地址')
    return
  }
  // 与资产管理列表一致：打开百度地图并自动把资产地址带入搜索框。
  window.open(`https://map.baidu.com/search?querytype=s&wd=${encodeURIComponent(address)}`, '_blank')
}

window.__openDetail = (id) => {
  const asset = assets.value.find(a => String(a.id) === String(id))
  if (asset) {
    currentAsset.value = asset
    detailVisible.value = true
  }
}

window.__openStreet = (id) => {
  const asset = assets.value.find(a => String(a.id) === String(id))
  if (asset) openStreetView(asset)
}

const viewFullDetail = () => {
  if (!currentAsset.value) return
  detailVisible.value = false
  router.push(`/assets/${currentAsset.value.id}`)
}

const onImageError = (e) => {
  e.target.style.display = 'none'
}

onMounted(() => {
  fetchAssets()
  setTimeout(initMap, 100)
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})
</script>

<style scoped>
.map-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 100px);
  gap: 16px;
}

.toolbar-card { flex-shrink: 0; }

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.map-container {
  flex: 1;
  display: flex;
  gap: 16px;
  min-height: 0;
}

.asset-list-panel {
  width: 280px;
  flex-shrink: 0;
  background: white;
  border-radius: 12px;
  border: 1px solid #f0f2f5;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.list-header {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.list-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.asset-count {
  font-size: 12px;
  color: #909399;
}

.asset-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 20px;
}

.asset-item {
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.asset-item:hover {
  background: #f5f7fa;
}

.asset-item.has-coords {
  border-left: 3px solid #67c23a;
}

.asset-item.no-coords {
  border-left: 3px solid #e6a23c;
  opacity: 0.7;
}

.asset-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.asset-location {
  font-size: 11px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-coords-tag {
  font-size: 10px;
  color: #e6a23c;
  margin-top: 2px;
}

.map-view {
  flex: 1;
  min-width: 0;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #f0f2f5;
}

#asset-map {
  width: 100%;
  height: 100%;
}

:deep(.asset-marker-icon) {
  background: transparent;
  border: 0;
}

:deep(.asset-marker-pin) {
  width: 28px;
  height: 28px;
  border-radius: 50% 50% 50% 0;
  background: #409eff;
  border: 2px solid #fff;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.35);
  transform: rotate(-45deg);
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.asset-marker-pin span) {
  color: #fff;
  font-size: 17px;
  font-weight: 700;
  line-height: 1;
  transform: rotate(45deg);
}

.asset-images {
  margin-top: 16px;
}

.asset-images h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.image-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.image-list img {
  width: 150px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #eee;
}

.map-image-item {
  width: 180px;
  height: 140px;
  border-radius: 8px;
  border: 1px solid #eee;
}

.image-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  background: #f5f7fa;
}

.map-hover-card {
  position: absolute;
  z-index: 1000;
  width: 260px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.12);
  padding: 12px;
  pointer-events: auto;
}

.hover-title {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

.hover-sub {
  font-size: 12px;
  color: #909399;
  margin-bottom: 10px;
}

.hover-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 地图标记精美信息框 */
:deep(.leaflet-popup-content-wrapper) {
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.14);
  padding: 0;
  overflow: hidden;
}

:deep(.leaflet-popup-content) {
  margin: 0;
  width: 300px !important;
}

:deep(.custom-popup) {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

:deep(.popup-header) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px 10px;
  border-bottom: 1px solid #f0f2f5;
  background: #fafafa;
}

:deep(.popup-title) {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 8px;
}

:deep(.popup-badge) {
  font-size: 11px;
  color: #fff;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

:deep(.popup-body) {
  padding: 10px 14px;
}

:deep(.popup-row) {
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 12px;
  line-height: 1.4;
}

:deep(.popup-row:last-child) {
  margin-bottom: 0;
}

:deep(.popup-label) {
  color: #909399;
  flex-shrink: 0;
  min-width: 42px;
}

:deep(.popup-value) {
  color: #303133;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.popup-footer) {
  display: flex;
  gap: 8px;
  padding: 10px 14px;
  border-top: 1px solid #f0f2f5;
  background: #fafafa;
}

:deep(.popup-btn) {
  flex: 1;
  padding: 6px 0;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

:deep(.popup-btn:hover) {
  opacity: 0.85;
}

:deep(.popup-btn.primary) {
  background: #409eff;
  color: #fff;
}

:deep(.popup-btn.success) {
  background: #67c23a;
  color: #fff;
}
</style>
