<template>
  <div class="app-shell">
    <!-- 顶部导航栏 -->
    <header class="topbar">
      <div class="topbar-left">
        <router-link to="/" class="logo-link">
          <span class="logo-icon">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <circle cx="14" cy="14" r="12" stroke="currentColor" stroke-width="2" opacity="0.3"/>
              <circle cx="14" cy="14" r="6" fill="currentColor"/>
              <circle cx="14" cy="14" r="10" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.6"/>
            </svg>
          </span>
          <span class="logo-text">VisionHub</span>
        </router-link>
      </div>

      <div class="topbar-center">
        <nav class="pill-nav">
          <router-link to="/" class="pill-item" exact-active-class="pill-active">
            <el-icon><Monitor /></el-icon>
            <span>总览</span>
          </router-link>
          <router-link to="/devices" class="pill-item" active-class="pill-active">
            <el-icon><Connection /></el-icon>
            <span>设备</span>
          </router-link>
          <router-link to="/print-queue" class="pill-item" active-class="pill-active">
            <el-icon><Printer /></el-icon>
            <span>队列</span>
          </router-link>
          <router-link to="/history" class="pill-item" active-class="pill-active">
            <el-icon><Document /></el-icon>
            <span>历史</span>
          </router-link>
          <router-link to="/settings" class="pill-item" active-class="pill-active">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </router-link>
          <router-link to="/test-tool" class="pill-item" active-class="pill-active">
            <el-icon><Tools /></el-icon>
            <span>测试</span>
          </router-link>
        </nav>
      </div>

      <div class="topbar-right">
        <span class="status-indicator">
          <span class="status-dot pulse"></span>
          系统运行中
        </span>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-area">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Monitor, Connection, Printer, Document, Setting, Tools } from '@element-plus/icons-vue'
import axios from 'axios'

const visionChartKeys = ['visionType', 'eyes', 'right', 'left', 'f', 'resultTime', 'userName', 'userId', 'userld', 'deviceNumber']

onMounted(async () => {
  const search = new URLSearchParams(window.location.search)
  if (!visionChartKeys.some(key => search.has(key))) return

  try {
    const res = await axios.get('/api/receive/vision-chart', { params: Object.fromEntries(search.entries()) })
    if (res.data.code === 0) {
      ElMessage.success('电子视力表数据已接收')
    }
  } catch (e) {
    ElMessage.error('电子视力表数据接收失败')
  }
})
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
}

/* ===== 顶部导航栏 ===== */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--topbar-height);
  padding: 0 var(--space-6);
  background: var(--surface);
  border-bottom: 1px solid var(--gray-200);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}

.topbar-left,
.topbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex: 0 0 auto;
  min-width: 180px;
}

.topbar-right {
  justify-content: flex-end;
}

.topbar-center {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

/* Logo */
.logo-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  text-decoration: none;
  color: var(--primary);
}

.logo-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.logo-text {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, var(--primary) 0%, var(--purple) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 药丸导航 */
.pill-nav {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  background: var(--gray-50);
  padding: var(--space-1);
  border-radius: var(--radius-lg);
}

.pill-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  color: var(--gray-600);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all var(--duration-fast) var(--ease-out);
  position: relative;
}

.pill-item:hover {
  color: var(--gray-800);
  background: var(--gray-100);
}

.pill-active {
  color: var(--primary) !important;
  background: var(--surface) !important;
  box-shadow: var(--shadow-xs);
}

/* 状态指示器 */
.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 0.85rem;
  color: var(--gray-600);
  white-space: nowrap;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success);
  display: inline-block;
}

.status-dot.pulse {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* ===== 主内容区 ===== */
.main-area {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: var(--space-6);
}
</style>
