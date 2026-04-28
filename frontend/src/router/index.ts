import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: () => import('@/components/AppLayout.vue'),
      children: [
        { path: '', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
        { path: 'knowledge-bases', name: 'kb-list', component: () => import('@/views/KBListView.vue') },
        { path: 'knowledge-bases/:id', name: 'kb-detail', component: () => import('@/views/KBDetailView.vue') },
      ],
    },
  ],
})

export default router
