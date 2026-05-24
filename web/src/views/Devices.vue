<template>
  <div class="devices">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">设备管理</h1>
        <p class="page-subtitle">管理蓝牙设备连接与打印机配置</p>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="refreshDevices" :loading="scanning">
          <el-icon><Refresh /></el-icon>
          扫描设备
        </el-button>
      </div>
    </div>

    <!-- 设备统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon blue">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="stat-value">{{ discoveredDevices.length }}</div>
        <div class="stat-label">已发现设备</div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-value" style="color: var(--success)">{{ discoveredDevices.filter(d => d.connected).length }}</div>
        <div class="stat-label">已连接</div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon purple">
          <el-icon><Remove /></el-icon>
        </div>
        <div class="stat-value" style="color: var(--gray-500)">{{ discoveredDevices.filter(d => !d.connected).length }}</div>
        <div class="stat-label">未连接</div>
      </el-card>
    </div>

    <!-- 连接模式选择 -->
    <el-card class="section-gap" shadow="hover">
      <template #header>
        <span>连接模式</span>
      </template>
      <el-radio-group v-model="connectMode" @change="switchMode">
        <el-radio value="serial">COM 口（推荐，更稳定）</el-radio>
        <el-radio value="bluetooth">直接蓝牙</el-radio>
      </el-radio-group>
    </el-card>

    <!-- 打印机配置 -->
    <el-card class="section-gap" shadow="hover">
      <template #header>
        <span>打印机配置</span>
      </template>

      <el-form :model="printerConfig" label-width="140px">
        <el-form-item label="当前状态">
          <el-tag :type="btStatus.connected ? 'success' : 'info'">
            {{ btStatus.connected ? '已连接' : '未连接' }}
          </el-tag>
        </el-form-item>
        <el-form-item label="自动打印">
          <el-switch v-model="printerConfig.autoPrint" />
        </el-form-item>
        <el-form-item label="打印纸宽度">
          <el-select v-model="printerConfig.paperWidth" style="width:160px">
            <el-option label="56mm" :value="56" />
            <el-option label="80mm" :value="80" />
          </el-select>
        </el-form-item>
        <el-form-item label="模拟模式">
          <el-switch v-model="printerConfig.simulate" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="savePrinterConfig">保存配置</el-button>
          <el-button type="success" @click="printTestPage" :disabled="!btStatus.connected && !printerConfig.simulate">
            打印测试页
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 蓝牙设备列表 -->
    <el-card class="section-gap" shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>{{ connectMode === 'serial' ? 'COM 口列表' : '蓝牙设备列表' }}</span>
        </div>
      </template>

      <el-table :data="discoveredDevices" v-loading="scanning" empty-text="未发现设备，请点击扫描">
        <el-table-column label="设备名称" min-width="180">
          <template #default="{ row }">
            <strong>{{ row.name || '未知设备' }}</strong>
          </template>
        </el-table-column>
        <el-table-column label="端口/蓝牙MAC" width="200">
          <template #default="{ row }">
            <div>
              <div><code style="font-family:var(--font-mono);font-size:0.8rem;color:var(--primary);">{{ row.address }}</code></div>
              <div v-if="row.mac_address" style="margin-top:2px;">
                <code style="font-family:var(--font-mono);font-size:0.75rem;color:var(--gray-600);">MAC: {{ row.mac_address }}</code>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="paired" label="配对状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.paired ? 'success' : 'info'" size="small" effect="light" v-if="connectMode === 'bluetooth'">
              {{ row.paired ? '已配对' : '未配对' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="连接状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.connected ? 'success' : 'info'" size="small" effect="light">
              <span style="display:flex;align-items:center;gap:4px;">
                <span :style="{width:'6px',height:'6px',borderRadius:'50%',background:row.connected?'var(--success)':'var(--gray-400)'}"></span>
                {{ row.connected ? '已连接' : '未连接' }}
              </span>
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              v-if="!row.connected"
              size="small"
              type="success"
              @click="connectDevice(row)"
              :disabled="btStatus.connected"
            >连接</el-button>
            <el-button
              v-else
              size="small"
              type="danger"
              @click="disconnectDevice(row)"
            >断开</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Monitor, CircleCheck, Remove } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores'
import axios from 'axios'

const store = useAppStore()

const apiClient = axios.create({ baseURL: '/api' })

const scanning = ref(false)
const connectMode = ref('serial') // 'serial' or 'bluetooth'

const printerConfig = ref({
  macAddress: '',
  autoPrint: false,
  paperWidth: 56,
  simulate: true
})

const btStatus = ref({
  available: false,
  connected: false
})

type DeviceInfo = { address: string; name: string; paired: boolean; connected: boolean; mac_address?: string | null; rssi?: number }

const discoveredDevices = ref<DeviceInfo[]>([])

onMounted(() => {
  loadPrinterConfig()
  loadBoundDevice()
  checkBluetoothStatus()
})

const checkBluetoothStatus = async () => {
  try {
    const res = await apiClient.get('/bluetooth/status')
    if (res.data.code === 0) {
      btStatus.value.available = res.data.data.available
      btStatus.value.connected = res.data.data.connected
      if (res.data.data.device) {
        upsertDevice({ ...res.data.data.device, connected: res.data.data.connected })
        saveBoundDevice(res.data.data.device)
      }
    }
  } catch (e) {
    console.log('检查蓝牙状态失败', e)
  }
}

const loadPrinterConfig = () => {
  const saved = localStorage.getItem('printerConfig')
  if (saved) {
    try {
      printerConfig.value = JSON.parse(saved)
    } catch {
      console.log('加载配置失败')
    }
  }
}

const savePrinterConfig = async () => {
  localStorage.setItem('printerConfig', JSON.stringify(printerConfig.value))
  await apiClient.post('/settings/printer', {
    autoPrint: printerConfig.value.autoPrint,
    simulatePrint: printerConfig.value.simulate,
    paperWidth: printerConfig.value.paperWidth,
    printerMac: printerConfig.value.macAddress
  })
  ElMessage.success('配置已保存')
}

const saveBoundDevice = (device: DeviceInfo) => {
  localStorage.setItem('boundPrinterDevice', JSON.stringify(device))
}

const loadBoundDevice = () => {
  const saved = localStorage.getItem('boundPrinterDevice')
  if (!saved) return
  try {
    upsertDevice(JSON.parse(saved))
  } catch {
    localStorage.removeItem('boundPrinterDevice')
  }
}

const clearBoundDevice = () => {
  localStorage.removeItem('boundPrinterDevice')
}

const upsertDevice = (device: DeviceInfo) => {
  const index = discoveredDevices.value.findIndex(d => d.address === device.address)
  if (index >= 0) {
    discoveredDevices.value[index] = { ...discoveredDevices.value[index], ...device }
  } else {
    discoveredDevices.value.unshift(device)
  }
}

const printTestPage = async () => {
  try {
    await store.printTestPage()
    ElMessage.success('测试页已发送')
  } catch {
    ElMessage.error('测试页发送失败')
  }
}

const refreshDevices = async () => {
  scanning.value = true
  try {
    const res = await apiClient.get('/bluetooth/scan', { params: { duration: 5 } })
    if (res.data.code === 0) {
      const saved = localStorage.getItem('boundPrinterDevice')
      const boundDevice = saved ? JSON.parse(saved) : null
      discoveredDevices.value = res.data.data.devices.map((d: any) => ({
        ...d,
        connected: d.connected || (btStatus.value.connected && boundDevice?.address === d.address),
        rssi: -70
      }))
      if (boundDevice && !discoveredDevices.value.some(d => d.address === boundDevice.address)) {
        upsertDevice({ ...boundDevice, connected: btStatus.value.connected })
      }
      ElMessage.success(`已发现 ${discoveredDevices.value.length} 个设备`)
    }
  } catch (e) {
    ElMessage.error('扫描失败')
  } finally {
    scanning.value = false
  }
}

const connectDevice = async (device: any) => {
  try {
    ElMessage.info(`正在连接 ${device.name}...`)
    const res = await apiClient.post('/bluetooth/connect', {
      address: device.address,
      name: device.name,
      mac_address: device.mac_address || null
    })
    if (res.data.code === 0) {
      discoveredDevices.value.forEach(d => { d.connected = false })
      device.connected = true
      btStatus.value.connected = true
      printerConfig.value.macAddress = device.address
      printerConfig.value.simulate = false
      saveBoundDevice(device)
      ElMessage.success(`已连接到 ${device.name}`)
      savePrinterConfig()
    }
  } catch (e) {
    ElMessage.error('连接失败')
  }
}

const disconnectDevice = async (device: any) => {
  try {
    ElMessage.info(`正在断开 ${device.name}...`)
    await apiClient.post('/bluetooth/disconnect')
    device.connected = false
    btStatus.value.connected = false
    printerConfig.value.simulate = true
    clearBoundDevice()
    ElMessage.success(`已断开 ${device.name}`)
    savePrinterConfig()
  } catch (e) {
    ElMessage.error('断开失败')
  }
}

const switchMode = async () => {
  try {
    const res = await apiClient.post('/bluetooth/mode', { mode: connectMode.value })
    if (res.data.code === 0) {
      ElMessage.success(res.data.message || '已切换模式')
      discoveredDevices.value = []
      checkBluetoothStatus()
    }
  } catch (e) {
    ElMessage.error('切换模式失败')
  }
}
</script>

<style scoped>
.devices {
  /* styles via global.css */
}
</style>
