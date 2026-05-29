<template>
  <div class="batch-detect">
    <div class="page-header">
      <h1>📦 批量建筑检测</h1>
      <p class="page-description">同时上传多张遥感影像，批量进行建筑检测与面积统计</p>
    </div>

    <div class="card upload-card">
      <div class="card-header">
        <h3 class="card-title">📁 上传图片</h3>
      </div>
      <div class="card-body">
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
            <div class="drop-hint">支持 JPG、PNG 格式，可多选</div>
          </div>
        </div>

        <div class="upload-controls">
          <label class="btn btn-primary">
            <input
              ref="fileInputRef"
              type="file"
              accept="image/*"
              multiple
              @change="onFileChange"
              class="file-input"
            />
            <span class="btn-icon">➕</span>
            <span>选择图片</span>
          </label>
          <button
            v-if="selectedFiles.length > 0"
            class="btn btn-secondary"
            @click="clearAllFiles"
          >
            <span class="btn-icon">🗑️</span>
            <span>清空</span>
          </button>
          <button
            class="btn btn-success"
            @click="detect"
            :disabled="selectedFiles.length === 0 || loading"
          >
            <span class="btn-icon">{{ loading ? '⏳' : '🚀' }}</span>
            <span>{{ loading ? '检测中...' : '开始批量检测' }}</span>
          </button>
          <span v-if="selectedFiles.length > 0" class="file-counter">
            已选择 {{ selectedFiles.length }} 张图片
          </span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在批量处理 {{ selectedFiles.length }} 张图片...</span>
    </div>

    <div v-if="errorMsg" class="alert alert-error">
      <span class="alert-icon">❌</span>
      <span>{{ errorMsg }}</span>
    </div>

    <div v-if="selectedFiles.length > 0 && (!batchResults || batchResults.length === 0)" class="card preview-card">
      <div class="card-header">
        <h3 class="card-title">📷 已选择的图片</h3>
        <span class="card-subtitle">点击右上角 ✕ 删除</span>
      </div>
      <div class="card-body">
        <div class="preview-grid">
          <div
            v-for="(item, index) in previewFiles"
            :key="index"
            class="preview-item"
          >
            <button
              class="remove-btn"
              @click="removeFile(index)"
              title="删除此图片"
            >
              ✕
            </button>
            <img :src="item.url" class="preview-img" :alt="item.file.name" />
            <div class="preview-info">
              <div class="preview-name">{{ item.file.name }}</div>
              <div class="preview-size">{{ formatFileSize(item.file.size) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="batchResults" class="results-section">
      <div class="card summary-card">
        <div class="card-header">
          <h3 class="card-title">📊 检测汇总</h3>
        </div>
        <div class="card-body">
          <div class="summary-grid">
            <div class="summary-item">
              <div class="summary-icon">📁</div>
              <div class="summary-value">{{ summary?.total_images || 0 }}</div>
              <div class="summary-label">总图片数</div>
            </div>
            <div class="summary-item success">
              <div class="summary-icon">✅</div>
              <div class="summary-value">{{ summary?.success_count || 0 }}</div>
              <div class="summary-label">成功</div>
            </div>
            <div class="summary-item failed">
              <div class="summary-icon">❌</div>
              <div class="summary-value">{{ summary?.failed_count || 0 }}</div>
              <div class="summary-label">失败</div>
            </div>
            <div class="summary-item">
              <div class="summary-icon">🏢</div>
              <div class="summary-value">{{ summary?.total_objects || 0 }}</div>
              <div class="summary-label">总检测目标</div>
            </div>
            <div class="summary-item">
              <div class="summary-icon">⏱️</div>
              <div class="summary-value">{{ (summary?.total_cost_time || 0).toFixed(2) }}s</div>
              <div class="summary-label">总耗时</div>
            </div>
          </div>
        </div>
      </div>

      <div class="results-header">
        <h3>📋 检测结果详情</h3>
        <span class="results-count">共 {{ batchResults.length }} 个结果</span>
      </div>

      <div class="results-grid">
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
          <div class="result-body">
            <div class="result-filename">{{ result.filename }}</div>
            <div v-if="result.success">
              <div class="result-stats">
                <span class="stat">检测数: {{ result.total_objects }}</span>
                <span class="stat">耗时: {{ result.cost_time }}s</span>
              </div>
              <div v-if="result.result_url" class="result-image-wrapper">
                <img :src="result.result_url" class="result-image" />
              </div>
            </div>
            <div v-else class="error-message">
              {{ result.error }}
            </div>
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

.card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.card-subtitle {
  font-size: 13px;
  color: var(--text-tertiary);
}

.card-body {
  padding: 20px;
}

.drop-zone {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-lg);
  padding: 48px 20px;
  text-align: center;
  background: var(--bg-secondary);
  transition: var(--transition-normal);
  margin-bottom: 16px;
}

.drop-zone:hover,
.drop-zone.drag-over {
  border-color: var(--primary-color);
  background: #e6f7ff;
}

.drop-zone.drag-over {
  transform: scale(1.01);
}

.drop-content {
  color: var(--text-tertiary);
}

.drop-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.drop-text {
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.drop-hint {
  font-size: 13px;
  color: var(--text-tertiary);
}

.upload-controls {
  display: flex;
  align-items: center;
  gap: 12px;
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

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: #f0f0f0;
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

.file-counter {
  font-size: 14px;
  color: var(--primary-color);
  font-weight: 500;
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

.alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 16px;
  border-radius: var(--radius-md);
  font-size: 14px;
  margin-bottom: 20px;
}

.alert-error {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: var(--danger-color);
}

.alert-icon {
  font-size: 18px;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.preview-item {
  position: relative;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: var(--transition-normal);
}

.preview-item:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.remove-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border: 2px solid #ffffff;
  border-radius: 50%;
  background: var(--danger-color);
  color: #ffffff;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-normal);
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
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 4px;
}

.preview-size {
  font-size: 11px;
  color: var(--text-tertiary);
}

.results-section {
  margin-top: 20px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 16px;
}

.summary-item {
  text-align: center;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  transition: var(--transition-normal);
}

.summary-item:hover {
  transform: translateY(-2px);
}

.summary-item.success .summary-value {
  color: var(--success-color);
}

.summary-item.failed .summary-value {
  color: var(--danger-color);
}

.summary-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.summary-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.results-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.results-count {
  font-size: 14px;
  color: var(--text-tertiary);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 16px;
}

.result-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  border: 1px solid var(--border-light);
}

.result-card.failed {
  border-color: #ffccc7;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-light);
}

.result-index {
  font-weight: 600;
  color: var(--text-primary);
}

.result-status {
  font-size: 13px;
  font-weight: 500;
}

.result-status.success {
  color: var(--success-color);
}

.result-status.failed {
  color: var(--danger-color);
}

.result-body {
  padding: 14px 16px;
}

.result-filename {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.result-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
}

.stat {
  font-size: 13px;
  color: var(--text-tertiary);
}

.result-image-wrapper {
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.result-image {
  width: 100%;
  height: auto;
  display: block;
}

.error-message {
  padding: 12px;
  background: #fff2f0;
  border-radius: var(--radius-sm);
  color: var(--danger-color);
  font-size: 13px;
}
</style>
