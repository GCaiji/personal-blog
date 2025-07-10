<template>
  <div class="common-layout">
    <el-container style="height: 100vh; display: flex; flex-direction: column">
      <el-header><Header /></el-header>
      <el-container style="flex: 1; overflow: hidden">
        <el-aside width="200px"><Sidebar /></el-aside>
        <el-main style="padding: 20px; height: 100%">
          <!-- 添加 key 强制重新渲染视图 -->
          <router-view :key="$route.fullPath" />
        </el-main>
      </el-container>
      <el-footer>&copy; 2024 我的博客</el-footer>
    </el-container>
  </div>
</template>

<script setup>
import Header from '../components/Header.vue'
import Sidebar from '../components/Sidebar.vue'
</script>

<style scoped>
.common-layout {
  min-height: 100vh;
  font-family: Arial, sans-serif;
}

.el-header {
  background-color: #007bff;
  color: white;
  padding: 0 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.el-aside {
  background-color: #f4f4f4;
  padding: 20px;
  box-shadow: 2px 0 4px rgba(0, 0, 0, 0.1);
}

.el-main {
  padding: 40px;
  background-color: #f9f9f9;
}

.home-content {
  text-align: center;
}

.home-content h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 20px;
}

.home-content p {
  font-size: 18px;
  color: #555;
  line-height: 1.6;
}

.el-footer {
  background-color: #343a40;
  color: white;
  text-align: center;
  padding: 15px;
  font-size: 14px;
}
</style>
