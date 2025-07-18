<template>
  <section class="moment-post-box">
    <img src="@/assets/images/Logos/DefaultLogo.svg" alt="User Avatar" class="user-avatar" />
    <textarea v-model="newMomentContent" placeholder="分享新鲜事..." class="moment-textarea"></textarea>
     <div class="post-options">
      <label for="image-upload" class="add-image-box">
        <span class="plus-icon">+</span>
        <input type="file" id="image-upload" @change="handleImageUpload" accept="image/*" multiple class="hidden-input" />
      </label>
      <button @click="postMoment" class="post-button">发布</button>
    </div>
    <div class="image-previews-container">
      <div v-for="(image, index) in imageFiles" :key="index" class="image-preview-item">
        <img :src="image.preview" alt="Image Preview" class="image-preview" />
        <button @click="removeImage(index)" class="remove-image-button">X</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';

const newMomentContent = ref('');
const imageFiles = ref([]); // Store objects with file and preview URL
const emits = defineEmits(['post-moment']);

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

const showSuccess = (message) => {
  ElMessage.success({
    message,
    duration: 3000,
    showClose: true,
  });
};

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const handleImageUpload = (event) => {
  const files = Array.from(event.target.files);
  files.forEach(file => {
    const reader = new FileReader();
    reader.onload = (e) => {
      imageFiles.value.push({ file: file, preview: e.target.result });
    };
    reader.readAsDataURL(file);
  });
  event.target.value = ''; // Clear the input so the same file can be selected again
};

const removeImage = (index) => {
  imageFiles.value.splice(index, 1);
};

const postMoment = async () => {
      if (!newMomentContent.value.trim()) {
        ElMessage.warning('动态内容不能为空！');
        return;
      }

      try {
        const response = await api.post('/moments', {
          content: newMomentContent.value
        });
        if (response.data.success) {
          const newMomentId = response.data.moment_id;
          if (imageFiles.value.length > 0) {
            await uploadImage(newMomentId);
          }
          emits('post-moment');
          newMomentContent.value = '';
          imageFiles.value = [];
          showSuccess('动态发布成功！');
        } else {
          console.error('发布动态失败:', response.data.error);
          ElMessage.error('发布动态失败: ' + response.data.error);
        }
      } catch (error) {
        console.error('发布动态请求失败:', error);
        ElMessage.error('发布动态请求失败: ' + error.message);
      }
    };

    const uploadImage = async (momentId) => {
      if (imageFiles.value.length === 0) {
        return;
      }

      const formData = new FormData();
      imageFiles.value.forEach(file => {
        formData.append('image', file.file);
      });

      try {
        const response = await api.post(`/moment/${momentId}/images`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        if (response.data.success) {
          // handleUploadSuccess(response); // No need for separate success handler here, main postMoment handles overall success
        } else {
          console.error('图片上传失败:', response.data.error);
          ElMessage.error('图片上传失败: ' + response.data.error);
        }
      } catch (error) {
        console.error('图片上传请求失败:', error);
        ElMessage.error('图片上传请求失败: ' + error.message);
      }
    };
</script>

<style scoped>
.moment-post-box {
  display: flex;
  flex-direction: column; /* Changed to column layout */
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
  align-self: flex-start; /* Align avatar to the start */
}

.moment-textarea {
  flex-grow: 1;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
  font-size: 14px;
  min-height: 60px;
  resize: vertical;
  width: 100%; /* Take full width */
  margin-bottom: 10px; /* Add margin below textarea */
}

.post-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-top: 10px;
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

.add-image-box {
  width: 40px;
  height: 40px;
  border: 2px dashed #ccc;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.add-image-box:hover {
  border-color: #409eff;
}

.plus-icon {
  font-size: 24px;
  color: #ccc;
}

.hidden-input {
  display: none;
}

.image-previews-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
  width: 100%;
}

.image-preview-item {
  position: relative;
  width: 100px;
  height: 100px;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.image-preview {
  max-width: 100%;
  max-height: 100%;
  display: block;
  border-radius: 5px;
}

.remove-image-button {
  position: absolute;
  top: 2px;
  right: 2px;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  z-index: 1;
}
</style>
