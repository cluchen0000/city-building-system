<template>
  <div class="single-detect">
    <h1>🏢 单图建筑检测</h1>
    
    <ImgUpload
      :loading="loading"
      @detect="detect"
      @fileChange="onFileChange"
      @ready="onCanvasReady"
    />

    <ResultShow v-if="detectResult" :result="detectResult" />

    <div v-if="errorMsg" class="error-tip">{{ errorMsg }}</div>
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
    if (previewCanvas) {
      drawBoxesOnCanvas(previewCanvas, result.boxes)
    }
  } catch (err: any) {
    console.error(err)
    errorMsg.value = `检测失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

function drawBoxesOnCanvas(canvas: HTMLCanvasElement, boxes: DetectionBox[]) {
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const img = new Image()
  img.onload = () => {
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
    boxes.forEach(box => {
      const { x1, y1, x2, y2, confidence, class_name, area_sqm } = box
      ctx.strokeStyle = '#ff4d4f'
      ctx.lineWidth = 2
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)
      ctx.fillStyle = '#ff4d4f'
      ctx.font = 'bold 14px "Segoe UI"'
      const label = `${class_name} ${(confidence * 100).toFixed(1)}%`
      const areaText = area_sqm ? ` ${area_sqm}m²` : ''
      ctx.fillText(label + areaText, x1, y1 - 5)
    })
  }
  img.src = imageUrl.value
}
</script>

<style scoped>
.single-detect {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.single-detect h1 {
  color: #262626;
  margin: 0 0 20px 0;
}

.error-tip {
  color: #ff4d4f;
  margin-top: 20px;
  padding: 12px 16px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
}
</style>
