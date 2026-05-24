<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="page-header-left">
        <h1 class="page-title">数据总览</h1>
        <p class="page-subtitle">实时监控视力检查数据与打印状态</p>
      </div>
      <div class="page-header-right">
        <el-button type="primary" @click="handlePrintTest">打印测试页</el-button>
        <el-button @click="store.fetchRecords()">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon blue">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-value">{{ todayCount }}</div>
        <div class="stat-label">今日检查数</div>
        <div class="stat-trend up">人</div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-value" style="color: var(--warning)">{{ pendingCount }}</div>
        <div class="stat-label">待打印数</div>
        <div class="stat-trend down" v-if="pendingCount > 0">需处理</div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-value" style="color: var(--success)">{{ printedCount }}</div>
        <div class="stat-label">已打印数</div>
        <div class="stat-trend up">份</div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-icon purple">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="stat-value" style="font-size: 1.25rem; color: var(--success)">已连接</div>
        <div class="stat-label">设备状态</div>
        <div class="stat-trend up">
          <span class="status-dot pulse" style="width:6px;height:6px;"></span> 在线
        </div>
      </el-card>
    </div>

    <!-- 最近记录 -->
    <el-card class="section-gap" shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>最近检查记录</span>
          <el-button size="small" type="primary" @click="handlePrintTest">打印测试页</el-button>
        </div>
      </template>

      <el-table :data="recentRecords" v-loading="store.loading" empty-text="暂无检查记录">
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
        <el-table-column prop="metadata.checkTime" label="检查时间" min-width="170" />
        <el-table-column prop="printed" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.printed ? 'success' : 'warning'" size="small" effect="light">
              {{ row.printed ? '已打印' : '待打印' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handlePrint(row)" :disabled="row.printed">
              {{ row.printed ? '已打' : '打印' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAppStore } from '@/stores'
import { ElMessage } from 'element-plus'
import { Document, Clock, CircleCheck, Connection, Refresh } from '@element-plus/icons-vue'
import type { CheckRecord } from '@/stores'

const store = useAppStore()

const todayCount = computed(() => store.records.length)
const pendingCount = computed(() => store.records.filter(r => !r.printed).length)
const printedCount = computed(() => store.records.filter(r => r.printed).length)

const recentRecords = computed(() => [...store.records].reverse().slice(0, 10))

const getDeviceTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    'vision-chart': '电子视力表',
    'biometer': '眼生物测量仪',
    'vision-screening': '视力筛查仪'
  }
  return typeMap[type] || type
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

const handlePrintTest = async () => {
  try {
    await store.printTestPage()
    ElMessage.success('测试页已发送')
  } catch {
    ElMessage.error('测试页发送失败')
  }
}

onMounted(() => {
  store.fetchRecords()
})
</script>

<style scoped>
.dashboard {
  /* page-container handles max-width and padding */
}
</style>
