<template>
  <div class="single-detect">
    <div class="page-header">
      <h1>🏢 单图建筑检测</h1>
      <p class="page-description">上传遥感影像或航拍图片，智能识别建筑物并计算面积</p>
    </div>

    <div class="main-content">
      <div class="card upload-card">
        <div class="card-header">
          <h3 class="card-title">📁 上传图片</h3>
        </div>
        <div class="card-body">
          <ImgUpload
            :loading="loading"
            @detect="detect"
            @fileChange="onFileChange"
            @ready="onCanvasReady"
          />
        </div>
      </div>

      <ResultShow v-if="detectResult" :result="detectResult" />

      <div v-if="errorMsg" class="alert alert-error">
        <span class="alert-icon">❌</span>
        <span>{{ errorMsg }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ImgUpload from '../components/ImgUpload.vue'
import ResultShow from '../components/ResultShow.vue'
import { detectSingleImage } from '../api/detectApi'
import type { DetectResult, DetectionBox } from '../types'

const loading = ref(false)
const errorMsg = ref('')
const detectResult = ref<DetectResult | null>(null)
const selectedFile = ref<File | null>(null)
const imageUrl = ref('')
let previewCanvas: HTMLCanvasElement | null = null

function onFileChange(file: File, url: string) {
  selectedFile.value = file
  imageUrl.value = url
  detectResult.value = null
  errorMsg.value = ''
}

function onCanvasReady(canvas: HTMLCanvasElement) {
  previewCanvas = canvas
}

async function detect() {
  if (!selectedFile.value) {
    errorMsg.value = '请先选择图片'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const result = await detectSingleImage(selectedFile.value)
    detectResult.value = result
  } catch (err: any) {
    console.error(err)
    errorMsg.value = `检测失败: ${err.message}`
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.single-detect {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-description {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: var(--transition-normal);
}

.card:hover {
  box-shadow: var(--shadow-md);
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-secondary);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.card-body {
  padding: 20px;
}

.alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  font-size: 14px;
}

.alert-error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: var(--danger-color);
}

.alert-icon {
  font-size: 18px;
}
</style>
