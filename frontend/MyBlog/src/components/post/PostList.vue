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
      <div v-for="post in posts" :key="post.id" @click="goToPostDetail(post.id)" class="post-card">
        <h2 class="post-title" :title="post.title">{{ post.title }}</h2>
        <p class="post-excerpt">{{ post.content.length > 100 ? post.content.slice(0, 100) + '...' : post.content }}</p>
        <div class="post-meta">
          <span><i class="fas fa-thumbs-up"></i> {{ post.like_count }}</span>
          <span><i class="fas fa-comments"></i> {{ post.comment_count }}</span>
          <button v-if="userRole === 'author'" @click.stop="deletePost(post.id)" class="delete-button">删除</button>
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
const userRole = ref('guest');
const router = useRouter();

const goToPostDetail = (postId) => {
  router.push({ name: 'post-detail', params: { post_id: postId } });
};

const fetchUserRole = async () => {
  try {
    const response = await axios.get('/api/userinfo');
    userRole.value = response.data.role || 'guest';
  } catch (error) {
    console.error('获取用户角色失败:', error);
    userRole.value = 'guest';
  }
};

const fetchPosts = async () => {
  loading.value = true;
  try {
    const response = await axios.get('/api/posts');
    posts.value = response.data;
  } catch (error) {
    console.error('获取文章列表失败:', error);
  } finally {
    loading.value = false;
  }
};

const deletePost = async (postId) => {
  if (!confirm('确定要删除这篇文章吗？')) {
    return;
  }
  try {
    await axios.delete(`/api/post/${postId}`);
    alert('文章删除成功');
    fetchPosts();
  } catch (error) {
    alert('删除文章失败: ' + (error.response?.data?.error || error.message));
  }
};

onMounted(() => {
  fetchUserRole();
  fetchPosts();
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
  display: block;
}

.post-card {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  width: 100%;
  overflow: hidden;
}

.post-title {
  color: #007bff;
  font-size: 1.8em;
  font-weight: bold;
  margin: 0 0 10px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.post-excerpt {
  font-size: 1em;
  color: #555;
  margin: 0 0 15px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  display: -moz-box; /* 确保跨浏览器兼容 */
  -webkit-line-clamp: 3;
  line-clamp: 3; /* 新增标准属性 */
  -webkit-box-orient: vertical;
  -moz-box-orient: vertical; /* 兼容旧版 Firefox */
  box-orient: vertical; /* 标准属性 */
}

.post-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  z-index: 100;
}

.post-meta {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  color: #777;
  font-size: 0.9em;
  margin-top: auto;
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
.delete-button {
  background-color: #ff4d4f;
  border: none;
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
  margin-left: 0;
  align-self: flex-start;
  transition: background-color 0.3s ease;
}

.delete-button:hover {
  background-color: #d9363e;
}

.post-card:hover h2 {
  position: static;
  white-space: nowrap;
  width: auto;
  background: none;
  box-shadow: none;
  padding: 0;
}

</style>


