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
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const currentRoute = computed(() => route.name)
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
}
</style>
