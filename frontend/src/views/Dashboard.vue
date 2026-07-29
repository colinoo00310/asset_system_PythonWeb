<template>
  <div class="dashboard">

    <!-- 顶部公司 banner -->
    <div class="company-banner">
      <div class="banner-bg"></div>
      <div class="banner-content">
        <div class="banner-left">
          <div class="banner-logo-fallback">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="banner-text">
            <h1>资产管理平台</h1>
            <p>Asset Management System</p>
          </div>
        </div>
        <div class="banner-right">
          <span class="banner-date">{{ currentDate }}</span>
        </div>
      </div>
    </div>

    <!-- 统计卡片三列 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="8">
        <div class="stat-card">
          <div class="stat-icon-wrap blue">
            <el-icon class="stat-icon"><Box /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-label">资产总数</p>
            <p class="stat-value">{{ stats.total || 0 }} <span class="stat-unit">个</span></p>
          </div>
          <div class="stat-trend up">
            <el-icon><Top /></el-icon>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="8">
        <div class="stat-card">
          <div class="stat-icon-wrap green">
            <el-icon class="stat-icon"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-label">部门数量</p>
            <p class="stat-value">{{ stats.department_count || 0 }} <span class="stat-unit">个</span></p>
          </div>
          <div class="stat-trend up">
            <el-icon><Top /></el-icon>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="8">
        <div class="stat-card">
          <div class="stat-icon-wrap amber">
            <el-icon class="stat-icon"><User /></el-icon>
          </div>
          <div class="stat-info">
            <p class="stat-label">用户数量</p>
            <p class="stat-value">{{ stats.user_count || 0 }} <span class="stat-unit">人</span></p>
          </div>
          <div class="stat-trend up">
            <el-icon><Top /></el-icon>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 公司简介 & 联系我们 -->
    <el-row :gutter="20" class="info-row">
      <el-col :xs="24" :lg="12">
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header-inner">
              <el-icon class="header-icon blue"><Reading /></el-icon>
              <span>项目简介</span>
            </div>
          </template>
          <div class="info-content">
            <p>这是一个面向学习、演示和二次开发的通用资产管理模板。项目包含资产台账、部门与人员、角色权限、租赁提醒、地图展示以及 Excel 导入导出等功能。</p>
            <br>模板特性：
            <br>• Flask REST API 与 Vue 3 管理界面
            <br>• SQLite 开箱即用，可按需替换数据库
            <br>• 首次启动自动创建完全虚构的演示数据
            <br><br>请在实际使用前修改品牌、账号和生产环境配置。
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header-inner">
              <el-icon class="header-icon green"><Phone /></el-icon>
              <span>演示信息</span>
            </div>
          </template>
          <div class="info-content contact-grid">
            <div class="contact-item">
              <el-icon class="contact-icon"><Location /></el-icon>
              <div>
                <span class="contact-label">示例地址</span>
                <span class="contact-value">示例市创新路 100 号</span>
              </div>
            </div>
            <div class="contact-item">
              <el-icon class="contact-icon"><Phone /></el-icon>
              <div>
                <span class="contact-label">联系电话</span>
                <span class="contact-value">010-00000000</span>
              </div>
            </div>
            <div class="contact-item">
              <el-icon class="contact-icon"><Message /></el-icon>
              <div>
                <span class="contact-label">电子邮箱</span>
                <span class="contact-value">demo@example.com</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 管理类型统计 -->
    <el-card class="section-card" shadow="never" v-if="stats.by_management_type && Object.keys(stats.by_management_type).length > 0">
      <template #header>
        <div class="card-header-inner">
          <el-icon class="header-icon purple"><Collection /></el-icon>
          <span>资产管理类型统计</span>
        </div>
      </template>
      <div class="management-list">
        <div v-for="item in managementSummary" :key="item.name" class="management-item">
          <div class="management-dot"></div>
          <span class="management-name">{{ item.name }}</span>
          <el-progress :percentage="getPercentage(item.count)" :stroke-width="8" :show-text="false" class="management-progress" />
          <span class="management-count">{{ item.count }} 处</span>
        </div>
      </div>
    </el-card>

    <!-- 资产分类和状态统计 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <el-card class="section-card" shadow="never">
          <template #header>
            <div class="card-header-inner">
              <el-icon class="header-icon blue"><PieChart /></el-icon>
              <span>资产分类统计</span>
            </div>
          </template>
          <div class="pie-wrapper" v-if="stats.by_category && Object.keys(stats.by_category).length > 0">
            <div ref="pieChartRef" class="pie-chart"></div>
          </div>
          <div v-else class="no-data">
            <el-empty description="暂无数据" :image-size="80" />
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card class="section-card" shadow="never">
          <template #header>
            <div class="card-header-inner">
              <el-icon class="header-icon amber"><DataLine /></el-icon>
              <span>资产状态统计</span>
            </div>
          </template>
          <div class="chart-container">
            <div v-if="!stats.by_status || Object.keys(stats.by_status).length === 0" class="no-data">
              <el-empty description="暂无数据" :image-size="80" />
            </div>
            <div v-else class="status-list">
              <div v-for="(count, status) in stats.by_status" :key="status" class="status-item">
                <el-tag :type="getStatusType(status)" size="default" effect="light">{{ status }}</el-tag>
                <span class="status-count">{{ count }}</span>
                <el-progress :percentage="getPercentage(count)" :stroke-width="8" :show-text="false" class="status-progress" />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import api from '@/utils/api'
import {
  Box, OfficeBuilding, User, Top, Reading, Phone, Location, Message,
  Collection, PieChart, DataLine, TrendCharts
} from '@element-plus/icons-vue'
import { ElEmpty } from 'element-plus'
import * as echarts from 'echarts'

const stats = ref({})
const pieChartRef = ref(null)

const currentDate = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })

const managementSummary = computed(() => {
  const counts = stats.value.by_management_type || {}
  return [
    { name: '托管资产', count: Number(counts['托管管理'] || 0) },
    {
      name: '自有资产',
      count: Number(counts['自主管理'] || 0) + Number(counts['租赁管理'] || 0)
    }
  ]
})

const getPercentage = (count) => stats.value.total ? Math.round((count / stats.value.total) * 100) : 0

const getStatusType = (status) => ({ '使用中': 'success', '闲置': 'warning', '已报废': 'danger', '未设置': 'info' })[status] || 'info'

const categoryColors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc']
const getCategoryColor = (category) => {
  const keys = Object.keys(stats.value.by_category || {})
  const idx = keys.indexOf(category)
  return categoryColors[idx % categoryColors.length]
}

const fetchStats = async () => {
  try {
    const data = await api.get('/assets/stats')
    stats.value = data
    await nextTick()
    renderPieChart()
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const renderPieChart = () => {
  if (!pieChartRef.value || !stats.value.by_category) return
  const chart = echarts.init(pieChartRef.value)
  const chartData = Object.entries(stats.value.by_category).map(([name, value]) => ({ name, value }))
  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'middle', textStyle: { fontSize: 13 } },
    color: categoryColors,
    series: [{
      name: '资产分类',
      type: 'pie',
      radius: ['42%', '72%'],
      center: ['60%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n{c}', fontSize: 12 },
      emphasis: { label: { show: true, fontSize: 15, fontWeight: 'bold' } },
      data: chartData
    }]
  }
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

onMounted(() => {
  fetchStats()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

/* 顶部 Banner */
.company-banner {
  position: relative;
  height: 130px;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.banner-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #1a1f36 0%, #2d4a6e 40%, #1a3a5c 100%);
}

.banner-bg::after {
  content: '';
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.banner-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 32px;
}

.banner-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.banner-logo {
  width: 70px;
  height: 70px;
  border-radius: 12px;
  object-fit: cover;
  border: 2px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.1);
}

.banner-logo-fallback {
  width: 70px;
  height: 70px;
  border-radius: 12px;
  background: rgba(255,255,255,0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: rgba(255,255,255,0.6);
}

.banner-text h1 {
  color: #fff;
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 4px 0;
  letter-spacing: 1px;
}

.banner-text p {
  color: rgba(255,255,255,0.6);
  font-size: 13px;
  margin: 0;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.banner-right {
  text-align: right;
}

.banner-date {
  color: rgba(255,255,255,0.5);
  font-size: 13px;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 22px 24px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #f0f2f5;
  margin-bottom: 16px;
  position: relative;
  transition: all 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  transform: translateY(-1px);
}

.stat-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-wrap.blue { background: #eef2ff; }
.stat-icon-wrap.green { background: #e8f8f0; }
.stat-icon-wrap.amber { background: #fff8eb; }

.stat-icon {
  font-size: 26px;
}

.stat-icon-wrap.blue .stat-icon { color: #4f6fd5; }
.stat-icon-wrap.green .stat-icon { color: #27ae60; }
.stat-icon-wrap.amber .stat-icon { color: #e67e22; }

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: #8c8c8c;
  margin: 0 0 4px 0;
  font-weight: 400;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
  line-height: 1.2;
}

.stat-unit {
  font-size: 14px;
  font-weight: 400;
  color: #8c8c8c;
}

.stat-trend {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.stat-trend.up {
  background: #e8f8f0;
  color: #27ae60;
}

/* 信息卡片 */
.info-row {
  margin-bottom: 20px;
  display: flex;
}

.info-card {
  border-radius: 12px;
  border: 1px solid #f0f2f5;
  margin-bottom: 16px;
  height: 100%;
  min-height: 260px;
  display: flex;
  flex-direction: column;
}

.info-card :deep(.el-card__body) {
  flex: 1;
}

.card-header-inner {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
  color: #1a1a2e;
}

.header-icon {
  font-size: 18px;
}

.header-icon.blue { color: #4f6fd5; }
.header-icon.green { color: #27ae60; }
.header-icon.amber { color: #e67e22; }
.header-icon.purple { color: #8e44ad; }

.info-content {
  color: #5a5a5a;
  font-size: 13.5px;
  line-height: 1.8;
}

.info-content p {
  margin: 0 0 12px 0;
}


.contact-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.contact-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.contact-icon {
  font-size: 18px;
  color: #4f6fd5;
  margin-top: 2px;
  flex-shrink: 0;
}

.contact-item div {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.contact-label {
  font-size: 12px;
  color: #8c8c8c;
}

.contact-value {
  font-size: 13.5px;
  color: #2c2c2c;
  line-height: 1.6;
}

/* 通用卡片 */
.section-card {
  border-radius: 12px;
  border: 1px solid #f0f2f5;
  margin-bottom: 16px;
}

.chart-row {
  margin-bottom: 0;
  display: flex;
}

.chart-row .el-col {
  margin-bottom: 0;
  display: flex;
}

.chart-row .el-col > .section-card {
  flex: 1;
}

.chart-container {
  min-height: 220px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 220px;
}

/* 状态统计 */
.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.status-count {
  font-size: 14px;
  font-weight: 600;
  color: #2c2c2c;
  min-width: 28px;
  text-align: center;
}

.status-progress {
  flex: 1;
}

/* 管理类型 */
.management-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.management-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.management-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4f6fd5;
  flex-shrink: 0;
}

.management-name {
  font-size: 13px;
  color: #5a5a5a;
  min-width: 90px;
}

.management-progress {
  flex: 1;
}

.management-count {
  font-size: 13px;
  font-weight: 600;
  color: #2c2c2c;
  min-width: 50px;
  text-align: right;
}

/* 饼图 */
.pie-wrapper {
  height: 260px;
}

.pie-chart {
  width: 100%;
  height: 100%;
}
</style>
