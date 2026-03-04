<template>
  <div class="anomalies-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>异常记录查询</span>
          <el-button type="primary" @click="searchAnomalies">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
        </div>
      </template>
      
      <el-form :model="searchForm" :inline="true">
        <el-form-item label="用户ID">
          <el-input v-model="searchForm.userId" placeholder="请输入用户ID" clearable />
        </el-form-item>
        
        <el-form-item label="异常类型">
          <el-select v-model="searchForm.type" placeholder="请选择" clearable>
            <el-option label="全部" value="" />
            <el-option label="多带物品" value="extra" />
            <el-option label="物品缺失" value="missing" />
            <el-option label="数量异常" value="quantity" />
            <el-option label="重量异常" value="weight" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top: 20px;">
      <el-table :data="anomalies" border style="width: 100%" v-loading="loading">
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-content">
              <h4>异常详情</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="入场时间">
                  {{ row.entryTime }}
                </el-descriptions-item>
                <el-descriptions-item label="离场时间">
                  {{ row.exitTime }}
                </el-descriptions-item>
                <el-descriptions-item label="入场通道">
                  {{ row.entryChannel }}
                </el-descriptions-item>
                <el-descriptions-item label="离场通道">
                  {{ row.exitChannel }}
                </el-descriptions-item>
              </el-descriptions>
              
              <h4 style="margin-top: 20px;">物品对比</h4>
              <el-row :gutter="20">
                <el-col :span="12">
                  <h5>入场物品</h5>
                  <el-table :data="row.entryItems" border size="small">
                    <el-table-column prop="name" label="物品" />
                    <el-table-column prop="quantity" label="数量" width="80" />
                    <el-table-column prop="weight" label="重量(kg)" width="100">
                      <template #default="{ row }">
                        {{ row.weight || 0 }}
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="12">
                  <h5>离场物品</h5>
                  <el-table :data="row.exitItems" border size="small">
                    <el-table-column prop="name" label="物品" />
                    <el-table-column prop="quantity" label="数量" width="80" />
                    <el-table-column prop="weight" label="重量(kg)" width="100">
                      <template #default="{ row }">
                        {{ row.weight || 0 }}
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
              </el-row>
              
              <div style="margin-top: 20px;">
                <el-tag type="danger">{{ row.anomalyDescription }}</el-tag>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="id" label="记录ID" width="100" />
        <el-table-column prop="userId" label="用户ID" width="150" />
        <el-table-column prop="type" label="异常类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)">{{ row.typeText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="发生时间" width="180" />
        <el-table-column prop="status" label="处理状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : 'success'">
              {{ row.status === 'pending' ? '待处理' : '已处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewDetail(row)">
              查看
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              size="small"
              @click="handleAnomaly(row)"
            >
              处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: center;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const searchForm = ref({
  userId: '',
  type: '',
  dateRange: []
})

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const anomalies = ref([])
const loading = ref(false)

/**
 * 加载异常记录
 */
const loadAnomalies = async () => {
  loading.value = true
  try {
    const params = {
      userId: searchForm.value.userId || undefined,
      type: searchForm.value.type || undefined,
      page: currentPage.value,
      pageSize: pageSize.value
    }
    
    const data = await api.getAnomalies(params)
    anomalies.value = data.data || []
    total.value = data.total || 0
  } catch (error) {
    console.error('加载异常记录失败:', error)
    ElMessage.error('加载异常记录失败')
  } finally {
    loading.value = false
  }
}

/**
 * 查询异常记录
 */
const searchAnomalies = async () => {
  currentPage.value = 1
  await loadAnomalies()
  ElMessage.success('查询完成')
}

/**
 * 获取异常类型颜色
 */
const getTypeColor = (type) => {
  const colors = {
    extra: 'danger',
    missing: 'warning',
    quantity: 'info',
    weight: 'primary'
  }
  return colors[type] || 'info'
}

/**
 * 查看详情
 */
const viewDetail = (row) => {
  ElMessage.info(`查看记录: ${row.id}`)
}

/**
 * 处理异常
 */
const handleAnomaly = async (row) => {
  try {
    await ElMessageBox.prompt('请输入处理备注', '处理异常', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '请输入处理备注'
    })
    
    // 更新状态
    row.status = 'resolved'
    ElMessage.success('处理完成')
    
    // 刷新列表
    await loadAnomalies()
  } catch {
    // 取消操作
  }
}

onMounted(async () => {
  await loadAnomalies()
})
</script>

<style scoped>
.anomalies-container {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.expand-content {
  padding: 20px;
  background: #f5f7fa;
}

.expand-content h4 {
  margin: 10px 0;
  color: #303133;
}

.expand-content h5 {
  margin: 10px 0;
  color: #606266;
}
</style>
