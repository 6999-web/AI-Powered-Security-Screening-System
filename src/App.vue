<template>
  <div id="app">
    <el-container class="layout-container">
      <el-aside width="200px" class="sidebar">
        <div class="logo">
          <el-icon :size="30"><Camera /></el-icon>
          <span>智能安检系统</span>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          class="menu"
        >
          <el-menu-item index="/checkin">
            <el-icon><Upload /></el-icon>
            <span>入场安检</span>
          </el-menu-item>
          <el-menu-item index="/checkout">
            <el-icon><Download /></el-icon>
            <span>离场安检</span>
          </el-menu-item>
          <el-menu-item index="/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据看板</span>
          </el-menu-item>
          <el-menu-item index="/anomalies">
            <el-icon><Warning /></el-icon>
            <span>异常记录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="header">
          <div class="header-title">{{ pageTitle }}</div>
          <div class="header-info">
            <el-icon><User /></el-icon>
            <span>管理员</span>
          </div>
        </el-header>

        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const pageTitle = computed(() => {
  const titles = {
    '/checkin': '入场安检',
    '/checkout': '离场安检',
    '/dashboard': '数据看板',
    '/anomalies': '异常记录'
  }
  return titles[route.path] || '智能安检系统'
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  height: 100vh;
  overflow: hidden;
}

.layout-container {
  height: 100vh;
}

.sidebar {
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.menu {
  border: none;
  background: transparent;
}

.el-menu-item {
  color: rgba(255, 255, 255, 0.7) !important;
}

.el-menu-item:hover,
.el-menu-item.is-active {
  background: rgba(64, 158, 255, 0.2) !important;
  color: #fff !important;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.main-content {
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
