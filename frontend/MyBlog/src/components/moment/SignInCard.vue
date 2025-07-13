<template>
  <div class="sign-in-card">
    <h3>每日签到</h3>
    <div class="sign-in-status">
      <p v-if="!hasSignedIn">今天还没有签到哦！</p>
      <p v-else>今天已签到，获得 {{ pointsEarned }} 积分！</p>
    </div>
    <button @click="signIn" :disabled="hasSignedIn" class="sign-in-button">
      {{ hasSignedIn ? '已签到' : '立即签到' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const hasSignedIn = ref(false);
const pointsEarned = ref(0);

const signIn = () => {
  if (!hasSignedIn.value) {
    pointsEarned.value = Math.floor(Math.random() * 10) + 1; // 随机获得1-10积分
    hasSignedIn.value = true;
    alert(`签到成功！获得 ${pointsEarned.value} 积分。`);
  }
};
</script>

<style scoped>
.sign-in-card {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.sign-in-card h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
}

.sign-in-status {
  margin-bottom: 15px;
  color: #666;
  font-size: 14px;
}

.sign-in-button {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 15px;
  transition: background-color 0.3s ease;
}

.sign-in-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.sign-in-button:hover:not(:disabled) {
  background-color: #d32f2f;
}
</style>