import { createRouter, createWebHashHistory } from 'vue-router';

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/industries', component: () => import('../views/Industries.vue'), meta: { auth: true } },
  { path: '/prompts', component: () => import('../views/PromptTemplates.vue'), meta: { auth: true } },
];

const router = createRouter({ history: createWebHashHistory(), routes });

router.beforeEach((to) => {
  if (to.meta.auth && !localStorage.getItem('adminToken')) return '/login';
});

export default router;