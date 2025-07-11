import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import About from '../components/common/About.vue';
import PostList from '../components/post/PostList.vue'
import ProjectList from '../components/project/ProjectList.vue'
import PostDetail from '../components/post/PostDetail.vue'
import ProjectDetail from '../components/project/ProjectDetail.vue'
import MomentList from '../components/moment/MomentList.vue'
import AIDialogue from '../components/ai/AIDialogue.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/home',
      name: 'home',
      redirect: '/home/about',
      component: HomeView,
      children: [
        {
          path: 'about',
          name: 'about',
          component: About,
        },
        {
          path: 'postlist',
          name: 'postlist',
          component: PostList,
          meta: { requiresAuth: true },
        },
        {
          path: 'postlist/:post_id',
          name: 'post-detail',
          component: PostDetail,
          props: true,
          meta: { requiresAuth: true },
        },
        {
          path: 'projectlist',
          name: 'projectlist',
          component: ProjectList,
          meta: { requiresAuth: true },
        },
        {
          path: 'projectlist/:project_id',
          name: 'project-detail',
          component: ProjectDetail,
          props: true,
          meta: { requiresAuth: true },
        },
        {
          path: 'monetlist',
          name: 'monetlist',
          component: MomentList,
          meta: { requiresAuth: true },
        },
        {
          path: 'ai-dialogue',
          name: 'ai-dialogue',
          component: AIDialogue,
          meta: { requiresAuth: true },
        },
      ],
    },
    {
      path: '/temp',
      name: 'temp',
      component: () => import('../views/temp.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
  ],
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token');
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next('/login');
  } else if ((to.name === 'login' || to.name === 'register') && isAuthenticated) {
    next('/');
  } else {
    next();
  }
});

export default router
