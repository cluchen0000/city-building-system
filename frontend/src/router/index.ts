// frontend/src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import SingleDetect from '../views/SingleDetect.vue'
import BatchDetect from '../views/BatchDetect.vue'
import VideoDetect from '../views/VideoDetect.vue'
import CameraDetect from '../views/CameraDetect.vue'
import History from '../views/History.vue'
import Login from '../views/login.vue'
import Register from '../views/register.vue'

const routes = [
  { path: '/', redirect: '/single-detect' },
  { path: '/login', component: Login, name: 'Login' },
  { path: '/register', component: Register, name: 'Register' },
  { path: '/single-detect', component: SingleDetect, name: 'SingleDetect' },
  { path: '/batch-detect', component: BatchDetect, name: 'BatchDetect' },
  { path: '/video-detect', component: VideoDetect, name: 'VideoDetect' },
  { path: '/camera-detect', component: CameraDetect, name: 'CameraDetect' },
  { path: '/history', component: History, name: 'History' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

async function validateToken(): Promise<boolean> {
  const token = localStorage.getItem('token');
  if (!token) return false;
  
  try {
    const response = await fetch('/api/auth/verify', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.ok;
  } catch {
    return false;
  }
}

router.beforeEach(async (to, from, next) => {
  if (to.path === '/login' || to.path === '/register') {
    next();
    return;
  }
  
  const token = localStorage.getItem('token');
  if (!token) {
    next('/login');
    return;
  }
  
  const isValid = await validateToken();
  if (!isValid) {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    next('/login');
    return;
  }
  
  next();
})

export default router