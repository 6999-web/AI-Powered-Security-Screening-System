<template>
  <div class="checkout-container">
    <el-card class="step-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><UserFilled /></el-icon>
          <span>步骤 1：身份验证</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="100px">
        <el-form-item label="验证方式">
          <el-radio-group v-model="verifyMethod">
            <el-radio value="idcard">身份证</el-radio>
            <el-radio value="face">人脸识别</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="verifyMethod === 'idcard'" label="身份证号">
          <el-input v-model="form.idCard" placeholder="请输入身份证号" />
        </el-form-item>
        
        <el-form-item v-if="verifyMethod === 'face'" label="人脸照片">
          <el-upload
            class="upload-demo"
            :auto-upload="false"
            :on-change="handleFaceUpload"
            :show-file-list="false"
          >
            <el-button type="primary">
              <el-icon><Camera /></el-icon>
              拍摄/上传照片
            </el-button>
          </el-upload>
          <div v-if="facePreview" class="preview-image">
            <img :src="facePreview" alt="人脸照片" />
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button type="success" @click="verifyIdentity" :loading="verifying">
            验证身份
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-alert
        v-if="userId"
        title="身份验证成功，已匹配入场记录"
        type="success"
        :closable="false"
        show-icon
      >
        <template #default>
          用户ID: <strong>{{ userId }}</strong>
        </template>
      </el-alert>
    </el-card>

    <el-card v-if="userId && entryRecord" class="info-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Document /></el-icon>
          <span>入场记录</span>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="入场时间">
          {{ entryRecord.checkTime }}
        </el-descriptions-item>
        <el-descriptions-item label="通道号">
          {{ entryRecord.channelNo }}
        </el-descriptions-item>
        <el-descriptions-item label="物品总数">
          {{ entryRecord.totalCount }}
        </el-descriptions-item>
        <el-descriptions-item label="总重量">
          {{ entryRecord.totalWeight }} kg
        </el-descriptions-item>
      </el-descriptions>
      
      <el-table :data="entryRecord.items" border style="margin-top: 20px;">
        <el-table-column prop="name" label="物品名称" />
        <el-table-column prop="category" label="类别" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="weight" label="重量(kg)" />
      </el-table>
    </el-card>

    <el-card class="step-card" :class="{ disabled: !userId }">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Box /></el-icon>
          <span>步骤 2：离场物品识别</span>
        </div>
      </template>
      
      <!-- 摄像头未启动时显示点击区域 -->
      <div 
        v-if="!cameraActive && !imagePreview" 
        class="camera-trigger-area"
        @click="startCamera"
        :class="{ disabled: !userId }"
      >
        <el-icon class="camera-icon"><Camera /></el-icon>
        <div class="trigger-text">点击此处调用摄像头</div>
        <div class="trigger-tip">将自动识别并比对离场物品</div>
      </div>

      <!-- 摄像头实时预览 -->
      <div v-if="cameraActive" class="camera-preview">
        <video ref="videoElement" autoplay playsinline></video>
        <canvas ref="canvasElement" style="display: none;"></canvas>
        
        <div class="camera-controls">
          <el-button type="success" size="large" @click="captureAndRecognize" :loading="recognizing">
            <el-icon><Camera /></el-icon>
            {{ recognizing ? '识别中...' : '拍照并识别' }}
          </el-button>
          <el-button size="large" @click="stopCamera">
            关闭摄像头
          </el-button>
        </div>

        <!-- 识别进度 -->
        <div v-if="recognizing" class="recognition-progress">
          <el-progress :percentage="recognitionProgress" :status="recognitionProgress === 100 ? 'success' : undefined" />
          <p>{{ recognitionStatus }}</p>
        </div>
      </div>

      <!-- 拍摄的图片预览 -->
      <div v-if="imagePreview && !cameraActive" class="image-preview">
        <img :src="imagePreview" alt="拍摄的图片" />
        <div class="preview-controls">
          <el-button type="primary" @click="startCamera">
            <el-icon><Camera /></el-icon>
            重新拍摄
          </el-button>
        </div>
      </div>
      
      <!-- 物品信息表单 -->
      <el-form v-if="imagePreview && !cameraActive" :model="form" label-width="100px" style="margin-top: 20px;">
        <el-form-item label="物品重量">
          <el-input-number v-model="form.weight" :min="0" :precision="2" />
          <span style="margin-left: 10px;">kg</span>
        </el-form-item>
        
        <el-form-item label="通道号">
          <el-input-number v-model="form.channelNo" :min="1" />
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="comparisonResult" class="result-card">
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><DataAnalysis /></el-icon>
          <span>比对结果</span>
        </div>
      </template>
      
      <el-alert
        :title="comparisonResult.status === 'normal' ? '比对通过，无异常' : '检测到异常'"
        :type="comparisonResult.status === 'normal' ? 'success' : 'warning'"
        :closable="false"
        show-icon
        style="margin-bottom: 20px;"
      />
      
      <el-table :data="comparisonResult.items" border>
        <el-table-column prop="name" label="物品名称" />
        <el-table-column prop="category" label="类别" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="weight" label="重量(kg)" />
        <el-table-column label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'normal' ? 'success' : 'warning'">
              {{ row.statusText }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-if="comparisonResult.anomalies && comparisonResult.anomalies.length > 0" class="anomaly-section">
        <h3>异常详情</h3>
        <el-alert
          v-for="(anomaly, index) in comparisonResult.anomalies"
          :key="index"
          :title="anomaly.title"
          :type="anomaly.type"
          :description="anomaly.description"
          show-icon
          style="margin-bottom: 10px;"
        />
      </div>
      
      <div class="action-buttons">
        <el-button
          v-if="comparisonResult.status === 'normal'"
          type="success"
          size="large"
          @click="confirmCheckOut"
        >
          <el-icon><Check /></el-icon>
          确认放行
        </el-button>
        <el-button
          v-else
          type="warning"
          size="large"
          @click="handleAnomaly"
        >
          <el-icon><Warning /></el-icon>
          处理异常
        </el-button>
        <el-button size="large" @click="reset">
          <el-icon><RefreshLeft /></el-icon>
          重新识别
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const verifyMethod = ref('idcard')
const form = ref({
  idCard: '',
  weight: 0,
  channelNo: 1
})

const userId = ref('')
const verifying = ref(false)
const facePreview = ref('')
const faceFile = ref(null)

const entryRecord = ref(null)

// 摄像头相关
const cameraActive = ref(false)
const videoElement = ref(null)
const canvasElement = ref(null)
const mediaStream = ref(null)

const imagePreview = ref('')
const imageFile = ref(null)
const recognizing = ref(false)
const recognitionProgress = ref(0)
const recognitionStatus = ref('')
const comparisonResult = ref(null)

const handleFaceUpload = (file) => {
  faceFile.value = file.raw
  const reader = new FileReader()
  reader.onload = (e) => {
    facePreview.value = e.target.result
  }
  reader.readAsDataURL(file.raw)
}

const verifyIdentity = async () => {
  if (verifyMethod.value === 'idcard' && !form.value.idCard) {
    ElMessage.warning('请输入身份证号')
    return
  }
  if (verifyMethod.value === 'face' && !faceFile.value) {
    ElMessage.warning('请上传人脸照片')
    return
  }
  
  verifying.value = true
  try {
    // 调用身份验证API
    const formData = new FormData()
    if (verifyMethod.value === 'idcard') {
      formData.append('idCard', form.value.idCard)
    } else {
      formData.append('face', faceFile.value)
    }
    
    const result = await api.verifyIdentity(formData)
    userId.value = result.userId
    
    // 获取入场记录
    try {
      const record = await api.getComparison(userId.value)
      entryRecord.value = {
        checkTime: record.checkTimeFormatted || record.checkTime,
        channelNo: record.channelNo,
        totalCount: record.totalCount,
        totalWeight: record.totalWeight,
        items: record.items
      }
      ElMessage.success('身份验证成功，已匹配入场记录，请点击下方区域调用摄像头')
    } catch (error) {
      // 如果没有入场记录，提示用户先进行入场安检
      ElMessage.error('未找到入场记录，请先进行入场安检')
      userId.value = ''
      verifying.value = false
      return
    }
  } catch (error) {
    ElMessage.error('身份验证失败')
  } finally {
    verifying.value = false
  }
}

/**
 * 启动摄像头
 */
const startCamera = async () => {
  if (!userId.value) {
    ElMessage.warning('请先完成身份验证')
    return
  }

  try {
    // 先尝试使用默认配置
    let stream
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'environment'
        }
      })
    } catch (err) {
      // 如果失败，尝试使用更简单的配置
      console.warn('使用默认配置失败，尝试简化配置:', err)
      stream = await navigator.mediaDevices.getUserMedia({
        video: true
      })
    }
    
    mediaStream.value = stream
    cameraActive.value = true
    imagePreview.value = ''
    
    // 等待 DOM 更新
    setTimeout(() => {
      if (videoElement.value) {
        videoElement.value.srcObject = stream
      }
    }, 100)
    
    ElMessage.success('摄像头已启动，请将离场物品放在摄像头前')
  } catch (error) {
    console.error('摄像头启动失败:', error)
    if (error.name === 'NotAllowedError') {
      ElMessage.error('摄像头权限被拒绝，请在浏览器设置中允许访问摄像头')
    } else if (error.name === 'NotFoundError') {
      ElMessage.error('未检测到摄像头设备')
    } else if (error.name === 'NotReadableError') {
      ElMessage.error('摄像头被其他程序占用，请关闭其他使用摄像头的程序后重试')
    } else {
      ElMessage.error('无法访问摄像头：' + error.message)
    }
  }
}

/**
 * 停止摄像头
 */
const stopCamera = () => {
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach(track => track.stop())
    mediaStream.value = null
  }
  cameraActive.value = false
}

/**
 * 拍照并立即识别比对
 */
const captureAndRecognize = async () => {
  if (!videoElement.value || !canvasElement.value) {
    ElMessage.error('摄像头未就绪')
    return
  }
  
  recognizing.value = true
  recognitionProgress.value = 0
  recognitionStatus.value = '正在拍照...'
  
  try {
    // 1. 拍照
    const canvas = canvasElement.value
    const video = videoElement.value
    
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    const ctx = canvas.getContext('2d')
    ctx.drawImage(video, 0, 0)
    
    recognitionProgress.value = 20
    recognitionStatus.value = '正在处理图片...'
    
    // 2. 转换为 Blob
    const blob = await new Promise(resolve => {
      canvas.toBlob(resolve, 'image/jpeg', 0.9)
    })
    
    imageFile.value = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' })
    imagePreview.value = URL.createObjectURL(blob)
    
    recognitionProgress.value = 40
    recognitionStatus.value = '正在上传到服务器...'
    
    // 3. 调用 API 识别和比对
    const formData = new FormData()
    formData.append('image', imageFile.value)
    formData.append('userId', userId.value)
    formData.append('weight', form.value.weight)
    formData.append('channelNo', form.value.channelNo)
    
    recognitionProgress.value = 60
    recognitionStatus.value = '正在调用 AI 识别和比对...'
    
    const result = await api.checkOut(formData)
    
    recognitionProgress.value = 90
    recognitionStatus.value = '正在解析结果...'
    
    // 4. 显示比对结果
    comparisonResult.value = {
      status: result.status || 'normal',
      items: result.items || [],
      anomalies: result.anomalies || []
    }
    
    recognitionProgress.value = 100
    recognitionStatus.value = '识别完成！'
    
    // 停止摄像头
    stopCamera()
    
    if (result.status === 'normal') {
      ElMessage.success('比对通过，无异常')
    } else {
      ElMessage.warning('检测到异常，请查看详情')
    }
    
  } catch (error) {
    console.error('识别失败:', error)
    ElMessage.error('识别失败：' + (error.response?.data?.detail || error.message || '未知错误'))
    stopCamera()
  } finally {
    setTimeout(() => {
      recognizing.value = false
      recognitionProgress.value = 0
      recognitionStatus.value = ''
    }, 1000)
  }
}

const confirmCheckOut = () => {
  ElMessage.success('离场安检完成，正常放行')
  setTimeout(() => {
    reset()
  }, 1500)
}

const handleAnomaly = async () => {
  try {
    await ElMessageBox.confirm(
      '检测到异常，是否需要人工复核？',
      '异常处理',
      {
        confirmButtonText: '人工复核',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    ElMessage.info('已通知安检人员进行人工复核')
  } catch {
    // 取消操作
  }
}

const reset = () => {
  stopCamera()
  userId.value = ''
  form.value = { idCard: '', weight: 0, channelNo: 1 }
  facePreview.value = ''
  faceFile.value = null
  entryRecord.value = null
  imagePreview.value = ''
  imageFile.value = null
  comparisonResult.value = null
}

// 组件卸载时停止摄像头
onUnmounted(() => {
  stopCamera()
})
</script>

<style scoped>
.checkout-container {
  max-width: 1200px;
  margin: 0 auto;
}

.step-card,
.info-card,
.result-card {
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

/* 摄像头触发区域 */
.camera-trigger-area {
  text-align: center;
  padding: 60px 20px;
  border: 3px dashed #409eff;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8f4ff 100%);
}

.camera-trigger-area:hover {
  border-color: #66b1ff;
  background: linear-gradient(135deg, #e8f4ff 0%, #d9ecff 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.camera-trigger-area.disabled {
  cursor: not-allowed;
  opacity: 0.5;
  border-color: #dcdfe6;
  background: #f5f7fa;
}

.camera-trigger-area.disabled:hover {
  transform: none;
  box-shadow: none;
}

.camera-icon {
  font-size: 80px;
  color: #409eff;
  margin-bottom: 20px;
}

.trigger-text {
  font-size: 20px;
  color: #303133;
  font-weight: 500;
  margin-bottom: 10px;
}

.trigger-tip {
  font-size: 14px;
  color: #909399;
}

/* 摄像头预览 */
.camera-preview {
  text-align: center;
}

.camera-preview video {
  width: 100%;
  max-width: 800px;
  border-radius: 12px;
  background: #000;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.camera-controls {
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

/* 图片预览 */
.preview-image,
.image-preview {
  margin-top: 20px;
  text-align: center;
}

.preview-image img,
.image-preview img {
  max-width: 100%;
  max-height: 500px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.preview-controls {
  margin-top: 20px;
  display: flex;
  gap: 15px;
  justify-content: center;
}

.anomaly-section {
  margin: 20px 0;
}

.anomaly-section h3 {
  margin-bottom: 15px;
  color: #e6a23c;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}
</style>
