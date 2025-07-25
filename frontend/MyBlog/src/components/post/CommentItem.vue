<template>
  <el-card class="comment-item">
    <div class="comment-main-content">
      <p class="comment-meta">
        <strong>{{ comment.username || '匿名用户' }}</strong> 说：
      </p>
      <p class="comment-content">{{ comment.content }}</p>
      <el-button type="primary" size="small" @click="toggleReplyForm(comment.id)">回复</el-button>
      <el-button v-if="userRole === 'author'" type="danger" size="small" @click="deleteComment(comment.id)">删除</el-button>
    </div>

    <el-collapse-transition>
      <div v-if="showReplyForm" class="reply-form-container">
        <el-input
          v-model="replyContent"
          :rows="2"
          type="textarea"
          placeholder="回复内容..."
        />
        <div class="reply-form-actions">
          <el-button type="success" size="small" @click="submitReply(comment.id, comment.username)">提交回复</el-button>
          <el-button type="info" size="small" @click="cancelReply">取消</el-button>
        </div>
      </div>
    </el-collapse-transition>

    <div v-if="comment.replies && comment.replies.length">
      <el-button type="text" size="small" @click="toggleReplies">
        {{ showReplies ? '收起回复' : `展开回复 (${comment.replies.length})` }}
      </el-button>
      <transition name="fade">
        <div v-show="showReplies" class="comment-replies">
          <CommentItem
            v-for="reply in comment.replies"
            :key="reply.id"
            :comment="reply"
            :post-id="postId"
            @comment-added="$emit('comment-added')"
          />
        </div>
      </transition>
    </div>
  </el-card>
</template>

<script setup>
import { ref, defineProps, defineEmits, onMounted } from 'vue';
import axios from 'axios';
import { ElCard, ElButton, ElInput, ElMessage, ElCollapseTransition } from 'element-plus';

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  postId: {
    type: Number,
    required: true
  }
});

const emit = defineEmits(['comment-added']);

const showReplyForm = ref(false);
const replyContent = ref('');
const showReplies = ref(false);
const userRole = ref('guest');

const fetchUserRole = async () => {
  try {
    const response = await axios.get('/api/userinfo');
    userRole.value = response.data.role || 'guest';
  } catch (error) {
    console.error('获取用户角色失败:', error);
    userRole.value = 'guest';
  }
};

const toggleReplyForm = () => {
  showReplyForm.value = !showReplyForm.value;
  replyContent.value = '';
};

const toggleReplies = () => {
  showReplies.value = !showReplies.value;
};

const cancelReply = () => {
  showReplyForm.value = false;
  replyContent.value = '';
};

const submitReply = async (parentId, parentUsername) => {
  if (!replyContent.value.trim()) {
    ElMessage.warning('回复内容不能为空！');
    return;
  }

  try {
    const response = await axios.post('/api/comments', {
      user_id: 1,
      post_id: props.postId,
      content: `${replyContent.value}`,
      parent_id: parentId
    });

    if (response.status === 201) {
      ElMessage.success('回复提交成功！');
      replyContent.value = '';
      showReplyForm.value = false;
      emit('comment-added');
    } else {
      ElMessage.error('回复提交失败！');
    }
  } catch (error) {
    console.error('提交回复失败:', error);
    ElMessage.error('提交回复失败，请稍后再试。');
  }
};

const deleteComment = async (commentId) => {
  if (!confirm('确定要删除这条评论吗？')) {
    return;
  }
  try {
    await axios.delete(`/api/comments/${commentId}`);
    ElMessage.success('评论删除成功');
    emit('comment-added');
  } catch (error) {
    ElMessage.error('删除评论失败: ' + (error.response?.data?.error || error.message));
  }
};

onMounted(() => {
  fetchUserRole();
});

</script>

<style scoped>
.comment-item {
  margin-bottom: 15px;
}

.comment-main-content {
  margin-bottom: 10px;
}

.comment-meta {
  font-size: 0.9em;
  color: #555;
  margin-bottom: 8px;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.comment-meta strong {
  color: #007bff;
}

.comment-content {
  font-size: 1.1em;
  line-height: 1.6;
  color: #333;
  margin-bottom: 10px;
}

.reply-form-container {
  margin-top: 10px;
  padding: 10px;
  background-color: #f0f8ff;
  border: 1px solid #cceeff;
  border-radius: 5px;
}

.reply-form-actions {
  margin-top: 10px;
  text-align: right;
}

.comment-replies {
  margin-left: 20px; /* Indent replies */
  padding-left: 10px;
  border-left: 2px solid #eee;
  margin-top: 15px;
}

.comment-replies .comment-item {
  margin-top: 10px;
  margin-bottom: 0;
  background-color: #fdfdfd;
  box-shadow: none;
  border: 1px dashed #eee;
}
</style>
