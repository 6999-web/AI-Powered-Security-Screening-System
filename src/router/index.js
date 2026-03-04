import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/checkin'
  },
  {
    path: '/checkin',
    name: 'CheckIn',
    component: () => import('@/views/CheckIn.vue')
  },
  {
    path: '/checkout',
    name: 'CheckOut',
    component: () => import('@/views/CheckOut.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/anomalies',
    name: 'Anomalies',
    component: () => import('@/views/Anomalies.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
