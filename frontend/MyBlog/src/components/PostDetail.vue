<template>
  <div class="post-detail-container">
    <el-card class="post-card">
      <template #header>
        <div class="card-header">
          <span>{{ post.title }}</span>
        </div>
      </template>
      <div class="post-content">
        <p>{{ post.content }}</p>
      </div>
      <div class="post-meta">
        <el-tooltip :content="isLiked ? '取消点赞' : '点赞'" placement="top">
          <el-button
            :type="isLiked ? 'primary' : 'default'"

            circle
            @click="handleLike"
            class="like-button"
          />
        </el-tooltip>
        <span class="like-count">点赞数: {{ post.like_count }}</span>
        <span class="comment-count">评论数: {{ post.comment_count }}</span>
      </div>
      <CommentSection :postId="post.id" v-if="post.id" />
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import { ElMessage, ElButton } from 'element-plus';
import CommentSection from './CommentSection.vue';
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue';


// 添加类型定义
interface Post {
  id: number;
  title: string;
  content: string;
  like_count: number;
  comment_count: number;
}

export default defineComponent({
  name: 'PostDetail',
  components: {
    CommentSection,
    ElButton
  },
  setup() {
    const route = useRoute();
    // 添加泛型类型声明
    const post = ref<Post>({
      id: 0,
      title: '',
      content: '',
      like_count: 0,
      comment_count: 0
    });
    const isLiked = ref(false);

    onMounted(() => {
      // 处理路由参数类型问题
      const postId = route.params.post_id;
      const id = Array.isArray(postId) ? postId[0] : postId;

      if (id) {
        fetchPostDetail(id);
      }
    });

    const fetchPostDetail = async (postId: string) => {
      try {
        const response = await axios.get(`/api/post/${postId}`);
        post.value = response.data;
        isLiked.value = response.data.is_liked; // 假设后端返回is_liked字段
      } catch (error) {
        console.error('获取文章详情失败:', error);
        ElMessage.error('获取文章详情失败，请稍后再试！');
      }
    };

    const handleLike = async () => {
      try {
        const response = await axios.post(`/api/post/${post.value.id}/like`);
        if (response.data.success) {
          post.value.like_count = response.data.like_count;
          isLiked.value = response.data.is_liked; // 更新点赞状态
          ElMessage.success(response.data.message || (response.data.is_liked ? '点赞成功！' : '已取消点赞！'));
        } else {
          ElMessage.warning(response.data.message);
        }
      } catch (error) {
        console.error('点赞操作失败:', error);
        ElMessage.error('操作失败，请稍后再试！');
      }
    };

    return {
      post,
      handleLike,
      ArrowUp,
      ArrowDown,
      isLiked,
    };
  }
});
</script>

<style scoped>
/* 保持原有样式不变 */
.post-detail-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 60px);
}

.post-card {
  width: 80%;
  max-width: 900px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 10px;
}

.card-header {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.post-content {
  font-size: 16px;
  line-height: 1.8;
  color: #555;
  margin-bottom: 20px;
  white-space: pre-wrap;
}

.post-meta {
  display: flex;
  justify-content: flex-end;
  font-size: 14px;
  color: #999;
  border-top: 1px solid #eee;
  padding-top: 10px;
}

.post-meta span {
  margin-left: 15px;
}
.like-button {
  margin-right: 10px;
  transition: transform 0.3s, background-color 0.3s;
}

.like-button:hover {
  transform: scale(1.1);
}

/* 调整元数据显示布局 */
.post-meta {
  display: flex;
  align-items: center; /* 垂直居中 */
  justify-content: flex-end;
  gap: 12px; /* 增加间距 */

}
</style>
