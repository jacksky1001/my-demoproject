<template>
  <div class="test-tool">
    <el-row :gutter="20">
      <!-- 左侧：参数表单 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>设备手工测试</span>
              <div>
                <el-radio-group v-model="deviceType" size="small" @change="onDeviceTypeChange">
                  <el-radio-button value="vision-chart">视力表</el-radio-button>
                  <el-radio-button value="biometer">生物测量仪</el-radio-button>
                  <el-radio-button value="vision-screening">视力筛查仪</el-radio-button>
                </el-radio-group>
                <el-button type="success" @click="randomGenerate" style="margin-left:10px">
                  <el-icon><Refresh /></el-icon>
                  随机生成
                </el-button>
              </div>
            </div>
          </template>

          <el-form :model="formData" label-width="120px" size="default">
            <!-- 患者信息（通用） -->
            <el-divider content-position="left">患者信息</el-divider>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="姓名">
                  <el-input v-model="formData.patientName" placeholder="请输入姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="ID">
                  <el-input v-model="formData.patientId" placeholder="请输入ID" />
                </el-form-item>
              </el-col>
            </el-row>

            <!-- ===== 电子视力表参数 ===== -->
            <template v-if="deviceType === 'vision-chart'">
              <el-divider content-position="left">检查参数</el-divider>
              <el-row :gutter="16">
                <el-col :span="8">
                  <el-form-item label="视标" label-width="60px">
                    <el-select v-model="formData.visionType" style="width:100%">
                      <el-option label="E字" value="E" />
                      <el-option label="C字" value="C" />
                      <el-option label="字母" value="letter" />
                      <el-option label="数字" value="number" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="距离" label-width="50px">
                    <el-select v-model="formData.spaceType" style="width:100%">
                      <el-option label="5m" value="5m" />
                      <el-option label="3m" value="3m" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="矫正" label-width="50px">
                    <el-select v-model="formData.eyeCorrect" style="width:100%">
                      <el-option label="裸眼" value="裸眼" />
                      <el-option label="框架镜" value="框架镜" />
                      <el-option label="隐形眼镜" value="隐形眼镜" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-divider content-position="left">视力数据</el-divider>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-card shadow="never" class="eye-card">
                    <template #header><strong>右眼 (OD)</strong></template>
                    <el-form-item label="视力值" label-width="60px">
                      <el-input v-model="formData.odVision" placeholder="1.0" size="small" />
                    </el-form-item>
                    <el-form-item label="对数" label-width="60px">
                      <el-input v-model="formData.odLog" placeholder="5.0" size="small" />
                    </el-form-item>
                  </el-card>
                </el-col>
                <el-col :span="12">
                  <el-card shadow="never" class="eye-card">
                    <template #header><strong>左眼 (OS)</strong></template>
                    <el-form-item label="视力值" label-width="60px">
                      <el-input v-model="formData.osVision" placeholder="0.8" size="small" />
                    </el-form-item>
                    <el-form-item label="对数" label-width="60px">
                      <el-input v-model="formData.osLog" placeholder="4.9" size="small" />
                    </el-form-item>
                  </el-card>
                </el-col>
              </el-row>
            </template>

            <!-- ===== 生物测量仪参数 ===== -->
            <template v-if="deviceType === 'biometer'">
              <el-divider content-position="left">测量数据</el-divider>
              <el-table :data="biometerFields" border size="small">
                <el-table-column prop="label" label="参数" width="100" />
                <el-table-column label="右眼 (OD)">
                  <template #default="{ row }">
                    <el-input v-model="formData.bmOd[row.key]" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="左眼 (OS)">
                  <template #default="{ row }">
                    <el-input v-model="formData.bmOs[row.key]" size="small" />
                  </template>
                </el-table-column>
              </el-table>
            </template>

            <!-- ===== 视力筛查仪参数 ===== -->
            <template v-if="deviceType === 'vision-screening'">
              <el-divider content-position="left">验光数据</el-divider>
              <el-table :data="screeningFields" border size="small">
                <el-table-column prop="label" label="参数" width="80" />
                <el-table-column label="右眼 (OD)">
                  <template #default="{ row }">
                    <el-input v-model="formData.vsOd[row.key]" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="左眼 (OS)">
                  <template #default="{ row }">
                    <el-input v-model="formData.vsOs[row.key]" size="small" />
                  </template>
                </el-table-column>
              </el-table>
              <el-form-item label="瞳距 (PD)" style="margin-top:10px">
                <el-input v-model="formData.vsPd" style="width:120px" size="small">
                  <template #suffix>mm</template>
                </el-input>
              </el-form-item>
            </template>

            <el-divider content-position="left">设备信息</el-divider>
            <el-form-item label="设备编号">
              <el-input v-model="formData.deviceNumber" style="width:200px" placeholder="如: VC-001" />
            </el-form-item>

            <el-form-item style="margin-top:20px">
              <el-button type="primary" size="large" @click="submitTest" :loading="submitting">
                <el-icon><Upload /></el-icon>
                模拟提交并打印
              </el-button>
              <el-button size="large" @click="submitOnly" :loading="submitting">
                仅提交不打印
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：打印预览 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>热敏打印机 - 打印效果模拟</span>
          </template>

          <div v-if="!lastRecordId" class="empty-state">
            <el-icon :size="64"><Printer /></el-icon>
            <p>尚未发送测试数据</p>
            <p style="color:#999;font-size:13px;">提交数据后将在此显示打印效果</p>
          </div>

          <div v-else class="thermal-printer">
            <div class="printer-body">
              <div class="printer-top">
                <span class="printer-brand">VISION CENTER</span>
                <span class="printer-model">56mm Thermal Printer</span>
              </div>
              <div class="paper-slot">
                <div class="thermal-paper">
                  <div class="paper-content">
                    <!-- 标题 -->
                    <div class="receipt-line receipt-center receipt-bold receipt-large">=== 视力中心 ===</div>
                    <div class="receipt-line receipt-center receipt-bold" style="font-size:13px">
                      {{ deviceLabel }}报告
                    </div>
                    <div class="receipt-line receipt-center receipt-dots">------------------------</div>
                    <div class="receipt-line">姓名: {{ tickData.patientName }}</div>
                    <div class="receipt-line">ID: {{ tickData.patientId }}</div>
                    <div class="receipt-line">时间: {{ tickData.checkTime }}</div>
                    <div class="receipt-line">设备: {{ deviceLabel }}</div>
                    <div class="receipt-line receipt-dots">------------------------</div>

                    <!-- 视力表预览 -->
                    <template v-if="lastDeviceType === 'vision-chart'">
                      <div class="receipt-line receipt-bold">          右眼      左眼</div>
                      <div class="receipt-line">视力:      {{ tickData.odVision || '-' }}<span class="spacer">{{ tickData.osVision || '-' }}</span></div>
                      <div class="receipt-line">对数:      {{ tickData.odLog || '-' }}<span class="spacer">{{ tickData.osLog || '-' }}</span></div>
                      <div class="receipt-line">矫正: {{ tickData.eyeCorrect || '-' }}</div>
                      <div class="receipt-line">视标: {{ tickData.visionType || '-' }}</div>
                    </template>

                    <!-- 生物测量仪预览 -->
                    <template v-if="lastDeviceType === 'biometer'">
                      <div class="receipt-line receipt-bold">参数          OD        OS</div>
                      <div class="receipt-line" v-for="f in biometerFields" :key="f.key">
                        {{ f.label }}:        {{ tickData.bmOd?.[f.key] || '-' }}<span class="spacer2">{{ tickData.bmOs?.[f.key] || '-' }}</span>
                      </div>
                    </template>

                    <!-- 视力筛查仪预览 -->
                    <template v-if="lastDeviceType === 'vision-screening'">
                      <div class="receipt-line receipt-bold">参数       S        C        A</div>
                      <div class="receipt-line">OD:      {{ tickData.vsOd?.sph || '-' }}<span style="margin-left:10px">{{ tickData.vsOd?.cyl || '-' }}</span><span style="margin-left:14px">{{ tickData.vsOd?.axis || '-' }}</span></div>
                      <div class="receipt-line">OS:      {{ tickData.vsOs?.sph || '-' }}<span style="margin-left:10px">{{ tickData.vsOs?.cyl || '-' }}</span><span style="margin-left:14px">{{ tickData.vsOs?.axis || '-' }}</span></div>
                      <div class="receipt-line">PD: {{ tickData.vsPd || '-' }}mm</div>
                    </template>

                    <div class="receipt-line">&nbsp;</div>
                    <div class="receipt-center">
                      <img v-if="qrDataUrl" :src="qrDataUrl" class="qrcode-img" alt="QR" />
                      <div style="font-size:10px;margin-top:4px;">扫码查看完整数据</div>
                    </div>
                    <div class="receipt-line">&nbsp;</div>
                    <div class="receipt-line">&nbsp;</div>
                    <div class="receipt-cut">- - - - - - 撕纸线 - - - - - -</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 结果对话框 -->
    <el-dialog v-model="resultVisible" title="提交结果" width="500px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="记录ID">{{ resultRecordId }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ deviceLabel }}</el-descriptions-item>
        <el-descriptions-item label="患者">{{ resultPatientName }}</el-descriptions-item>
        <el-descriptions-item label="打印状态">
          <el-tag :type="resultPrinted ? 'success' : 'info'">{{ resultPrinted ? '已打印' : '未打印' }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="resultVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Upload, Printer } from '@element-plus/icons-vue'
import axios from 'axios'

const apiClient = axios.create({ baseURL: '/api' })

// 设备类型
const deviceType = ref('vision-chart')
const lastDeviceType = ref('')

const deviceLabel = computed(() => {
  const map: Record<string, string> = { 'vision-chart': '视力检查', 'biometer': '生物测量', 'vision-screening': '视力筛查' }
  return map[deviceType.value] || ''
})

// 生物测量仪字段配置
const biometerFields = [
  { label: 'AL(mm)', key: 'al' },
  { label: 'K1(D)', key: 'k1' },
  { label: 'K2(D)', key: 'k2' },
  { label: 'Km(D)', key: 'km' },
  { label: 'Astig(D)', key: 'astig' },
  { label: 'ACD(mm)', key: 'acd' },
  { label: 'LT(mm)', key: 'lt' },
  { label: 'WTW(mm)', key: 'wtW' },
]

// 视力筛查仪字段配置
const screeningFields = [
  { label: 'S', key: 'sph' },
  { label: 'C', key: 'cyl' },
  { label: 'A', key: 'axis' },
  { label: 'VA', key: 'va' },
  { label: 'pupil', key: 'pupil' },
]

const names = ['张', '李', '王', '赵', '陈', '刘', '黄', '周', '吴', '郑']
const givens = ['明', '华', '强', '丽', '伟', '芳', '敏', '静', '勇', '磊', '军', '霞', '娜', '涛', '鑫']
const vs = ['0.6', '0.8', '1.0', '1.2', '1.5', '0.5', '0.4', '0.3', '0.7', '0.9']
const sx = ['-0.50', '-1.00', '-2.00', '-2.50', '-1.50', '0.00', '+0.50']
const cx = ['-0.50', '-0.75', '-1.00', '-1.25', '-1.50', '-0.25']
const ax = ['180', '175', '170', '165', '5', '10', '90', '85']

// 统一表单数据
const formData = reactive<Record<string, any>>({
  patientName: '', patientId: '', deviceNumber: '',
  // vision-chart
  visionType: 'E', spaceType: '5m', eyeCorrect: '裸眼',
  odVision: '', odLog: '', osVision: '', osLog: '',
  // biometer
  bmOd: {} as Record<string, string>, bmOs: {} as Record<string, string>,
  // vision-screening
  vsOd: {} as Record<string, string>, vsOs: {} as Record<string, string>,
  vsPd: '62'
})

const submitting = ref(false)
const lastRecordId = ref('')
const resultVisible = ref(false)
const resultRecordId = ref('')
const resultPatientName = ref('')
const resultPrinted = ref(false)
const qrDataUrl = ref('')

const tickData = reactive<Record<string, any>>({})

const randomPick = (arr: string[]) => arr[Math.floor(Math.random() * arr.length)]
const rnd = (min: number, max: number, dec: number) => (Math.random() * (max - min) + min).toFixed(dec)

const randomGenerate = () => {
  formData.patientName = randomPick(names) + randomPick(givens) + (Math.random() > 0.5 ? randomPick(givens) : '')
  formData.patientId = 'P' + String(Math.floor(Math.random() * 90000) + 10000)

  if (deviceType.value === 'vision-chart') {
    formData.visionType = randomPick(['E', 'C', 'letter', 'number'])
    formData.spaceType = randomPick(['5m', '3m'])
    formData.eyeCorrect = randomPick(['裸眼', '框架镜', '隐形眼镜'])
    formData.deviceNumber = 'VC-' + String(Math.floor(Math.random() * 900) + 100).padStart(3, '0')
    const rv = randomPick(vs); const lv = randomPick(vs)
    formData.odVision = rv; formData.odLog = (parseFloat(rv) + 4.0).toFixed(1)
    formData.osVision = lv; formData.osLog = (parseFloat(lv) + 4.0).toFixed(1)
  } else if (deviceType.value === 'biometer') {
    formData.deviceNumber = 'BM-' + String(Math.floor(Math.random() * 900) + 100).padStart(3, '0')
    const bmOd: Record<string, string> = {}; const bmOs: Record<string, string> = {}
    bmOd.al = rnd(22, 26, 2); bmOd.k1 = rnd(42, 45, 2); bmOd.k2 = rnd(43, 46, 2)
    bmOd.km = ((parseFloat(bmOd.k1) + parseFloat(bmOd.k2)) / 2).toFixed(2)
    bmOd.astig = Math.abs(parseFloat(bmOd.k2) - parseFloat(bmOd.k1)).toFixed(2)
    bmOd.acd = rnd(2.5, 3.8, 2); bmOd.lt = rnd(3.5, 4.5, 2); bmOd.wtW = rnd(10.5, 12.5, 2)
    bmOs.al = rnd(22, 26, 2); bmOs.k1 = rnd(42, 45, 2); bmOs.k2 = rnd(43, 46, 2)
    bmOs.km = ((parseFloat(bmOs.k1) + parseFloat(bmOs.k2)) / 2).toFixed(2)
    bmOs.astig = Math.abs(parseFloat(bmOs.k2) - parseFloat(bmOs.k1)).toFixed(2)
    bmOs.acd = rnd(2.5, 3.8, 2); bmOs.lt = rnd(3.5, 4.5, 2); bmOs.wtW = rnd(10.5, 12.5, 2)
    formData.bmOd = bmOd; formData.bmOs = bmOs
  } else if (deviceType.value === 'vision-screening') {
    formData.deviceNumber = 'VS-' + String(Math.floor(Math.random() * 900) + 100).padStart(3, '0')
    formData.vsOd = { sph: randomPick(sx), cyl: randomPick(cx), axis: randomPick(ax), va: randomPick(vs), pupil: rnd(3, 5, 1) }
    formData.vsOs = { sph: randomPick(sx), cyl: randomPick(cx), axis: randomPick(ax), va: randomPick(vs), pupil: rnd(3, 5, 1) }
    formData.vsPd = rnd(58, 65, 1)
  }
}

const onDeviceTypeChange = () => {
  randomGenerate()
}

const buildPayload = () => {
  const payload: Record<string, any> = {
    patientName: formData.patientName,
    patientId: formData.patientId,
    deviceId: formData.deviceNumber
  }
  if (deviceType.value === 'vision-chart') {
    payload.visionType = formData.visionType
    payload.spaceType = formData.spaceType
    payload.eyeCorrect = formData.eyeCorrect
    payload.right = formData.odVision + '(' + formData.odLog + ')'
    payload.left = formData.osVision + '(' + formData.osLog + ')'
  } else if (deviceType.value === 'biometer') {
    payload.od = { ...formData.bmOd }
    payload.os = { ...formData.bmOs }
    payload.calculationMode = 'SRK/T'
  } else if (deviceType.value === 'vision-screening') {
    payload.od = { ...formData.vsOd }
    payload.os = { ...formData.vsOs }
    payload.pd = formData.vsPd
    payload.examMode = 'Auto'
  }
  return payload
}

const updateTickData = () => {
  const now = new Date()
  tickData.patientName = formData.patientName
  tickData.patientId = formData.patientId
  tickData.checkTime = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0') + ' ' + String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0')
  tickData.odVision = formData.odVision; tickData.odLog = formData.odLog
  tickData.osVision = formData.osVision; tickData.osLog = formData.osLog
  tickData.eyeCorrect = formData.eyeCorrect; tickData.visionType = formData.visionType
  tickData.bmOd = formData.bmOd; tickData.bmOs = formData.bmOs
  tickData.vsOd = formData.vsOd; tickData.vsOs = formData.vsOs; tickData.vsPd = formData.vsPd
  lastDeviceType.value = deviceType.value

  const payload = buildPayload()
  const qrJson = JSON.stringify({
    version: '1.0',
    generateTime: new Date().toISOString(),
    patientInfo: { name: formData.patientName, id: formData.patientId, phone: '' },
    checkData: [{ deviceType: deviceType.value, checkTime: new Date().toISOString(), data: payload }]
  })
  qrDataUrl.value = 'https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=' + encodeURIComponent(qrJson)
}

const submitTest = async () => {
  if (!formData.patientName || !formData.patientId) {
    ElMessage.warning('请至少填写患者姓名和ID')
    return
  }
  submitting.value = true
  try {
    const payload = buildPayload()
    let resp
    if (deviceType.value === 'vision-chart') {
      const time = new Date()
      const timeStr = time.getFullYear() + '-' + String(time.getMonth() + 1).padStart(2, '0') + '-' + String(time.getDate()).padStart(2, '0') + '-' + String(time.getHours()).padStart(2, '0') + '-' + String(time.getMinutes()).padStart(2, '0') + '-' + String(time.getSeconds()).padStart(2, '0')
      const params = new URLSearchParams({
        visionType: payload.visionType, eyes: '2.0(5.3)', right: payload.right,
        left: payload.left, spaceType: payload.spaceType || '5m',
        resultTime: timeStr, userName: payload.patientName, userId: payload.patientId,
        deviceNumber: payload.deviceId || '', eyeCorrect: payload.eyeCorrect || ''
      })
      resp = await apiClient.get('receive/vision-chart?' + params.toString())
    } else if (deviceType.value === 'biometer') {
      resp = await apiClient.post('/receive/biometer', payload)
    } else {
      resp = await apiClient.post('/receive/vision-screening', payload)
    }
    if (resp.data.code === 0) {
      const recordId = resp.data.data.recordId
      lastRecordId.value = recordId
      resultRecordId.value = recordId
      resultPatientName.value = formData.patientName
      updateTickData()
      try {
        const pr = await apiClient.post('/print/' + recordId)
        resultPrinted.value = pr.data.code === 0
      } catch { resultPrinted.value = false }
      resultVisible.value = true
    }
  } catch (e: any) {
    ElMessage.error('提交失败: ' + (e?.message || e?.toString() || ''))
  } finally {
    submitting.value = false
  }
}

const submitOnly = async () => {
  if (!formData.patientName || !formData.patientId) {
    ElMessage.warning('请至少填写患者姓名和ID')
    return
  }
  submitting.value = true
  try {
    const payload = buildPayload()
    let resp
    if (deviceType.value === 'vision-chart') {
      const time = new Date()
      const timeStr = time.getFullYear() + '-' + String(time.getMonth() + 1).padStart(2, '0') + '-' + String(time.getDate()).padStart(2, '0') + '-' + String(time.getHours()).padStart(2, '0') + '-' + String(time.getMinutes()).padStart(2, '0') + '-' + String(time.getSeconds()).padStart(2, '0')
      const params = new URLSearchParams({
        visionType: payload.visionType, eyes: '2.0(5.3)', right: payload.right,
        left: payload.left, spaceType: payload.spaceType || '5m',
        resultTime: timeStr, userName: payload.patientName, userId: payload.patientId,
        deviceNumber: payload.deviceId || '', eyeCorrect: payload.eyeCorrect || ''
      })
      resp = await apiClient.get('receive/vision-chart?' + params.toString())
    } else if (deviceType.value === 'biometer') {
      resp = await apiClient.post('/receive/biometer', payload)
    } else {
      resp = await apiClient.post('/receive/vision-screening', payload)
    }
    if (resp.data.code === 0) {
      const recordId = resp.data.data.recordId
      lastRecordId.value = recordId
      resultRecordId.value = recordId
      resultPatientName.value = formData.patientName
      updateTickData()
      resultPrinted.value = false
      resultVisible.value = true
    }
  } catch (e: any) {
    ElMessage.error('提交失败: ' + (e?.message || e?.toString() || ''))
  } finally {
    submitting.value = false
  }
}

// 初始生成
randomGenerate()
</script>

<style scoped>
.test-tool { height: 100%; }
.card-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.eye-card { background: #fafbfc; }
.eye-card :deep(.el-card__header) { padding: 8px 12px; background: #f0f2f5; }
.empty-state { text-align: center; padding: 60px 0; color: #999; }
.empty-state p { margin: 8px 0; }

.thermal-printer { display: flex; justify-content: center; }
.printer-body { width: 320px; background: #e8e8e8; border-radius: 8px 8px 4px 4px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.printer-top { background: #404040; color: #ccc; padding: 6px 12px; display: flex; justify-content: space-between; font-size: 11px; font-family: monospace; }
.printer-brand { color: #6f6; font-weight: bold; }
.paper-slot { background: #2a2a2a; padding: 8px 0; display: flex; justify-content: center; }

.thermal-paper {
  width: 240px; background: #f7f3e8; border-radius: 2px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
  font-family: 'Courier New', 'SimHei', monospace;
  font-size: 12px; line-height: 1.5; color: #1a1a1a;
  max-height: 520px; overflow-y: auto;
}
.paper-content { padding: 14px 10px; }
.receipt-line { padding: 1px 0; white-space: pre-wrap; word-break: break-all; }
.spacer { margin-left: 48px; }
.spacer2 { margin-left: 60px; }
.receipt-center { text-align: center; }
.receipt-bold { font-weight: bold; }
.receipt-large { font-size: 14px; }
.receipt-dots { letter-spacing: 2px; color: #888; }
.receipt-cut { text-align: center; color: #999; font-size: 10px; letter-spacing: 3px; border-top: 1px dashed #ccc; padding-top: 8px; margin-top: 4px; }
.qrcode-img { width: 100px; height: 100px; image-rendering: pixelated; }
</style>
