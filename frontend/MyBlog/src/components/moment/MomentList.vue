<template>
  <div class="moment-page-wrapper">
    <aside class="left-sidebar">
      <AppCenter />
    </aside>

    <div class="moment-page">
      <header class="page-header">
        <h1>我的动态</h1>
      </header>

      <section class="moment-post-box">
        <div class="user-avatar"></div>
        <textarea v-model="newMomentContent" placeholder="分享新鲜事..." class="moment-textarea"></textarea>
        <div class="post-actions">
          <button @click="postMoment" class="post-button">发布</button>
        </div>
      </section>

      <section class="moment-list">
        <div v-for="moment in moments" :key="moment.id" class="moment-item">
          <div class="moment-header">
            <div class="user-avatar"></div>
            <div class="user-info">
              <span class="username">{{ moment.username }}</span>
              <span class="timestamp">{{ moment.timestamp }}</span>
            </div>
          </div>
          <div class="moment-content">
            <p>{{ moment.content }}</p>
            <div v-if="moment.images && moment.images.length" class="moment-images">
              <img v-for="image in moment.images" :src="image" :key="image" class="moment-image" />
            </div>
          </div>
          <div class="moment-actions">
            <span class="action-item"><i class="icon-like"></i> 赞 ({{ moment.likes }})</span>
            <span class="action-item"><i class="icon-comment"></i> 评论 ({{ moment.comments.length }})</span>
            <span class="action-item"><i class="icon-share"></i> 转发</span>
          </div>
          <div class="moment-comments">
            <div v-for="comment in moment.comments" :key="comment.id" class="comment-item">
              <span class="comment-user">{{ comment.username }}:</span>
              <span class="comment-text">{{ comment.text }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>

    <aside class="right-sidebar">
      <SignInCard />
    </aside>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AppCenter from './AppCenter.vue';
import SignInCard from './SignInCard.vue';

const newMomentContent = ref('');
const moments = ref([
  {
    id: 1,
    username: '用户A',
    timestamp: '2023-10-26 10:30',
    content: '今天天气真好，适合出去走走！',
    images: ['https://via.placeholder.com/150/FF0000/FFFFFF?text=Image1'],
    likes: 15,
    comments: [
      { id: 101, username: '用户B', text: '是啊，阳光明媚！' },
      { id: 102, username: '用户C', text: '羡慕ing~' }
    ]
  },
  {
    id: 2,
    username: '用户D',
    timestamp: '2023-10-25 18:00',
    content: '分享一首最近很喜欢的歌，希望大家也喜欢。',
    images: [],
    likes: 8,
    comments: [
      { id: 201, username: '用户E', text: '好听！求歌名！' }
    ]
  }
]);

const postMoment = () => {
  if (newMomentContent.value.trim() !== '') {
    const newId = moments.value.length > 0 ? Math.max(...moments.value.map(m => m.id)) + 1 : 1;
    moments.value.unshift({
      id: newId,
      username: '当前用户',
      timestamp: new Date().toLocaleString(),
      content: newMomentContent.value.trim(),
      images: [],
      likes: 0,
      comments: []
    });
    newMomentContent.value = '';
  }
};
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

.moment-post-box {
  display: flex;
  align-items: flex-start;
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.moment-post-box .user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #409eff; /* 模拟头像 */
  margin-right: 15px;
  flex-shrink: 0;
}

.moment-textarea {
  flex-grow: 1;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
  font-size: 14px;
  min-height: 60px;
  resize: vertical;
  margin-right: 10px;
}

.post-actions {
  display: flex;
  align-items: center;
}

.post-button {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.post-button:hover {
  background-color: #337ecc;
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
  background-color: #67c23a; /* 模拟头像 */
  margin-right: 10px;
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

.moment-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
  margin-top: 10px;
}

.moment-image {
  width: 100%;
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
