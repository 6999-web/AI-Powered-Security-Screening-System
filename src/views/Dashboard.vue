<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" :size="40" color="#409eff"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.todayCheckIn }}</div>
              <div class="stat-label">今日入场</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" :size="40" color="#67c23a"><Check /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.todayCheckOut }}</div>
              <div class="stat-label">今日离场</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" :size="40" color="#e6a23c"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.todayAnomalies }}</div>
              <div class="stat-label">今日异常</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" :size="40" color="#f56c6c"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.currentInside }}</div>
              <div class="stat-label">当前在场</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近安检记录</span>
              <el-button type="text" @click="refreshRecords">刷新</el-button>
            </div>
          </template>
          
          <el-table :data="recentRecords" style="width: 100%">
            <el-table-column prop="userId" label="用户ID" width="150" />
            <el-table-column prop="type" label="类型" width="80">
              <template #default="{ row }">
                <el-tag :type="row.type === '入场' ? 'success' : 'info'">
                  {{ row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="itemCount" label="物品数" width="80" />
            <el-table-column prop="time" label="时间" />
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近异常记录</span>
              <el-button type="text" @click="$router.push('/anomalies')">查看全部</el-button>
            </div>
          </template>
          
          <el-table :data="recentAnomalies" style="width: 100%">
            <el-table-column prop="userId" label="用户ID" width="150" />
            <el-table-column prop="typeText" label="异常类型">
              <template #default="{ row }">
                <el-tag type="warning">{{ row.typeText }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="time" label="时间" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>通道使用情况</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="6" v-for="channel in channels" :key="channel.id">
              <div class="channel-card" :class="{ active: channel.active }">
                <div class="channel-header">
                  <span>通道 {{ channel.id }}</span>
                  <el-tag :type="channel.active ? 'success' : 'info'" size="small">
                    {{ channel.active ? '使用中' : '空闲' }}
                  </el-tag>
                </div>
                <div class="channel-stats">
                  <div>今日通过: {{ channel.todayCount }}</div>
                  <div>当前用户: {{ channel.currentUser || '-' }}</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const statistics = ref({
  todayCheckIn: 0,
  todayCheckOut: 0,
  todayAnomalies: 0,
  currentInside: 0
})

const recentRecords = ref([])
const recentAnomalies = ref([])
const channels = ref([])

let refreshTimer = null

/**
 * 加载统计数据
 */
const loadStatistics = async () => {
  try {
    const data = await api.getStatistics()
    statistics.value = data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

/**
 * 加载最近记录
 */
const loadRecentRecords = async () => {
  try {
    const data = await api.getRecentRecords(5)
    recentRecords.value = data
  } catch (error) {
    console.error('加载最近记录失败:', error)
  }
}

/**
 * 加载最近异常
 */
const loadRecentAnomalies = async () => {
  try {
    const data = await api.getRecentAnomalies(4)
    recentAnomalies.value = data
  } catch (error) {
    console.error('加载最近异常失败:', error)
  }
}

/**
 * 加载通道信息
 */
const loadChannels = async () => {
  try {
    const data = await api.getChannels()
    channels.value = data
  } catch (error) {
    console.error('加载通道信息失败:', error)
  }
}

/**
 * 刷新所有数据
 */
const refreshAll = async () => {
  await Promise.all([
    loadStatistics(),
    loadRecentRecords(),
    loadRecentAnomalies(),
    loadChannels()
  ])
}

/**
 * 刷新记录
 */
const refreshRecords = async () => {
  await loadRecentRecords()
  ElMessage.success('数据已刷新')
}

onMounted(async () => {
  // 初始加载
  await refreshAll()
  
  // 定时刷新数据（每10秒）
  refreshTimer = setInterval(async () => {
    await refreshAll()
  }, 10000)
})

onUnmounted(() => {
  // 清除定时器
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 0;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  height: 100%;
}

.stat-icon {
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.channel-card {
  padding: 15px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s;
}

.channel-card.active {
  border-color: #67c23a;
  background: #f0f9ff;
}

.channel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  font-weight: bold;
}

.channel-stats {
  font-size: 14px;
  color: #606266;
}

.channel-stats > div {
  margin: 5px 0;
}
</style>
