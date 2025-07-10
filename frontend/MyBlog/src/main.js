import './assets/main.css';

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import axios from 'axios';

import App from './App.vue';
import router from './router';

import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

const app = createApp(App);

// Configure axios base URL
axios.defaults.baseURL = 'http://localhost:5000'; // Your backend API base URL

// Add a request interceptor to include the JWT token
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

app.use(createPinia());
app.use(router);
app.use(ElementPlus);

app.mount('#app');
