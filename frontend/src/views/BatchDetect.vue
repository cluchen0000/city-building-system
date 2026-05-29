<template>
  <div class="batch-detect">
    <h1>📦 批量建筑检测</h1>

    <div class="upload-section">
      <div
        class="drop-zone"
        :class="{ 'drag-over': isDragOver }"
        @dragover.prevent="onDragOver"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
      >
        <div class="drop-content">
          <div class="drop-icon">📁</div>
          <div class="drop-text">拖拽图片到此处上传</div>
          <div class="drop-hint">或点击下方按钮选择图片</div>
        </div>
      </div>

      <div class="upload-controls">
        <label class="upload-btn">
          <input
            ref="fileInputRef"
            type="file"
            accept="image/*"
            multiple
            @change="onFileChange"
            class="file-input"
          />
          ➕ 选择图片
        </label>
        <button
          class="clear-btn"
          v-if="selectedFiles.length > 0"
          @click="clearAllFiles"
        >
          🗑️ 清空
        </button>
        <button
          class="detect-btn"
          @click="detect"
          :disabled="selectedFiles.length === 0 || loading"
        >
          {{ loading ? '检测中...' : '开始批量检测' }}
        </button>
        <span class="file-count" v-if="selectedFiles.length > 0">
          已选择 {{ selectedFiles.length }} 张图片
        </span>
      </div>
    </div>

    <div v-if="loading" class="loading-tip">
      ⏳ 正在批量处理 {{ selectedFiles.length }} 张图片，请稍候...
    </div>

    <div v-if="errorMsg" class="error-tip">{{ errorMsg }}</div>

    <div v-if="selectedFiles.length > 0 && (!batchResults || batchResults.length === 0)" class="preview-section">
      <h3>📷 已选择的图片预览（点击右上角 ✕ 删除）</h3>
      <div class="preview-grid">
        <div
          v-for="(item, index) in previewFiles"
          :key="index"
          class="preview-card"
        >
          <button
            class="remove-btn"
            @click="removeFile(index)"
            title="删除此图片"
          >
            ✕
          </button>
          <img :src="item.url" class="preview-img" />
          <div class="preview-info">
            <div class="preview-name">{{ item.file.name }}</div>
            <div class="preview-size">{{ formatFileSize(item.file.size) }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="batchResults" class="results-area">
      <h3>批量检测结果</h3>

      <div v-if="summary" class="summary-card">
        <h4>检测汇总</h4>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-label">总图片数</span>
            <span class="summary-value">{{ summary.total_images }}</span>
          </div>
          <div class="summary-item success">
            <span class="summary-label">成功</span>
            <span class="summary-value">{{ summary.success_count }}</span>
          </div>
          <div class="summary-item failed">
            <span class="summary-label">失败</span>
            <span class="summary-value">{{ summary.failed_count }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">总检测目标</span>
            <span class="summary-value">{{ summary.total_objects }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">总耗时</span>
            <span class="summary-value">{{ summary.total_cost_time.toFixed(2) }} 秒</span>
          </div>
        </div>
      </div>

      <div class="results-list">
        <div
          v-for="(result, index) in batchResults"
          :key="index"
          class="result-card"
          :class="{ failed: !result.success }"
        >
          <div class="result-header">
            <span class="result-index">图片 {{ index + 1 }}</span>
            <span class="result-status" :class="result.success ? 'success' : 'failed'">
              {{ result.success ? '✅ 成功' : '❌ 失败' }}
            </span>
          </div>
          <div class="result-filename">{{ result.filename }}</div>

          <div v-if="result.success">
            <div class="result-stats">
              <span>检测数: {{ result.total_objects }}</span>
              <span>耗时: {{ result.cost_time }} 秒</span>
            </div>
            <div v-if="result.result_url" class="result-image">
              <img :src="result.result_url" class="annotated-img" />
            </div>
          </div>
          <div v-else class="error-detail">
            {{ result.error }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { detectBatchImages, type BatchDetectResult } from '../api/detectApi'
import type { BatchImageResult, BatchSummary } from '../types'

interface PreviewFile {
  file: File
  url: string
}

const loading = ref(false)
const errorMsg = ref('')
const selectedFiles = ref<File[]>([])
const previewFiles = ref<PreviewFile[]>([])
const batchResults = ref<BatchImageResult[]>([])
const summary = ref<BatchSummary | null>(null)
const isDragOver = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const blobUrls: string[] = []

function addFiles(files: FileList | File[]) {
  const fileArray = Array.from(files)
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']
  
  const newFiles = fileArray.filter(file => {
    const isValidMime = file.type.startsWith('image/')
    const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    const isValidExt = imageExtensions.includes(ext)
    return isValidMime || isValidExt
  })

  if (newFiles.length > 0) {
    selectedFiles.value = [...selectedFiles.value, ...newFiles]

    newFiles.forEach(file => {
      const url = URL.createObjectURL(file)
      blobUrls.push(url)
      previewFiles.value.push({ file, url })
    })

    batchResults.value = []
    summary.value = null
    errorMsg.value = ''
  }
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    addFiles(input.files)
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }
  }
}

function onDragOver() {
  isDragOver.value = true
}

function onDragLeave() {
  isDragOver.value = false
}

function onDrop(e: DragEvent) {
  isDragOver.value = false
  if (e.dataTransfer?.files) {
    addFiles(e.dataTransfer.files)
  }
}

function removeFile(index: number) {
  URL.revokeObjectURL(previewFiles.value[index].url)
  previewFiles.value.splice(index, 1)
  selectedFiles.value.splice(index, 1)
}

function clearAllFiles() {
  blobUrls.forEach(url => URL.revokeObjectURL(url))
  blobUrls.length = 0
  previewFiles.value = []
  selectedFiles.value = []
  batchResults.value = []
  summary.value = null
  errorMsg.value = ''
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

async function detect() {
  if (selectedFiles.value.length === 0) {
    errorMsg.value = '请先选择图片'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const result: BatchDetectResult = await detectBatchImages(selectedFiles.value)
    batchResults.value = result.results
    summary.value = result.summary
  } catch (err: any) {
    console.error(err)
    errorMsg.value = `批量检测失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  blobUrls.forEach(url => URL.revokeObjectURL(url))
})
</script>

<style scoped>
.batch-detect {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.batch-detect h1 {
  color: #262626;
  margin: 0 0 20px 0;
}

.upload-section {
  margin-bottom: 20px;
}

.drop-zone {
  border: 2px dashed #d9d9d9;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  background: #fafafa;
  transition: all 0.3s ease;
  margin-bottom: 16px;
}

.drop-zone:hover,
.drop-zone.drag-over {
  border-color: #1890ff;
  background: #e6f7ff;
}

.drop-zone.drag-over {
  transform: scale(1.01);
}

.drop-content {
  color: #8c8c8c;
}

.drop-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.drop-text {
  font-size: 16px;
  color: #595959;
  margin-bottom: 8px;
}

.drop-hint {
  font-size: 13px;
  color: #bfbfbf;
}

.upload-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.upload-btn,
.clear-btn,
.detect-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.upload-btn {
  background: #1890ff;
  color: white;
}

.upload-btn:hover {
  background: #40a9ff;
}

.clear-btn {
  background: #fff;
  color: #595959;
  border: 1px solid #d9d9d9;
}

.clear-btn:hover {
  background: #fafafa;
  border-color: #bfbfbf;
}

.detect-btn {
  background: #52c41a;
  color: white;
}

.detect-btn:disabled {
  background: #95de64;
  cursor: not-allowed;
}

.detect-btn:not(:disabled):hover {
  background: #73d13d;
}

.file-input {
  display: none;
}

.file-count {
  color: #1890ff;
  font-size: 14px;
  font-weight: 500;
}

.loading-tip {
  color: #1890ff;
  margin: 16px 0;
  padding: 16px 20px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 6px;
}

.error-tip {
  color: #ff4d4f;
  margin: 20px 0;
  padding: 12px 16px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 6px;
}

.preview-section h3 {
  margin: 24px 0 16px 0;
  color: #262626;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.preview-card {
  position: relative;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.preview-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border: 2px solid white;
  border-radius: 50%;
  background: #ff4d4f;
  color: white;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.remove-btn:hover {
  background: #ff7875;
  transform: scale(1.15);
}

.preview-img {
  width: 100%;
  height: 140px;
  object-fit: cover;
  display: block;
}

.preview-info {
  padding: 10px;
}

.preview-name {
  font-size: 12px;
  color: #262626;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.preview-size {
  font-size: 11px;
  color: #8c8c8c;
}

.results-area h3 {
  margin: 24px 0 16px 0;
  color: #262626;
}

.summary-card {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.summary-card h4 {
  margin: 0 0 16px 0;
  color: #262626;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.summary-item {
  text-align: center;
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.summary-item.success .summary-value {
  color: #52c41a;
}

.summary-item.failed .summary-value {
  color: #ff4d4f;
}

.summary-label {
  display: block;
  color: #8c8c8c;
  font-size: 12px;
  margin-bottom: 4px;
}

.summary-value {
  display: block;
  color: #262626;
  font-size: 20px;
  font-weight: 600;
}

.results-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 16px;
}

.result-card {
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  overflow: hidden;
}

.result-card.failed {
  border-color: #ffccc7;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.result-index {
  color: #262626;
  font-weight: 600;
}

.result-status {
  font-size: 14px;
}

.result-status.success {
  color: #52c41a;
}

.result-status.failed {
  color: #ff4d4f;
}

.result-filename {
  padding: 12px 16px;
  color: #595959;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}

.result-stats {
  padding: 12px 16px;
  display: flex;
  gap: 20px;
  color: #8c8c8c;
  font-size: 13px;
}

.result-image {
  padding: 12px 16px;
}

.annotated-img {
  max-width: 100%;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.error-detail {
  padding: 16px;
  color: #ff4d4f;
  background: #fff2f0;
  font-size: 13px;
}
</style>
