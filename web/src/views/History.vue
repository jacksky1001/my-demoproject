<template>
  <div class="history">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">历史记录</h1>
        <p class="page-subtitle">查看和管理所有视力检查记录</p>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon blue">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-value">{{ filteredRecords.length }}</div>
        <div class="stat-label">总记录数</div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-value" style="color: var(--success)">{{ printedCount }}</div>
        <div class="stat-label">已打印</div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-value" style="color: var(--warning)">{{ unprintedCount }}</div>
        <div class="stat-label">未打印</div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon purple">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-value">{{ printRate }}%</div>
        <div class="stat-label">打印率</div>
      </el-card>
    </div>

    <!-- 筛选栏 + 表格 -->
    <el-card class="section-gap" shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
          <span>检查记录</span>
          <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              size="small"
              value-format="YYYY-MM-DD"
            />
            <el-select
              v-model="deviceTypeFilter"
              placeholder="设备类型"
              clearable
              size="small"
              style="width:150px"
            >
              <el-option label="全部" value="" />
              <el-option label="电子视力表" value="vision-chart" />
              <el-option label="眼生物测量仪" value="biometer" />
              <el-option label="视力筛查仪" value="vision-screening" />
            </el-select>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索姓名或ID"
              size="small"
              style="width:180px"
              clearable
              @keyup.enter="search"
            />
            <el-button type="primary" size="small" @click="search">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button size="small" @click="resetFilters">重置</el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="paginatedRecords"
        v-loading="loading"
        empty-text="暂无匹配记录"
      >
        <el-table-column prop="id" label="记录ID" width="220">
          <template #default="{ row }">
            <code style="font-family:var(--font-mono);font-size:0.8rem;color:var(--gray-600);">{{ row.id }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="patientInfo.patientName" label="姓名" width="100" />
        <el-table-column prop="patientInfo.patientId" label="患者ID" width="120">
          <template #default="{ row }">
            <code style="font-family:var(--font-mono);font-size:0.8rem;">{{ row.patientInfo.patientId }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="metadata.deviceType" label="设备类型" width="130">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ getDeviceTypeName(row.metadata.deviceType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="metadata.checkTime" label="检查时间" width="170" />
        <el-table-column prop="printed" label="打印状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.printed ? 'success' : 'warning'" size="small" effect="light">
              <span style="display:flex;align-items:center;gap:4px;">
                <span :style="{width:'6px',height:'6px',borderRadius:'50%',background:row.printed?'var(--success)':'var(--warning)'}"></span>
                {{ row.printed ? '已打印' : '待打印' }}
              </span>
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="printTime" label="打印时间" width="170">
          <template #default="{ row }">
            {{ row.printTime ? formatTime(row.printTime) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openPreview(row)">
              <el-icon><View /></el-icon>
              预览
            </el-button>
            <el-button size="small" type="success" @click="handlePrint(row)">
              {{ row.printed ? '补打' : '打印' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="filteredRecords.length"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        size="small"
      />
    </el-card>

    <el-dialog
      v-model="previewVisible"
      title="打印预览"
      width="480px"
      :close-on-click-modal="false"
    >
      <div class="print-preview" v-if="previewRecord">
        <div class="preview-paper">
          <div class="preview-header-line">
            <span>━━━━━━━━━━━━━━━━</span>
          </div>
          <h3 class="preview-title">视力检查报告</h3>
          <div class="preview-divider">────────────────</div>
          <div class="preview-field">
            <span class="preview-label">姓名</span>
            <span class="preview-value">{{ previewRecord.patientInfo.patientName }}</span>
          </div>
          <div class="preview-field">
            <span class="preview-label">ID</span>
            <span class="preview-value">{{ previewRecord.patientInfo.patientId }}</span>
          </div>
          <div class="preview-field">
            <span class="preview-label">时间</span>
            <span class="preview-value">{{ formatTime(previewRecord.metadata.checkTime) }}</span>
          </div>
          <div class="preview-field">
            <span class="preview-label">设备</span>
            <span class="preview-value">{{ getPreviewDeviceName(previewRecord) }}</span>
          </div>
          <div class="preview-divider">────────────────</div>
          <div v-if="previewRecord.visionChartData" class="preview-vision">
            <div class="preview-table-header">
              <span></span>
              <span>右眼</span>
              <span>左眼</span>
            </div>
            <div class="preview-table-row">
              <span>裸眼</span>
              <span class="preview-vision-val">{{ previewRecord.visionChartData.od?.vision || '-' }}</span>
              <span class="preview-vision-val">{{ previewRecord.visionChartData.os?.vision || '-' }}</span>
            </div>
            <div v-if="hasAnyEyeValue(previewRecord, 'logVision')" class="preview-table-row">
              <span>对数</span>
              <span>{{ previewRecord.visionChartData.od?.logVision || '-' }}</span>
              <span>{{ previewRecord.visionChartData.os?.logVision || '-' }}</span>
            </div>
            <div v-if="hasAnyEyeValue(previewRecord, 'ref')" class="preview-table-row">
              <span>参考</span>
              <span>{{ previewRecord.visionChartData.od?.ref || '-' }}</span>
              <span>{{ previewRecord.visionChartData.os?.ref || '-' }}</span>
            </div>
            <div v-if="hasAnyEyeValue(previewRecord, 'speed')" class="preview-table-row">
              <span>用时</span>
              <span>{{ previewRecord.visionChartData.od?.speed || '-' }}</span>
              <span>{{ previewRecord.visionChartData.os?.speed || '-' }}</span>
            </div>
            <div v-if="hasAnyEyeValue(previewRecord, 'lowVision')" class="preview-table-row">
              <span>低视</span>
              <span>{{ previewRecord.visionChartData.od?.lowVision || '-' }}</span>
              <span>{{ previewRecord.visionChartData.os?.lowVision || '-' }}</span>
            </div>
            <div v-if="previewRecord.visionChartData.eyeCorrect" class="preview-field compact">
              <span class="preview-label">矫正</span>
              <span class="preview-value">{{ previewRecord.visionChartData.eyeCorrect }}</span>
            </div>
            <div v-if="previewRecord.visionChartData.visionType" class="preview-field compact">
              <span class="preview-label">视标</span>
              <span class="preview-value">{{ previewRecord.visionChartData.visionType }}</span>
            </div>
            <div v-if="previewRecord.visionChartData.spaceType" class="preview-field compact">
              <span class="preview-label">距离</span>
              <span class="preview-value">{{ previewRecord.visionChartData.spaceType }}</span>
            </div>
          </div>
          <div v-else class="preview-no-data">— 无视力数据 —</div>
          <div class="preview-divider">────────────────</div>
          <div class="preview-qr">
            <div class="qr-placeholder">
              <el-icon><Picture /></el-icon>
              <span>二维码</span>
            </div>
            <p class="qr-hint">扫码查看完整数据</p>
          </div>
          <div class="preview-header-line">
            <span>━━━━━━━━━━━━━━━━</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="printPreviewed">
          打印
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAppStore, type CheckRecord } from '@/stores'
import { ElMessage } from 'element-plus'
import { Search, Document, CircleCheck, Clock, TrendCharts, View, Picture } from '@element-plus/icons-vue'

const store = useAppStore()

const loading = ref(false)
const previewVisible = ref(false)
const previewRecord = ref<CheckRecord | null>(null)
const dateRange = ref<[string, string] | null>(null)
const searchKeyword = ref('')
const deviceTypeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const filteredRecords = computed(() => {
  let result = [...store.records].reverse()

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(r =>
      r.patientInfo.patientName.toLowerCase().includes(keyword) ||
      r.patientInfo.patientId.toLowerCase().includes(keyword)
    )
  }

  if (deviceTypeFilter.value) {
    result = result.filter(r => r.metadata.deviceType === deviceTypeFilter.value)
  }

  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const [startDate, endDate] = dateRange.value
    result = result.filter(r => {
      const checkDate = r.metadata.checkTime.split('T')[0]
      return checkDate >= startDate && checkDate <= endDate
    })
  }

  return result
})

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

const printedCount = computed(() => filteredRecords.value.filter(r => r.printed).length)
const unprintedCount = computed(() => filteredRecords.value.filter(r => !r.printed).length)
const printRate = computed(() => {
  const total = filteredRecords.value.length
  return total === 0 ? 0 : Math.round((printedCount.value / total) * 100)
})

onMounted(() => {
  store.fetchRecords()
})

const getDeviceTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    'vision-chart': '电子视力表',
    'biometer': '眼生物测量仪',
    'vision-screening': '视力筛查仪'
  }
  return typeMap[type] || type
}

const formatTime = (timeStr: string) => {
  return new Date(timeStr).toLocaleString('zh-CN')
}

const getPreviewDeviceName = (record: CheckRecord) => {
  return record.visionChartData?.deviceName || record.metadata.deviceId || getDeviceTypeName(record.metadata.deviceType)
}

const hasAnyEyeValue = (record: CheckRecord, key: 'logVision' | 'ref' | 'speed' | 'lowVision') => {
  const data = record.visionChartData
  return Boolean(data?.od?.[key] || data?.os?.[key])
}

const openPreview = (record: CheckRecord) => {
  previewRecord.value = record
  previewVisible.value = true
}

const search = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  searchKeyword.value = ''
  deviceTypeFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
}

const handlePrint = async (record: CheckRecord) => {
  try {
    await store.printRecord(record.id)
    ElMessage.success('打印任务已发送')
    await store.fetchRecords()
  } catch {
    ElMessage.error('打印失败')
  }
}

const printPreviewed = async () => {
  if (previewRecord.value) {
    await handlePrint(previewRecord.value)
    previewVisible.value = false
  }
}
</script>

<style scoped>
.history {
  /* styles via global.css */
}

.print-preview {
  display: flex;
  justify-content: center;
}

.preview-paper {
  width: 100%;
  max-width: 320px;
  background: #fdfdf8;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  padding: var(--space-5) var(--space-4);
  font-family: var(--font-sans);
  font-size: 0.85rem;
  color: var(--gray-800);
  line-height: 1.6;
}

.preview-header-line {
  text-align: center;
  color: var(--gray-400);
  font-size: 0.7rem;
  margin-bottom: var(--space-3);
}

.preview-title {
  text-align: center;
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 var(--space-3);
  letter-spacing: 0.05em;
}

.preview-divider {
  text-align: center;
  color: var(--gray-300);
  font-size: 0.65rem;
  margin: var(--space-3) 0;
}

.preview-field {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-1) 0;
}

.preview-field.compact {
  padding: 2px 0;
}

.preview-label {
  color: var(--gray-600);
  font-weight: 500;
}

.preview-value {
  color: var(--gray-900);
  font-weight: 500;
}

.preview-table-header,
.preview-table-row {
  display: grid;
  grid-template-columns: 64px 1fr 1fr;
  column-gap: var(--space-2);
  align-items: center;
  padding: 2px 0;
}

.preview-table-header {
  color: var(--gray-600);
  font-weight: 700;
  text-align: center;
}

.preview-table-row span:first-child {
  color: var(--gray-600);
  font-weight: 500;
}

.preview-table-row span:not(:first-child) {
  text-align: center;
  font-family: var(--font-mono);
}

.preview-vision-val {
  font-size: 1rem;
  color: var(--primary);
  font-weight: 700;
}

.preview-no-data {
  text-align: center;
  color: var(--gray-400);
  padding: var(--space-4) 0;
}

.preview-qr {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.qr-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  border: 2px dashed var(--gray-300);
  border-radius: var(--radius-md);
  color: var(--gray-400);
  font-size: 0.75rem;
  gap: var(--space-1);
}

.qr-placeholder .el-icon {
  font-size: 28px;
}

.qr-hint {
  font-size: 0.75rem;
  color: var(--gray-500);
  margin: 0;
}
</style>
