import { createRouter, createWebHistory } from 'vue-router'
import SingleDetect from '../views/SingleDetect.vue'
import BatchDetect from '../views/BatchDetect.vue'
import VideoDetect from '../views/VideoDetect.vue'

const routes = [
  { path: '/', redirect: '/single-detect' },
  { path: '/single-detect', component: SingleDetect, name: 'SingleDetect' },
  { path: '/batch-detect', component: BatchDetect, name: 'BatchDetect' },
  { path: '/video-detect', component: VideoDetect, name: 'VideoDetect' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
