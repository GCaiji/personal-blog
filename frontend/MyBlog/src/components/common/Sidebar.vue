<template>
  <div class="sidebar-container">
    <el-menu
      :default-active="activeMenu"
      class="el-menu-vertical-demo"
      router
      :unique-opened="true"
    >
      <!-- 修正路由路径 -->
      <el-menu-item index="/home/about">
        <el-icon><icon-menu /></el-icon>
        <span>个人介绍</span>
      </el-menu-item>
      <el-menu-item index="/home/postlist">
        <el-icon><document /></el-icon>
        <span>个人文章</span>
      </el-menu-item>
      <el-menu-item index="/home/projectlist">
        <el-icon><setting /></el-icon>
        <span>个人项目</span>
      </el-menu-item>
      <el-menu-item index="/home/monetlist">
        <el-icon><icon-menu /></el-icon>
        <span>个人动态</span>
      </el-menu-item>
      <el-menu-item index="/home/ai-dialogue">
        <el-icon><icon-menu /></el-icon>
        <span>AI对话</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup>
import { Document, Menu as IconMenu, Setting } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const activeMenu = computed(() => {
  // 确保匹配完整路径
  return route.path.startsWith('/home/') ? route.path : '/home/about'
})
</script>

<style scoped>
.sidebar-container {
  width: 100%;
  height: 100%;
  overflow: auto;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 100%;
  min-height: 100%;
}
</style>
