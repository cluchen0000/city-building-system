<template>
  <div class="img-upload">
    <div class="upload-controls">
      <label class="btn btn-primary">
        <input
          type="file"
          accept="image/jpeg,image/png,image/jpg"
          @change="onFileChange"
          class="file-input"
        />
        <span class="btn-icon">📷</span>
        <span>选择图片</span>
      </label>
      <button
        class="btn btn-success"
        @click="emit('detect')"
        :disabled="!selectedFile || loading"
      >
        <span class="btn-icon">{{ loading ? '⏳' : '🚀' }}</span>
        <span>{{ loading ? '检测中...' : '开始检测' }}</span>
      </button>
    </div>

    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在处理，请稍候...</span>
    </div>

    <div v-if="selectedFile" class="preview-section">
      <div class="preview-header">
        <h4>🖼️ 原始图片预览</h4>
        <span class="file-info">{{ selectedFile.name }}</span>
      </div>
      <div class="canvas-wrapper">
        <canvas
          ref="canvasRef"
          class="preview-canvas"
        ></canvas>
        <div v-if="!imgLoaded" class="canvas-loading">
          <div class="mini-spinner"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'

const props = defineProps<{
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'detect'): void
  (e: 'fileChange', file: File, url: string): void
  (e: 'ready', canvas: HTMLCanvasElement): void
}>()

const selectedFile = ref<File | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const imgLoaded = ref(false)
let blobUrl = ''

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    if (blobUrl) {
      URL.revokeObjectURL(blobUrl)
    }
    const file = input.files[0]
    selectedFile.value = file
    blobUrl = URL.createObjectURL(file)
    loadImageToCanvas(blobUrl)
  }
}

function loadImageToCanvas(url: string) {
  imgLoaded.value = false
  const img = new Image()
  img.onload = () => {
    const canvas = canvasRef.value
    if (canvas) {
      const maxWidth = 600
      const maxHeight = 400
      let width = img.width
      let height = img.height
      
      if (width > maxWidth) {
        height = (maxWidth / width) * height
        width = maxWidth
      }
      if (height > maxHeight) {
        width = (maxHeight / height) * width
        height = maxHeight
      }
      
      canvas.width = width
      canvas.height = height
      const ctx = canvas.getContext('2d')
      ctx?.drawImage(img, 0, 0, width, height)
      imgLoaded.value = true
      if (selectedFile.value) {
        emit('fileChange', selectedFile.value, blobUrl)
        emit('ready', canvas)
      }
    }
  }
  img.onerror = () => {
    imgLoaded.value = true
    console.error('图片加载失败')
  }
  img.src = url
}

onUnmounted(() => {
  if (blobUrl) {
    URL.revokeObjectURL(blobUrl)
  }
})
</script>

<style scoped>
.img-upload {
  width: 100%;
}

.upload-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-normal);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.btn-success {
  background: linear-gradient(135deg, var(--success-color) 0%, var(--success-dark) 100%);
  color: #ffffff;
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.3);
}

.btn-icon {
  font-size: 16px;
}

.file-input {
  display: none;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 16px;
  color: #ffffff;
  font-size: 16px;
}

.preview-section {
  margin-top: 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.preview-header h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.file-info {
  font-size: 13px;
  color: var(--text-tertiary);
  background: var(--bg-secondary);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
}

.canvas-wrapper {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
}

.preview-canvas {
  display: block;
  max-width: 100%;
  height: auto;
}

.canvas-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.mini-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(24, 144, 255, 0.2);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
</style>
