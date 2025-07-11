<template>
  <div class="post-list-container">
    <h1>文章列表</h1>
    <div v-if="loading" class="loading-indicator">
      <p>正在加载文章...</p>
    </div>
    <div v-else-if="posts.length === 0" class="no-posts">
      <p>暂无文章。</p>
    </div>
    <div v-else class="posts-grid">
      <!-- <p>文章数量: {{ posts.length }}</p> -->
      <div v-for="post in posts" :key="post.id" class="post-card" @click="goToPostDetail(post.id)">
        <h2>{{ post.title }}</h2>
        <div class="post-meta">
          <span><i class="fas fa-thumbs-up"></i> {{ post.like_count }}</span>
          <span><i class="fas fa-comments"></i> {{ post.comment_count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const posts = ref([]);
const loading = ref(true); // 新增 loading 状态
const router = useRouter();

const goToPostDetail = (postId) => {
  router.push({ name: 'post-detail', params: { post_id: postId } });
};

onMounted(async () => {
  try {
    const response = await axios.get('/api/posts');
    posts.value = response.data;
    console.log('获取到的文章数据:', posts.value);
  } catch (error) {
    console.error('获取文章列表失败:', error);
  } finally {
    loading.value = false; // 数据加载完成后设置 loading 为 false
  }
});
</script>

<style scoped>
.post-list-container {
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

.no-posts {
  text-align: center;
  color: #666;
  font-size: 1.2em;
  margin-top: 50px;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
}

.post-card {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.post-card h2 {
  color: #007bff;
  font-size: 1.8em;
  margin-top: 0;
  margin-bottom: 15px;
  word-break: break-word;
}

.post-meta {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  color: #777;
  font-size: 0.9em;
  margin-top: 15px;
}

.post-meta span {
  display: flex;
  align-items: center;
}

.post-meta i {
  margin-right: 5px;
  color: #007bff;
}

.loading-indicator {
  text-align: center;
  color: #007bff;
  font-size: 1.2em;
  margin-top: 50px;
}
</style>
