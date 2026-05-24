import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

// API 客户端
const apiClient = axios.create({
  baseURL: '/api'
})

// 检查记录类型
export interface PatientInfo {
  patientName: string
  patientId: string
  phone?: string
  birthday?: string
  gender?: string
}

export interface CheckMetadata {
  checkTime: string
  deviceType: string
  deviceId?: string
}

export interface EyeData {
  vision?: string
  logVision?: string
  subVision?: string
  ref?: string
  speed?: string
  isLowVision?: boolean
  lowVision?: string
}

export interface VisionChartData {
  visionType?: string
  spaceType?: string
  environment?: string
  eyeCorrect?: string
  testMode?: string
  openMirror?: boolean
  deviceName?: string
  eyes?: EyeData
  od?: EyeData
  os?: EyeData
}

export interface CheckRecord {
  id: string
  patientInfo: PatientInfo
  metadata: CheckMetadata
  visionChartData?: VisionChartData
  printed: boolean
  printTime?: string
}

export const useAppStore = defineStore('app', () => {
  const records = ref<CheckRecord[]>([])
  const loading = ref(false)

  // 获取记录列表
  const fetchRecords = async () => {
    loading.value = true
    try {
      const response = await apiClient.get('/records')
      if (response.data.code === 0) {
        records.value = response.data.data.records
      }
    } catch (error) {
      console.error('获取记录失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 打印记录
  const printRecord = async (recordId: string) => {
    try {
      const response = await apiClient.post(`/print/${recordId}`)
      return response.data
    } catch (error) {
      console.error('打印失败:', error)
      throw error
    }
  }

  // 打印测试页
  const printTestPage = async () => {
    try {
      const response = await apiClient.post('/print/test')
      return response.data
    } catch (error) {
      console.error('打印测试页失败:', error)
      throw error
    }
  }

  return {
    records,
    loading,
    fetchRecords,
    printRecord,
    printTestPage
  }
})