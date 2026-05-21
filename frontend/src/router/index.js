import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'SingleDetect',
    component: () => import('../views/SingleDetect.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
