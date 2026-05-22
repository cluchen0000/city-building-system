<template>
  <div class="img-upload">
    <div class="upload-controls">
      <label class="upload-btn">
        <input
          type="file"
          accept="image/jpeg,image/png,image/jpg"
          @change="onFileChange"
          class="file-input"
        />
        选择图片
      </label>
      <button
        class="detect-btn"
        @click="emit('detect')"
        :disabled="!selectedFile || loading"
      >
        {{ loading ? '检测中...' : '开始检测' }}
      </button>
    </div>

    <div v-if="loading" class="loading-tip">
      ⏳ 正在处理，请稍候...
    </div>

    <div v-if="selectedFile" class="preview-area">
      <h3>原始图片</h3>
      <canvas
        ref="canvasRef"
        :width="imgWidth"
        :height="imgHeight"
        class="preview-canvas"
      ></canvas>
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
const imgWidth = ref(0)
const imgHeight = ref(0)
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
  const img = new Image()
  img.onload = () => {
    imgWidth.value = img.width
    imgHeight.value = img.height
    const canvas = canvasRef.value
    if (canvas) {
      canvas.width = img.width
      canvas.height = img.height
      const ctx = canvas.getContext('2d')
      ctx?.drawImage(img, 0, 0)
      if (selectedFile.value) {
        emit('fileChange', selectedFile.value, blobUrl)
        emit('ready', canvas)
      }
    }
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
  margin: 20px 0;
}

.upload-btn {
  padding: 8px 16px;
  background: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.upload-btn:hover {
  background: #40a9ff;
}

.file-input {
  display: none;
}

.detect-btn {
  padding: 8px 16px;
  background: #52c41a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.detect-btn:disabled {
  background: #95de64;
  cursor: not-allowed;
}

.detect-btn:not(:disabled):hover {
  background: #73d13d;
}

.loading-tip {
  color: #1890ff;
  margin: 16px 0;
}

.preview-area {
  margin-top: 20px;
}

.preview-area h3 {
  margin: 0 0 12px 0;
  color: #262626;
}

.preview-canvas {
  max-width: 100%;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}
</style>
