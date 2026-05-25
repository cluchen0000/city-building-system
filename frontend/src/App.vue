<template>
  <div id="app">
    <AppNav />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppNav from './components/AppNav.vue'
</script>

<style scoped>
#app {
  min-height: 100vh;
  background: #f0f2f5;
}

.main-content {
  padding-top: 8px;
}
</style>
