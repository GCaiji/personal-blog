<template>
  <section class="moment-post-box">
    <img src="@/assets/images/Logos/DefaultLogo.svg" alt="User Avatar" class="user-avatar" />
    <textarea v-model="newMomentContent" placeholder="分享新鲜事..." class="moment-textarea"></textarea>
    <div class="post-actions">
      <button @click="postMoment" class="post-button">发布</button>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue';

const newMomentContent = ref('');
const emits = defineEmits(['post-moment']);

const postMoment = () => {
  if (newMomentContent.value.trim() !== '') {
    emits('post-moment', newMomentContent.value.trim());
    newMomentContent.value = '';
  }
};
</script>

<style scoped>
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
  background-color: #ffffff; /* 模拟头像 */
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
</style>
