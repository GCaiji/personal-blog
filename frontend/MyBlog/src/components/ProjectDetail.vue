<template>
  <div class="project-detail-container">
    <el-card class="project-card">
      <template #header>
        <div class="card-header">
          <span>{{ project.name }}</span>
        </div>
      </template>
      <div class="project-content">
        <img v-if="project.img" :src="project.img" alt="Project Image" class="project-image" />
        <p>{{ project.description }}</p>
        <p><strong>技术栈:</strong> {{ project.technologies && project.technologies.length > 0 ? project.technologies.join(', ') : '暂无' }}</p>
        <p><strong>开始日期:</strong> {{ project.start_date || '暂无' }}</p>
        <p><strong>结束日期:</strong> {{ project.end_date || '至今' }}</p>
        <p><strong>我的角色:</strong> {{ project.role || '暂无' }}</p>
        <p>
          <strong>演示链接:</strong>
          <template v-if="project.demo_url">
            <el-link :href="project.demo_url" target="_blank" type="primary">{{ project.demo_url }}</el-link>
          </template>
          <template v-else>
            <span>暂无</span>
          </template>
        </p>
        <p>
          <strong>项目链接:</strong>
          <template v-if="project.project_url">
            <el-link :href="project.project_url" target="_blank" type="primary">{{ project.project_url }}</el-link>
          </template>
          <template v-else>
            <span>暂无</span>
          </template>
        </p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const project = ref({})

onMounted(() => {
  const projectId = route.params.project_id
  if (projectId) {
    fetchProjectDetail(projectId)
  }
})

const fetchProjectDetail = async (projectId) => {
  try {
    const response = await axios.get(`/api/project/${projectId}`)
    project.value = response.data
  } catch (error) {
    console.error('获取项目详情失败:', error)
    ElMessage.error('获取项目详情失败，请稍后再试！')
  }
}
</script>

<style scoped>
.project-detail-container {
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 60px); /* Adjust based on your header/footer height */
}

.project-card {
  width: 100%;
  max-width: 900px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  border-radius: 12px;
  overflow: hidden;
}

.card-header {
  background-color: #409eff;
  color: white;
  font-size: 28px;
  font-weight: bold;
  text-align: center;
  padding: 20px 0;
  border-bottom: none;
}

.project-image {
  width: 100%;
  height: 400px; /* Fixed height for images */
  object-fit: cover; /* Cover the area, cropping if necessary */
  display: block;
  margin-bottom: 30px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.project-content {
  padding: 30px;
  font-size: 18px;
  line-height: 1.8;
  color: #444;
}

.project-content p {
  margin-bottom: 15px;
  display: flex;
  align-items: baseline;
}

.project-content strong {
  color: #333;
  flex-shrink: 0;
  margin-right: 10px;
  min-width: 90px; /* Align labels */
}

.el-link {
  font-size: 18px;
  vertical-align: baseline;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .project-card {
    width: 95%;
  }

  .card-header {
    font-size: 24px;
    padding: 15px 0;
  }

  .project-image {
    height: 250px;
    margin-bottom: 20px;
  }

  .project-content {
    padding: 20px;
    font-size: 16px;
  }

  .project-content p {
    flex-direction: column;
    align-items: flex-start;
  }

  .project-content strong {
    margin-bottom: 5px;
  }

  .el-link {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .project-detail-container {
    padding: 20px 10px;
  }

  .project-image {
    height: 180px;
  }

  .project-content {
    padding: 15px;
  }
}
</style>
