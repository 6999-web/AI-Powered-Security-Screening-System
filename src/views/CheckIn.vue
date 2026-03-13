<template>
  <div class="checkin-container">
    <el-card class="step-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><UserFilled /></el-icon>
          <span>步骤 1：身份验证</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="100px">
        <el-form-item label="身份证号">
          <el-input v-model="form.idCard" placeholder="请输入身份证号" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="success" @click="verifyIdentity" :loading="verifying">
            验证身份
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-alert
        v-if="userId"
        title="身份验证成功"
        type="success"
        :closable="false"
        show-icon
      >
        <template #default>
          用户ID: <strong>{{ userId }}</strong>
        </template>
      </el-alert>
    </el-card>

    <el-card class="step-card" :class="{ disabled: !userId }">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Box /></el-icon>
          <span>步骤 2：上传 X 光图片并识别</span>
        </div>
      </template>
      
      <!-- 图片上传区域 -->
      <div v-if="!imagePreview" class="upload-area">
        <el-upload
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleImageUpload"
          :show-file-list="false"
          accept="image/*"
        >
          <el-icon class="el-icon--upload"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg></el-icon>
          <div class="el-upload__text">
            拖拽图片到此或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 JPG、PNG 格式，模拟 X 光机扫描的图片
            </div>
          </template>
        </el-upload>
      </div>

      <!-- 图片预览 -->
      <div v-if="imagePreview" class="image-preview">
        <img :src="imagePreview" alt="上传的图片" />
        <div class="preview-controls">
          <el-button type="primary" @click="clearImage">
            <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg></el-icon>
            重新上传
          </el-button>
        </div>
      </div>
      
      <!-- 物品信息表单 -->
      <el-form v-if="imagePreview" :model="form" label-width="100px" style="margin-top: 20px;">
        <el-form-item label="物品重量">
          <el-input-number v-model="form.weight" :min="0" :precision="2" />
          <span style="margin-left: 10px;">kg</span>
        </el-form-item>
        
        <el-form-item label="通道号">
          <el-input-number v-model="form.channelNo" :min="1" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="success" @click="recognizeItems" :loading="recognizing">
            <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg></el-icon>
            {{ recognizing ? '识别中...' : '开始识别' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 识别进度 -->
      <div v-if="recognizing" class="recognition-progress">
        <el-progress :percentage="recognitionProgress" :status="recognitionProgress === 100 ? 'success' : undefined" />
        <p>{{ recognitionStatus }}</p>
      </div>
    </el-card>

    <el-card v-if="recognitionResult" class="result-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg></el-icon>
          <span>识别结果</span>
        </div>
      </template>
      
      <el-table :data="recognitionResult.items" border>
        <el-table-column prop="name" label="物品名称" />
        <el-table-column prop="category" label="类别" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="weight" label="重量(kg)" />
      </el-table>
      
      <div class="result-summary">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="总件数">
            {{ recognitionResult.totalCount }}
          </el-descriptions-item>
          <el-descriptions-item label="总重量">
            {{ recognitionResult.totalWeight }} kg
          </el-descriptions-item>
          <el-descriptions-item label="安检时间">
            {{ recognitionResult.checkTime }}
          </el-descriptions-item>
          <el-descriptions-item label="通道号">
            {{ recognitionResult.channelNo }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <div class="action-buttons">
        <el-button type="success" size="large" @click="submitCheckIn">
          <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg></el-icon>
          确认入场
        </el-button>
        <el-button size="large" @click="reset">
          <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 4v6h6M23 20v-6h-6"></path><path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path></svg></el-icon>
          重新识别
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const verifyMethod = ref('idcard')
const form = ref({
  idCard: '',
  weight: 0,
  channelNo: 1
})

const userId = ref('')
const verifying = ref(false)

// 图片相关
const imagePreview = ref('')
const imageFile = ref(null)
const recognizing = ref(false)
const recognitionProgress = ref(0)
const recognitionStatus = ref('')
const recognitionResult = ref(null)

const handleImageUpload = (file) => {
  imageFile.value = file.raw
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const verifyIdentity = async () => {
  if (!form.value.idCard) {
    ElMessage.warning('请输入身份证号')
    return
  }
  
  verifying.value = true
  try {
    const formData = new FormData()
    formData.append('idCard', form.value.idCard)
    
    const result = await api.verifyIdentity(formData)
    userId.value = result.userId
    ElMessage.success('身份验证成功，请上传 X 光图片')
  } catch (error) {
    ElMessage.error('身份验证失败')
  } finally {
    verifying.value = false
  }
}

const recognizeItems = async () => {
  if (!imageFile.value) {
    ElMessage.warning('请先上传图片')
    return
  }

  recognizing.value = true
  recognitionProgress.value = 0
  recognitionStatus.value = '正在处理图片...'
  
  try {
    recognitionProgress.value = 30
    recognitionStatus.value = '正在上传到服务器...'
    
    const formData = new FormData()
    formData.append('image', imageFile.value)
    formData.append('user_id', userId.value)
    formData.append('weight', form.value.weight)
    formData.append('channel_no', form.value.channelNo)
    
    recognitionProgress.value = 60
    recognitionStatus.value = '正在调用 AI 识别...'
    
    const result = await api.checkIn(formData)
    
    recognitionProgress.value = 90
    recognitionStatus.value = '正在解析结果...'
    
    recognitionResult.value = {
      items: result.items || [],
      totalCount: result.total_count || 0,
      totalWeight: result.total_weight || form.value.weight,
      checkTime: result.timestamp || new Date().toLocaleString('zh-CN'),
      channelNo: result.channel_no || form.value.channelNo
    }
    
    recognitionProgress.value = 100
    recognitionStatus.value = '识别完成！'
    
    ElMessage.success(`识别成功！共识别到 ${recognitionResult.value.totalCount} 件物品`)
    
  } catch (error) {
    console.error('识别失败:', error)
    ElMessage.error('识别失败：' + (error.response?.data?.detail || error.message || '未知错误'))
  } finally {
    setTimeout(() => {
      recognizing.value = false
      recognitionProgress.value = 0
      recognitionStatus.value = ''
    }, 1000)
  }
}

const clearImage = () => {
  imagePreview.value = ''
  imageFile.value = null
  recognitionResult.value = null
}

const submitCheckIn = () => {
  ElMessage.success('入场安检完成')
  setTimeout(() => {
    reset()
  }, 1500)
}

const reset = () => {
  userId.value = ''
  form.value = { idCard: '', weight: 0, channelNo: 1 }
  imagePreview.value = ''
  imageFile.value = null
  recognitionResult.value = null
}

onUnmounted(() => {
  // 清理资源
})
</script>

<style scoped>
.checkin-container {
  max-width: 1200px;
  margin: 0 auto;
}

.step-card {
  margin-bottom: 20px;
}

.step-card.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
}

/* 图片上传区域 */
.upload-area {
  margin: 20px 0;
}

.image-preview {
  margin-top: 20px;
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.preview-controls {
  margin-top: 20px;
  display: flex;
  gap: 15px;
  justify-content: center;
}

/* 识别进度 */
.recognition-progress {
  margin-top: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.recognition-progress p {
  margin-top: 10px;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.result-card {
  margin-top: 20px;
}

.result-summary {
  margin: 20px 0;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}
</style>
