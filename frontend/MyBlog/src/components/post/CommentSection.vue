<template>
  <el-card class="comment-section">
    <h3>评论</h3>
    <el-empty v-if="comments.length === 0" description="暂无评论，快来发表第一条评论吧！"></el-empty>
    <div v-else class="comment-list">
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        :post-id="postId"
        @comment-added="fetchComments"
      />
    </div>

    <el-card class="comment-form">
      <h4>发表评论</h4>
      <el-input
        v-model="newCommentContent"
        :rows="4"
        type="textarea"
        placeholder="留下你的评论..."
      />
      <el-button type="primary" @click="submitComment">提交评论</el-button>
    </el-card>
  </el-card>
</template>

<script setup>
import { ref, onMounted, defineProps } from 'vue';
import CommentItem from '../post/CommentItem.vue';
import axios from 'axios';
import { ElCard, ElInput, ElButton, ElMessage, ElEmpty } from 'element-plus';

const props = defineProps({
  postId: {
    type: Number,
    required: true
  }
});

const comments = ref([]);
const newCommentContent = ref('');


const fetchComments = async () => {
  try {
    const response = await axios.get(`/api/comments/${props.postId}`);
    comments.value = response.data.comments;
  } catch (error) {
    console.error('获取评论失败:', error);
    comments.value = [];
  }
};

const submitComment = async () => {
  if (!newCommentContent.value.trim()) {
    ElMessage.warning('评论内容不能为空！');
    return;
  }
  try {
    // 假设后端有一个 /api/comments 接口用于提交评论
    // 并且需要 user_id, post_id, content, parent_id (可选)
    // 这里 user_id 暂时写死，实际应用中应从用户会话中获取
    const response = await axios.post('/api/comments', {
      user_id: 1, // 示例：实际应从登录用户会话中获取
      post_id: props.postId,
      content: newCommentContent.value,
      parent_id: null // For top-level comments
    });
    if (response.status === 201) {
      ElMessage.success('评论提交成功！');
      newCommentContent.value = '';
      fetchComments(); // 重新加载评论以显示新评论
    } else {
      ElMessage.error('评论提交失败！');
    }
  } catch (error) {
    console.error('提交评论失败:', error);
    ElMessage.error('提交评论失败，请稍后再试。');
  }
};



onMounted(() => {
  fetchComments();
});
</script>

<style scoped>
.comment-section {
  margin-top: 30px;
}

.comment-section h3 {
  color: #333;
  margin-bottom: 20px;
  font-size: 1.8em;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

.comment-list {
  margin-bottom: 30px;
}

.comment-form {
  margin-top: 20px;
}

.comment-form h4 {
  color: #007bff;
  margin-bottom: 15px;
  font-size: 1.5em;
}

.comment-form .el-textarea {
  margin-bottom: 15px;
}

.comment-form .el-button {
  width: 100%;
  transition: background-color 0.3s ease;
}

.comment-form button:hover {
  background-color: #0056b3;
}
</style>
