<template>
  <el-card class="comment-section">
    <h3>评论</h3>
    <el-empty v-if="comments.length === 0"
    description="暂无评论，快来发表第一条评论吧！"></el-empty>
    <div v-else class="comment-list">
      <CommentItem
        v-for="comment in comments"
        :key="comment.id"
        :comment="comment"
        :post-id="postId"
        @comment-added="handleCommentAdded"
      />
    </div>

    <el-pagination
      v-if="totalPages > 1"
      background
      layout="prev, pager, next, ->, total"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="totalPages * pageSize"
      @current-change="handlePageChange"
      style="text-align: center; margin-bottom: 20px;"
    />

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
const currentPage = ref(1);
const pageSize = ref(5);
const totalPages = ref(1);

const fetchComments = async (page = 1) => {
  try {
    const response = await axios.get(`/api/comments/${props.postId}`, {
      params: {
        page: page,
        page_size: pageSize.value
      }
    });
    comments.value = response.data.data;
    currentPage.value = response.data.pagination.current_page;
    pageSize.value = response.data.pagination.page_size;
    totalPages.value = response.data.pagination.total_pages;
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
    const response = await axios.post('/api/comments', {
      user_id: 1,
      post_id: props.postId,
      content: newCommentContent.value,
      parent_id: null
    });
    if (response.status === 201) {
      ElMessage.success('评论提交成功！');
      newCommentContent.value = '';
      fetchComments(currentPage.value); // 添加评论后重新加载当前页
    } else {
      ElMessage.error('评论提交失败！');
    }
  } catch (error) {
    console.error('提交评论失败:', error);
    ElMessage.error('提交评论失败，请稍后再试。');
  }
};

const handlePageChange = (page) => {
  fetchComments(page);
};

const handleCommentAdded = () => {
  // 删除评论后重新加载当前页，且检查总页数变化
  fetchComments(currentPage.value);
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
