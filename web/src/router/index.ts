import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/devices',
    name: 'Devices',
    component: () => import('@/views/Devices.vue')
  },
  {
    path: '/print-queue',
    name: 'PrintQueue',
    component: () => import('@/views/PrintQueue.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue')
  },
  {
    path: '/test-tool',
    name: 'TestTool',
    component: () => import('@/views/TestTool.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router