<template>
  <div class="app-center">
    <h3>应用中心</h3>
    <div class="app-grid">
      <div v-for="app in apps" :key="app.id" class="app-item">
        <div class="app-icon">
          <i :class="app.icon"></i>
        </div>
        <span class="app-name">{{ app.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const apps = [
  { id: 1, name: '相册', icon: 'icon-album' },
  { id: 2, name: '日志', icon: 'icon-blog' },
  { id: 3, name: '留言板', icon: 'icon-message' },
  { id: 4, name: '音乐', icon: 'icon-music' },
  { id: 5, name: '游戏', icon: 'icon-game' },
  { id: 6, name: '更多', icon: 'icon-more' }
];
</script>

<style scoped>
.app-center {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.app-center h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
}

.app-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.app-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.app-icon {
  width: 40px;
  height: 40px;
  background-color: #409eff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 5px;
  color: white;
}

.app-name {
  font-size: 12px;
  color: #666;
}
</style>