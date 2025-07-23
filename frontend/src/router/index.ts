import ProjectList from '@/views/ProjectList.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: ProjectList,
    },
    {
      path: '/project/:id',
      name: 'ProjectDetail',
      component: () => import('@/views/ProjectDetail.vue'),
    },
    {
      path: '/template/:templateId/edit',
      name: 'TemplateEdit',
      component: () => import('@/views/TemplateEdit.vue'),
    },
    {
      path: '/provenance',
      name: 'Provenance',
      component: () => import('@/views/ProvenanceView.vue'),
    },
    {
      path: '/entities',
      name: 'EntityList',
      component: () => import('@/views/EntityList.vue'),
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router
