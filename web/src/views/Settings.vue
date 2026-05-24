<template>
  <div class="settings">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">系统设置</h1>
        <p class="page-subtitle">配置服务参数、打印选项与数据管理</p>
      </div>
    </div>

    <div class="settings-cards">
      <!-- 服务配置 -->
      <el-card shadow="hover">
        <template #header>
          <div style="display:flex;align-items:center;gap:8px;">
            <el-icon style="color:var(--primary);"><Setting /></el-icon>
            <span>服务配置</span>
          </div>
        </template>

        <el-form :model="settings" label-width="140px" size="default">
          <el-form-item label="服务地址">
            <el-input v-model="settings.serviceHost" placeholder="0.0.0.0" style="max-width:320px" />
          </el-form-item>
          <el-form-item label="HTTP服务端口">
            <el-input-number v-model="settings.httpPort" :min="1024" :max="65535" />
          </el-form-item>
          <el-form-item label="API基础地址">
            <el-input v-model="settings.apiBaseUrl" placeholder="http://localhost:8181" style="max-width:400px" />
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 打印配置 -->
      <el-card class="section-gap" shadow="hover">
        <template #header>
          <div style="display:flex;align-items:center;gap:8px;">
            <el-icon style="color:var(--success);"><Printer /></el-icon>
            <span>打印配置</span>
          </div>
        </template>

        <el-form :model="settings" label-width="140px">
          <el-form-item label="自动打印">
            <el-switch v-model="settings.autoPrint" />
            <span style="margin-left:8px;font-size:0.85rem;color:var(--gray-500);">
              收到数据后自动发送打印任务
            </span>
          </el-form-item>
          <el-form-item label="打印机MAC地址">
            <el-input v-model="settings.printerMac" placeholder="00:11:22:33:44:55" style="max-width:320px" />
          </el-form-item>
          <el-form-item label="打印纸宽度">
            <el-select v-model="settings.paperWidth" style="width:160px">
              <el-option label="56mm" :value="56" />
              <el-option label="80mm" :value="80" />
            </el-select>
          </el-form-item>
          <el-form-item label="模拟打印模式">
            <el-switch v-model="settings.simulatePrint" />
            <span style="margin-left:8px;font-size:0.85rem;color:var(--gray-500);">
              不连接真实打印机，在日志中模拟输出
            </span>
          </el-form-item>

          <!-- 蓝牙设备扫描 -->
          <el-divider content-position="left">蓝牙设备管理</el-divider>
          <el-form-item label="连接模式">
            <el-radio-group v-model="connectMode" @change="switchMode">
              <el-radio value="serial">串口模式 (COM 口) - 打印推荐</el-radio>
              <el-radio value="bluetooth">蓝牙模式 - 查看设备名称和 MAC</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="蓝牙状态">
            <el-tag :type="btStatus.connected ? 'success' : 'info'">
              {{ btStatus.connected ? '已连接' : '未连接' }}
            </el-tag>
            <span style="margin-left:12px;color:var(--gray-500);">
              当前模式: {{ connectMode === 'serial' ? '串口模式' : '蓝牙模式' }}
            </span>
          </el-form-item>
          <el-form-item label="扫描设备">
            <el-button type="primary" @click="scanDevices" :loading="scanning">
              <el-icon><Search /></el-icon>
              {{ connectMode === 'serial' ? '扫描串口' : '扫描蓝牙' }}
            </el-button>
          </el-form-item>
          <el-form-item label="可用设备列表">
            <el-table :data="devices" style="width:700px" max-height="300" border>
              <el-table-column label="设备名称" prop="name" min-width="180">
                <template #default="{ row }">
                  <strong>{{ row.name }}</strong>
                </template>
              </el-table-column>
              <el-table-column label="端口/蓝牙MAC" width="180">
                <template #default="{ row }">
                  <div>
                    <div><code style="font-family:monospace;font-size:0.8rem;color:var(--primary);">{{ row.address }}</code></div>
                    <div v-if="row.mac_address" style="margin-top:2px;">
                      <code style="font-family:monospace;font-size:0.75rem;color:var(--gray-600);">MAC: {{ row.mac_address }}</code>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.paired ? 'success' : 'info'" size="small">
                    {{ row.paired ? '已配对' : '未配对' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="80">
                <template #default="{ row }">
                  <el-button
                    v-if="!btStatus.connected"
                    type="success"
                    size="small"
                    @click="connectToDevice(row)"
                  >
                    连接
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-form-item>
          <el-form-item label="或手动输入地址">
            <el-input v-model="manualMac" placeholder="例如: COM4 或 00:11:22:33:44:55" style="width:320px" />
            <el-button
              style="margin-left:8px;"
              type="success"
              :disabled="!manualMac || btStatus.connected"
              @click="connectManualDevice"
            >
              连接
            </el-button>
          </el-form-item>
          <el-form-item label="">
            <el-button
              type="danger"
              :disabled="!btStatus.connected"
              @click="disconnectDevice"
            >
              <el-icon><Close /></el-icon>
              断开连接
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 数据配置 -->
      <el-card class="section-gap" shadow="hover">
        <template #header>
          <div style="display:flex;align-items:center;gap:8px;">
            <el-icon style="color:var(--purple);"><Coin /></el-icon>
            <span>数据配置</span>
          </div>
        </template>

        <el-form :model="settings" label-width="140px">
          <el-form-item label="数据保留天数">
            <el-input-number v-model="settings.dataRetentionDays" :min="1" :max="365" />
            <span style="margin-left:8px;font-size:0.85rem;color:var(--gray-500);">
              超过此天数的记录将被自动清理
            </span>
          </el-form-item>
          <el-form-item label="数据库路径">
            <el-input v-model="settings.dbPath" placeholder="data/vision-center.db" style="max-width:400px" />
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 日志配置 -->
      <el-card class="section-gap" shadow="hover">
        <template #header>
          <div style="display:flex;align-items:center;gap:8px;">
            <el-icon style="color:var(--warning);"><Document /></el-icon>
            <span>日志配置</span>
          </div>
        </template>

        <el-form :model="settings" label-width="140px">
          <el-form-item label="日志级别">
            <el-select v-model="settings.logLevel" style="width:160px">
              <el-option label="DEBUG" value="DEBUG" />
              <el-option label="INFO" value="INFO" />
              <el-option label="WARNING" value="WARNING" />
              <el-option label="ERROR" value="ERROR" />
            </el-select>
          </el-form-item>
          <el-form-item label="日志文件路径">
            <el-input v-model="settings.logFile" placeholder="留空表示不保存到文件" style="max-width:400px" />
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 操作按钮 -->
      <div class="section-gap" style="display:flex;gap:12px;">
        <el-button type="primary" size="large" @click="saveSettings">
          <el-icon><Check /></el-icon>
          保存设置
        </el-button>
        <el-button size="large" @click="resetSettings">
          <el-icon><RefreshRight /></el-icon>
          重置为默认
        </el-button>
        <el-button size="large" @click="exportSettings">
          <el-icon><Download /></el-icon>
          导出配置
        </el-button>
        <el-button size="large" @click="importSettingsClick">
          <el-icon><Upload /></el-icon>
          导入配置
        </el-button>
      </div>
    </div>

    <input
      type="file"
      ref="fileInput"
      accept=".json"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Printer, Coin, Document, Check, RefreshRight, Download, Upload, Search, Connection, Close } from '@element-plus/icons-vue'
import axios from 'axios'

const fileInput = ref<HTMLInputElement | null>(null)

const defaultSettings = {
  serviceHost: '0.0.0.0',
  httpPort: 8191,
  apiBaseUrl: 'http://localhost:8191',
  autoPrint: false,
  printerMac: '',
  paperWidth: 56,
  simulatePrint: true,
  dataRetentionDays: 90,
  dbPath: 'data/vision-center.db',
  logLevel: 'INFO',
  logFile: ''
}

const settings = reactive({ ...defaultSettings })

// 蓝牙相关状态
const btStatus = reactive({
  available: false,
  connected: false
})
const connectMode = ref('serial') // 'serial' or 'bluetooth'
const scanning = ref(false)
type DeviceInfo = { address: string; name: string; paired: boolean; connected: boolean; mac_address?: string | null }

const devices = ref<DeviceInfo[]>([])
const selectedDevice = ref<any>(null)
const manualMac = ref('')

onMounted(() => {
  loadSettings()
  loadBoundDevice()
  checkBluetoothStatus()
})

// ============ 蓝牙功能 ============
const apiClient = axios.create({ baseURL: '/api' })

const checkBluetoothStatus = async () => {
  try {
    const res = await apiClient.get('/bluetooth/status')
    if (res.data.code === 0) {
      btStatus.available = res.data.data.available
      btStatus.connected = res.data.data.connected
      if (res.data.data.device) {
        upsertDevice({ ...res.data.data.device, connected: res.data.data.connected })
        saveBoundDevice(res.data.data.device)
      }
    }
  } catch (e) {
    console.log('蓝牙状态检查失败', e)
  }
}

const scanDevices = async () => {
  scanning.value = true
  devices.value = []
  selectedDevice.value = null
  try {
    ElMessage.info('正在扫描蓝牙设备，请稍候...')
    const res = await apiClient.get('/bluetooth/scan?duration=8')
    if (res.data.code === 0) {
      const saved = localStorage.getItem('boundPrinterDevice')
      const boundDevice = saved ? JSON.parse(saved) : null
      devices.value = res.data.data.devices.map((d: any) => ({
        ...d,
        connected: d.connected || (btStatus.connected && boundDevice?.address === d.address)
      }))
      if (boundDevice && !devices.value.some(d => d.address === boundDevice.address)) {
        upsertDevice({ ...boundDevice, connected: btStatus.connected })
      }
      if (devices.value.length === 0) {
        ElMessage.warning('未发现蓝牙设备，请确保打印机已开启')
      } else {
        ElMessage.success(`发现 ${devices.value.length} 个设备`)
      }
    }
  } catch (e) {
    ElMessage.error('扫描失败')
  } finally {
    scanning.value = false
  }
}

const connectToDevice = async (device: any) => {
  try {
    ElMessage.info(`正在连接 ${device.name}...`)
    const res = await apiClient.post('/bluetooth/connect', {
      address: device.address,
      name: device.name,
      mac_address: device.mac_address || null
    })
    if (res.data.code === 0) {
      ElMessage.success('连接成功！')
      devices.value.forEach(d => { d.connected = false })
      device.connected = true
      btStatus.connected = true
      settings.printerMac = device.address
      settings.simulatePrint = false
      saveBoundDevice(device)
      await saveSettings()
    }
  } catch (e) {
    ElMessage.error('连接失败，请确保设备已配对')
  }
}

const connectManualDevice = async () => {
  const mac = manualMac.value.trim()
  if (!mac) return
  try {
    const res = await apiClient.post('/bluetooth/connect', { address: mac, name: mac })
    if (res.data.code === 0) {
      ElMessage.success('连接成功！')
      btStatus.connected = true
      settings.printerMac = mac
      settings.simulatePrint = false
      saveBoundDevice({ address: mac, name: mac, paired: true, connected: true })
      await saveSettings()
    }
  } catch (e) {
    ElMessage.error('连接失败，请确保 MAC 地址正确且设备已配对')
  }
}

const disconnectDevice = async () => {
  try {
    await apiClient.post('/bluetooth/disconnect')
    ElMessage.info('已断开连接')
    btStatus.connected = false
    settings.simulatePrint = true
    devices.value.forEach(d => { d.connected = false })
    clearBoundDevice()
    checkBluetoothStatus()
  } catch (e) {
    ElMessage.error('断开失败')
  }
}

const switchMode = async () => {
  try {
    const res = await apiClient.post('/bluetooth/mode', { mode: connectMode.value })
    if (res.data.code === 0) {
      ElMessage.success(res.data.message || '已切换模式')
      // 清空状态
      devices.value = []
      selectedDevice.value = null
      btStatus.connected = false
      // 检查状态
      checkBluetoothStatus()
    }
  } catch (e) {
    ElMessage.error('切换模式失败')
  }
}

const loadSettings = () => {
  const saved = localStorage.getItem('systemSettings')
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      Object.assign(settings, parsed)
    } catch {
      ElMessage.warning('配置加载失败，使用默认配置')
    }
  }
}

const saveSettings = async () => {
  localStorage.setItem('systemSettings', JSON.stringify(settings))
  await apiClient.post('/settings/printer', {
    autoPrint: settings.autoPrint,
    simulatePrint: settings.simulatePrint,
    paperWidth: settings.paperWidth,
    printerMac: settings.printerMac
  })
  ElMessage.success('设置已保存')
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
  const index = devices.value.findIndex(d => d.address === device.address)
  if (index >= 0) {
    devices.value[index] = { ...devices.value[index], ...device }
  } else {
    devices.value.unshift(device)
  }
}

const resetSettings = async () => {
  await ElMessageBox.confirm('确定重置所有设置为默认值?', '确认')
  Object.assign(settings, defaultSettings)
  localStorage.removeItem('systemSettings')
  ElMessage.info('设置已重置')
}

const exportSettings = () => {
  const dataStr = JSON.stringify(settings, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = `vision-center-settings-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  ElMessage.success('配置已导出')
}

const importSettingsClick = () => {
  fileInput.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const content = e.target?.result as string
      const imported = JSON.parse(content)
      Object.assign(settings, imported)
      await saveSettings()
      ElMessage.success('配置已导入')
    } catch {
      ElMessage.error('配置文件格式错误')
    }
  }
  reader.readAsText(file)
  target.value = ''
}
</script>

<style scoped>
.settings-cards {
  display: flex;
  flex-direction: column;
}

.section-gap {
  margin-top: var(--space-4);
}
</style>
