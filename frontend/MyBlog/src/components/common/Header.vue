<template>
  <el-menu
    :default-active="activeIndex"
    class="el-menu-demo"
    mode="horizontal"
    :ellipsis="false"
    @select="handleSelect"
  >
    <el-menu-item index="0">
      <router-link to="/" class="logo-link">我的博客</router-link>
    </el-menu-item>
    <div class="flex-grow" />
    <el-menu-item index="1">
      <router-link to="/">主页</router-link>
    </el-menu-item>
    <el-sub-menu index="2" v-if="isLoggedIn">
      <template #title>{{ username }} ({{ userRole }})</template>
      <el-menu-item index="2-1" @click="logout">退出登录</el-menu-item>
    </el-sub-menu>
    <template v-else>
      <el-menu-item index="3">
        <router-link to="/login">登录</router-link>
      </el-menu-item>
      <el-menu-item index="4">
        <router-link to="/register">注册</router-link>
      </el-menu-item>
    </template>
  </el-menu>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import axios from 'axios';
import { ElMenu, ElMenuItem, ElSubMenu, ElButton } from 'element-plus';

const activeIndex = ref('1');
const handleSelect = (key, keyPath) => {
  console.log(key, keyPath);
};

const isLoggedIn = ref(false);
const username = ref('');
const userRole = ref('');
const router = useRouter();

const fetchUserInfo = async () => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      const response = await axios.get('/api/userinfo', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      username.value = response.data.username;
      userRole.value = response.data.role;
      isLoggedIn.value = true;
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      // Token might be expired or invalid, log out user
      logout();
    }
  } else {
    isLoggedIn.value = false;
    username.value = '';
    userRole.value = '';
  }
};

const checkLoginStatus = () => {
  const token = localStorage.getItem('token');
  if (token) {
    fetchUserInfo();
  } else {
    isLoggedIn.value = false;
    username.value = '';
    userRole.value = '';
  }
};

const logout = () => {
  localStorage.removeItem('token');
  isLoggedIn.value = false;
  username.value = '';
  userRole.value = '';
  router.push('/login');
};

onMounted(() => {
  checkLoginStatus();
  // Listen for custom event to update login status
  window.addEventListener('login-status-changed', checkLoginStatus);
});

// Clean up event listener when component is unmounted
import { onUnmounted } from 'vue';
onUnmounted(() => {
  window.removeEventListener('login-status-changed', checkLoginStatus);
});
</script>

<style scoped>
.flex-grow {
  flex-grow: 1;
}

.el-menu-demo {
  width: 100%;
}

.el-menu-demo .el-menu-item,
.el-menu-demo .el-sub-menu {
  font-size: 16px;
}

.el-menu-demo .el-menu-item a {
  text-decoration: none;
  color: inherit;
}

.logo-link {
  font-size: 24px;
  font-weight: bold;
  text-decoration: none;
  color: inherit;
}
</style>