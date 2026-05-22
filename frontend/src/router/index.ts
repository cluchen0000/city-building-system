import { createRouter, createWebHistory } from 'vue-router'
import SingleDetect from '../views/SingleDetect.vue'

const routes = [
  { path: '/', component: SingleDetect },
  { path: '/single-detect', component: SingleDetect },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
