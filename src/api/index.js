import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000
})

request.interceptors.response.use(
  response => response.data,
  error => {
    ElMessage.error(error.response?.data?.message || '请求失败')
    return Promise.reject(error)
  }
)

export default {
  // 入场安检 - X 光 Demo 版本
  checkIn(data) {
    return request.post('/entry', data)
  },
  
  // 离场安检 - X 光 Demo 版本
  checkOut(data) {
    return request.post('/exit', data)
  },
  
  // 获取比对结果
  getComparison(userId) {
    return request.get(`/compare/${userId}`)
  },
  
  // 获取异常记录
  getAnomalies(params) {
    return request.get('/anomalies', { params })
  },
  
  // 获取统计数据
  getStatistics() {
    return request.get('/statistics')
  },
  
  // 获取最近记录
  getRecentRecords(limit = 10) {
    return request.get('/recent-records', { params: { limit } })
  },
  
  // 获取最近异常
  getRecentAnomalies(limit = 10) {
    return request.get('/recent-anomalies', { params: { limit } })
  },
  
  // 获取通道信息
  getChannels() {
    return request.get('/channels')
  },
  
  // 身份验证
  verifyIdentity(data) {
    return request.post('/verify-identity', data)
  }
}
