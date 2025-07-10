<template>
  <div class="project-list-container">
      <div class="project-list-container">
        <h1>个人项目</h1>
        <div v-if="projects.length === 0" class="no-projects">
          <p>暂无项目。</p>
        </div>
        <div v-else class="projects-grid">
          <div v-for="project in projects" :key="project.id" class="project-card" @click="goToProjectDetail(project.id)">
            <img :src="project.img || '/src/assets/Images/demo1.jpeg'" alt="Project Image" class="project-image" />
            <div class="project-info">
              <h2 class="project-name">{{ project.name }}</h2>
              <p class="project-description">{{ project.description }}</p>
              <div class="project-meta">
                <span class="meta-tag">
                  <span>{{ formatDate(project.start_date) }}</span>
                  <span>——</span>
                  <span v-if="project.end_date">{{ formatDate(project.end_date) }}</span>
                  <span v-else>至今</span>
                </span>
                <span v-if="project.role" class="meta-tag">角色: {{ project.role }}</span>
                <span v-if="project.technologies && project.technologies.length > 0" class="meta-tag">技术栈: {{ project.technologies.join(', ') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const projects = ref([]);
const router = useRouter();

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

onMounted(async () => {
  try {
    const response = await axios.get('http://127.0.0.1:5000/api/projects');
    projects.value = response.data;
    console.log('获取到的项目数据:', projects.value);
  } catch (error) {
    console.error('获取项目列表失败:', error);
  }
});

const goToProjectDetail = (projectId) => {
  router.push({ name: 'project-detail', params: { project_id: projectId } });
};
</script>

<style scoped>
.project-list-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Arial', sans-serif;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 2.5em;
}

.no-projects {
  text-align: center;
  color: #666;
  font-size: 1.2em;
  margin-top: 50px;
}

.projects-grid {
  display: flex;
  flex-direction: column;
  gap: 20px; /* Adjust as needed for spacing between projects */
}

.project-card {
  display: flex;
  flex-direction: row;
  align-items: flex-start; /* Align items to the top */
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  width: 100%; /* Ensure each project card takes full width */
  cursor: pointer;
}

.project-info {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.project-name {
  color: #3498db; /* 更醒目的蓝色 */
  font-size: 28px; /* 更大的字体 */
  font-weight: bold;
  margin-bottom: 10px;
}

.project-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 10px;
}

.project-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px; /* 标签之间的间距 */
  margin-top: 10px;
}

.meta-tag {
  background-color: #ecf5ff; /* 浅蓝色背景 */
  color: #409eff; /* 蓝色字体 */
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 13px;
  white-space: nowrap; /* 防止标签内容换行 */
}

.project-image {
  width: 200px; /* 固定宽度 */
  height: 150px; /* 固定高度 */
  margin-right: 20px;
  border-radius: 4px;
  object-fit: cover; /* 确保图片填充容器并保持比例 */
}
</style>
