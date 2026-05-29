<template>
  <nav class="app-nav">
    <div class="nav-logo">
      <span class="logo-icon">🏢</span>
      <span class="logo-text">城市建筑检测系统</span>
    </div>
    <div class="nav-links">
      <router-link
        to="/single-detect"
        class="nav-link"
        :class="{ active: currentRoute === 'SingleDetect' }"
      >
        <span class="link-icon">🖼️</span>
        <span>单图检测</span>
      </router-link>
      <router-link
        to="/batch-detect"
        class="nav-link"
        :class="{ active: currentRoute === 'BatchDetect' }"
      >
        <span class="link-icon">📦</span>
        <span>批量检测</span>
      </router-link>
      <router-link
        to="/video-detect"
        class="nav-link"
        :class="{ active: currentRoute === 'VideoDetect' }"
      >
        <span class="link-icon">🎬</span>
        <span>视频检测</span>
      </router-link>
      <router-link
        to="/camera-detect"
        class="nav-link"
        :class="{ active: currentRoute === 'CameraDetect' }"
      >
        <span class="link-icon">📹</span>
        <span>摄像头检测</span>
      </router-link>
      <router-link
        to="/history"
        class="nav-link"
        :class="{ active: currentRoute === 'History' }"
      >
        <span class="link-icon">📜</span>
        <span>历史记录</span>
      </router-link>
    </div>
    <div class="user-center">
      <button class="user-btn" @click="toggleUserMenu">
        <span class="user-icon">👤</span>
        <span class="user-name">{{ username }}</span>
        <span class="user-arrow">{{ isMenuOpen ? '▼' : '▲' }}</span>
      </button>
      <div v-if="isMenuOpen" class="user-menu" @click.self="isMenuOpen = false">
        <div class="user-info">
          <div class="user-avatar">👤</div>
          <div class="user-details">
            <div class="info-name">{{ username }}</div>
            <div class="info-role">普通用户</div>
          </div>
        </div>
        <div class="menu-divider"></div>
        <button class="menu-item" @click="logout">
          <span class="menu-icon">🚪</span>
          <span>注销登录</span>
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const currentRoute = computed(() => route.name)
const isMenuOpen = ref(false)
const username = ref(localStorage.getItem('username') || '用户')

async function fetchUserInfo() {
  const storedUsername = localStorage.getItem('username')
  if (storedUsername && storedUsername !== '用户') {
    username.value = storedUsername
    return
  }
  
  const token = localStorage.getItem('token')
  if (!token) return
  
  try {
    const response = await fetch('/api/auth/verify', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      username.value = data.username
      localStorage.setItem('username', data.username)
    }
  } catch {
    console.error('获取用户信息失败')
  }
}

onMounted(() => {
  fetchUserInfo()
})

watch(() => route.path, () => {
  fetchUserInfo()
})

function toggleUserMenu() {
  isMenuOpen.value = !isMenuOpen.value
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  username.value = '用户'
  isMenuOpen.value = false
  router.push('/login')
}
</script>

<style scoped>
.app-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 60px;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 1px;
}

.nav-links {
  display: flex;
  gap: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  font-weight: 500;
}

.link-icon {
  font-size: 18px;
}

.user-center {
  position: relative;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.15);
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-btn:hover {
  background: rgba(255, 255, 255, 0.25);
}

.user-icon {
  font-size: 20px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
}

.user-arrow {
  font-size: 12px;
  transition: transform 0.3s ease;
}

.user-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 200px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  padding: 12px 0;
  z-index: 1001;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px 12px;
}

.user-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.user-details {
  flex: 1;
}

.info-name {
  font-size: 15px;
  font-weight: 600;
  color: #262626;
}

.info-role {
  font-size: 13px;
  color: #8c8c8c;
  margin-top: 2px;
}

.menu-divider {
  height: 1px;
  background: #f0f0f0;
  margin: 8px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 16px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  color: #595959;
  transition: background 0.2s ease;
}

.menu-item:hover {
  background: #f5f5f5;
  color: #1890ff;
}

.menu-icon {
  font-size: 16px;
}

@media (max-width: 768px) {
  .app-nav {
    padding: 0 12px;
    flex-direction: column;
    height: auto;
    padding-bottom: 12px;
  }

  .nav-logo {
    padding: 12px 0;
  }

  .nav-links {
    width: 100%;
    justify-content: space-around;
  }

  .nav-link {
    padding: 8px 12px;
    font-size: 13px;
  }

  .user-center {
    position: absolute;
    top: 12px;
    right: 12px;
  }

  .user-btn {
    padding: 6px 12px;
  }

  .user-name {
    display: none;
  }
}
</style>
