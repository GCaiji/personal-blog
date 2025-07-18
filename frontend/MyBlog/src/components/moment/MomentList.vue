<template>
  <div class="moment-page-wrapper">
    <aside class="left-sidebar">
      <AppCenter />
    </aside>

    <div class="moment-page">
      <header class="page-header">
        <h1>我的动态</h1>
      </header>

      <MomentPostBox @post-moment="handlePostMoment" />

      <section class="moment-list">
        <div v-for="moment in moments" :key="moment.id" class="moment-item">
          <div class="moment-header">
            <div class="user-avatar">
            <img src="@/assets/images/Logos/DefaultLogo.svg" alt="User Avatar" class="avatar-img" />
          </div>
          <div class="user-info">
            <span class="username">{{ moment.user.username }}</span>
            <span class="timestamp">{{ new Date(moment.publish_time).toLocaleString('zh-CN', { hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }) }}</span>
          </div>
          </div>
          <div class="moment-content">
            <p>{{ moment.content }}</p>
            <div v-if="moment.images && moment.images.length" class="moment-images">
              <img v-for="image in moment.images" :src="`http://localhost:5000/static_assets/${image.image_url.replace(/\\/g, '/').replace('src/assets/', '')}`" :key="image.id" class="moment-image" @click="showImageModal(`http://localhost:5000/static_assets/${image.image_url.replace(/\\/g, '/').replace('src/assets/', '')}`)" />
            </div>
          </div>
          <div class="moment-actions">
            <span class="action-item" @click="toggleLike(moment)"><i class="icon-like"></i> 赞 ({{ moment.likes }})</span>
            <span class="action-item" @click="toggleCommentBox(moment)"><i class="icon-comment"></i> 评论 ({{ moment.comments.length }})</span>
            <span class="action-item"><i class="icon-share"></i> 转发</span>
          </div>
          <div class="moment-comments">
            <div v-for="comment in moment.comments" :key="comment.id" class="comment-item">
              <span class="comment-user">{{ (comment.user && comment.user.username) ? comment.user.username : '未知用户' }}:</span>
              <span class="comment-text">{{ comment.content }}</span>
            </div>
          </div>
          <div v-if="showCommentBox === moment.id" class="comment-input-box">
            <input type="text" v-model="commentContent" @keyup.enter="postComment(moment)" placeholder="发表评论..." />
            <button @click="postComment(moment)">评论</button>
          </div>
        </div>
      </section>
    </div>

    <aside class="right-sidebar">
      <SignInCard />
    </aside>
  </div>
  <div v-if="showModal" class="image-modal" @click.self="closeModal">
    <img :src="currentImage" alt="大图" class="modal-content" />
    <span class="close-button" @click="closeModal">&times;</span>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import AppCenter from './AppCenter.vue';
import SignInCard from './SignInCard.vue';
import MomentPostBox from './MomentPostBox.vue';

const moments = ref([]);
const showModal = ref(false);
const currentImage = ref('');

const showImageModal = (imageUrl) => {
  currentImage.value = imageUrl;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  currentImage.value = '';
};


const handlePostMoment = async (content) => {
  if (content.trim() !== '') {
    try {
      const token = localStorage.getItem('jwt_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.post('http://localhost:5000/api/moments', { content: content.trim() }, { headers });
      if (response.data.code === 200) {
        // Assuming the backend returns the newly created moment data
        const newMoment = response.data.data;
        moments.value.unshift({
          id: newMoment.id,
          user: newMoment.user,
          publish_time: newMoment.publish_time,
          content: newMoment.content,
          images: newMoment.images || [],
          likes: newMoment.likes_count,
          comments: newMoment.comments || []
        });
      } else {
        console.error('Error posting moment:', response.data.message);
      }
    } catch (error) {
      console.error('Error posting moment:', error);
    }
  }
};

const fetchMoments = async () => {
  try {
    const token = localStorage.getItem('jwt_token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    const response = await axios.get('http://localhost:5000/api/moments', { headers });
    console.log('Backend response for moments:', response.data);
    moments.value = response.data.moments.map(moment => ({
      id: moment.id,
      user: moment.user,
      publish_time: moment.publish_time,
      content: moment.content,
      images: moment.images || [],
      likes: moment.likes_count,
      comments: moment.comments || []
    }));
  } catch (error) {
    console.error('Error fetching moments:', error);
    // Handle error, e.g., show a message to the user
  }
};



const commentContent = ref('');
const showCommentBox = ref(null);

const toggleCommentBox = (moment) => {
  if (showCommentBox.value === moment.id) {
    showCommentBox.value = null;
  } else {
    showCommentBox.value = moment.id;
  }
};

const postComment = async (moment) => {
  if (commentContent.value.trim() !== '') {
    try {
      const token = localStorage.getItem('jwt_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.post(`http://localhost:5000/api/moments/${moment.id}/comment`, { content: commentContent.value.trim() }, { headers });
      if (response.data.code === 200) {
        moment.comments.push(response.data.data);
        commentContent.value = '';
        showCommentBox.value = null;
      } else {
        console.error('Error posting comment:', response.data.message);
      }
    } catch (error) {
      console.error('Error posting comment:', error);
    }
  }
};

const toggleLike = async (moment) => {
  try {
    const token = localStorage.getItem('jwt_token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    const response = await axios.post(`http://localhost:5000/api/moment/${moment.id}/like`, {}, { headers });
    moment.likes = response.data.like_count;
  } catch (error) {
    console.error('Error toggling like:', error);
  }
};



onMounted(async () => {
  fetchMoments();
});

// 关闭弹窗函数绑定到模板事件中
// showImageModal和closeModal函数已定义

</script>



<style scoped>
.moment-page-wrapper {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 20px;
  max-width: 1200px; /* 限制整体宽度 */
  margin: 0 auto; /* 居中显示 */
}

.left-sidebar,
.right-sidebar {
  flex-basis: 250px; /* 固定侧边栏宽度 */
  flex-shrink: 0;
}

.moment-page {
  flex-grow: 1;
  max-width: 700px; /* 动态内容区域最大宽度 */
  background-color: #f0f2f5;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.page-header {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.moment-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); /* Adjust column size as needed */
  gap: 10px;
  margin-top: 10px;
}

.moment-image {
  width: 100px;
  height: 100px;
  object-fit: cover; /* Ensures the image covers the area without distortion */
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s ease-in-out;
}

.moment-image:hover {
  transform: scale(1.05);
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.close-button {
  position: absolute;
  top: 20px;
  right: 30px;
  color: white;
  font-size: 30px;
  cursor: pointer;
}



.moment-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.moment-item {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.moment-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.moment-header .user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  margin-right: 10px;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: bold;
  color: #333;
  font-size: 15px;
}

.timestamp {
  color: #999;
  font-size: 12px;
}

.moment-content {
  margin-bottom: 10px;
}

.moment-content p {
  margin: 0;
  line-height: 1.6;
  color: #333;
}

.comment-input-box {
  display: flex;
  margin-top: 10px;
}

.comment-input-box input {
  flex-grow: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 8px;
}

.comment-input-box button {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.comment-input-box button:hover {
  background-color: #66b1ff;
}

.moment-images {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 10px;
  }

  .moment-image {
    width: 100px;
    height: 100px;
    object-fit: cover;
    border-radius: 4px;
  }

.moment-actions {
  display: flex;
  justify-content: space-around;
  padding-top: 10px;
  border-top: 1px solid #eee;
  margin-top: 10px;
}

.action-item {
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.action-item:hover {
  color: #409eff;
}

.icon-like, .icon-comment, .icon-share {
  display: inline-block;
  width: 16px;
  height: 16px;
  background-color: #999; /* 模拟图标 */
  border-radius: 2px;
  vertical-align: middle;
  margin-right: 5px;
}

.moment-comments {
  background-color: #f7f7f7;
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
}

.comment-item {
  margin-bottom: 5px;
  font-size: 13px;
}

.comment-user {
  font-weight: bold;
  color: #555;
  margin-right: 5px;
}

.comment-text {
  color: #333;
}
</style>
