<template>
  <div class="video-detect">
    <div class="page-header">
      <h1>🎬 视频建筑检测</h1>
      <p class="page-description">上传视频文件，自动抽帧进行建筑检测与面积统计</p>
    </div>

    <div class="card upload-card">
      <div class="card-header">
        <h3 class="card-title">📁 上传视频</h3>
      </div>
      <div class="card-body">
        <div class="upload-controls">
          <label class="btn btn-primary">
            <input
              type="file"
              accept="video/*"
              @change="onFileChange"
              class="file-input"
            />
            <span class="btn-icon">📹</span>
            <span>选择视频</span>
          </label>
          <span v-if="selectedVideo" class="file-info">{{ selectedVideo.name }}</span>
          <button
            class="btn btn-success"
            @click="detect"
            :disabled="!selectedVideo || loading"
          >
            <span class="btn-icon">{{ loading ? '⏳' : '🚀' }}</span>
            <span>{{ loading ? '检测中...' : '开始视频检测' }}</span>
          </button>
        </div>

        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner"></div>
          <span class="loading-text">正在处理视频，请稍候...</span>
        </div>

        <div v-if="errorMsg" class="alert alert-error">
          <span class="alert-icon">❌</span>
          <span>{{ errorMsg }}</span>
        </div>

        <div v-if="selectedVideo && !videoResults.length" class="video-preview">
          <h4 class="preview-title">🎥 视频预览</h4>
          <div class="video-wrapper">
            <video ref="videoRef" controls class="preview-video">
              <source :src="videoUrl" />
            </video>
          </div>
        </div>
      </div>
    </div>

    <div v-if="videoResults.length > 0" class="results-section">
      <div class="card info-card">
        <div class="card-header">
          <h3 class="card-title">📋 视频信息</h3>
        </div>
        <div class="card-body">
          <div class="info-grid">
            <div class="info-item">
              <div class="info-icon">⏱️</div>
              <div class="info-value">{{ formatDuration(videoInfo?.duration || 0) }}</div>
              <div class="info-label">时长</div>
            </div>
            <div class="info-item">
              <div class="info-icon">🎞️</div>
              <div class="info-value">{{ videoInfo?.fps || 0 }} FPS</div>
              <div class="info-label">帧率</div>
            </div>
            <div class="info-item">
              <div class="info-icon">📊</div>
              <div class="info-value">{{ videoInfo?.total_frames || 0 }}</div>
              <div class="info-label">总帧数</div>
            </div>
            <div class="info-item">
              <div class="info-icon">🔄</div>
              <div class="info-value">每 {{ videoInfo?.frame_interval || 10 }} 帧</div>
              <div class="info-label">抽帧间隔</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card summary-card">
        <div class="card-header">
          <h3 class="card-title">📊 检测汇总</h3>
        </div>
        <div class="card-body">
          <div class="summary-grid">
            <div class="summary-item">
              <div class="summary-icon">🎬</div>
              <div class="summary-value">{{ summary?.processed_frames || 0 }}</div>
              <div class="summary-label">处理帧数</div>
            </div>
            <div class="summary-item highlight">
              <div class="summary-icon">🏢</div>
              <div class="summary-value">{{ summary?.total_objects || 0 }}</div>
              <div class="summary-label">总检测目标</div>
            </div>
            <div class="summary-item">
              <div class="summary-icon">📈</div>
              <div class="summary-value">{{ (summary?.avg_objects_per_frame || 0).toFixed(2) }}</div>
              <div class="summary-label">平均每帧目标</div>
            </div>
            <div class="summary-item">
              <div class="summary-icon">⏱️</div>
              <div class="summary-value">{{ (summary?.total_cost_time || 0).toFixed(2) }}s</div>
              <div class="summary-label">总耗时</div>
            </div>
          </div>
        </div>
      </div>

      <div class="frames-header">
        <h3>🖼️ 抽帧检测结果</h3>
        <span class="frame-count">共 {{ videoResults.length }} 帧</span>
      </div>

      <div class="frames-grid">
        <div
          v-for="(frame, index) in videoResults"
          :key="index"
          class="frame-card"
        >
          <div class="frame-header">
            <span class="frame-index">第 {{ frame.frame_index }} 帧</span>
            <span class="frame-time">{{ formatDuration(frame.timestamp) }}</span>
          </div>
          <div class="frame-body">
            <div class="frame-stats">
              <span class="stat">检测数: {{ frame.total_objects }}</span>
            </div>
            <div v-if="frame.result_url" class="frame-image-wrapper">
              <img :src="frame.result_url" class="frame-image" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { detectVideo, type VideoDetectResult } from '../api/detectApi'
import type { VideoFrameResult, VideoInfo, VideoSummary } from '../types'

const loading = ref(false)
const errorMsg = ref('')
const selectedVideo = ref<File | null>(null)
const videoUrl = ref('')
const videoResults = ref<VideoFrameResult[]>([])
const videoInfo = ref<VideoInfo | null>(null)
const summary = ref<VideoSummary | null>(null)
const videoRef = ref<HTMLVideoElement | null>(null)
let blobUrl = ''

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    if (blobUrl) {
      URL.revokeObjectURL(blobUrl)
    }
    const file = input.files[0]
    selectedVideo.value = file
    blobUrl = URL.createObjectURL(file)
    videoUrl.value = blobUrl
    videoResults.value = []
    videoInfo.value = null
    summary.value = null
    errorMsg.value = ''
  }
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

async function detect() {
  if (!selectedVideo.value) {
    errorMsg.value = '请先选择视频'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const result: VideoDetectResult = await detectVideo(selectedVideo.value)
    videoResults.value = result.frames
    videoInfo.value = result.videoInfo
    summary.value = result.summary
  } catch (err: any) {
    console.error(err)
    errorMsg.value = `视频检测失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  if (blobUrl) {
    URL.revokeObjectURL(blobUrl)
  }
})
</script>

<style scoped>
.video-detect {
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

.upload-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 20px;
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

.file-info {
  font-size: 14px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  padding: 8px 14px;
  border-radius: var(--radius-sm);
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

.video-preview {
  margin-top: 20px;
}

.preview-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 12px 0;
}

.video-wrapper {
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: #000;
}

.preview-video {
  width: 100%;
  height: auto;
  display: block;
}

.results-section {
  margin-top: 20px;
}

.info-grid,
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.info-item,
.summary-item {
  text-align: center;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  transition: var(--transition-normal);
}

.info-item:hover,
.summary-item:hover {
  transform: translateY(-2px);
}

.summary-item.highlight {
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.08) 0%, rgba(9, 109, 217, 0.08) 100%);
  border: 1px solid rgba(24, 144, 255, 0.2);
}

.summary-item.highlight .summary-value {
  color: var(--primary-color);
}

.info-icon,
.summary-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.info-value,
.summary-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.info-label,
.summary-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.frames-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.frames-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.frame-count {
  font-size: 14px;
  color: var(--text-tertiary);
}

.frames-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.frame-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  border: 1px solid var(--border-light);
}

.frame-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-light);
}

.frame-index {
  font-weight: 600;
  color: var(--text-primary);
}

.frame-time {
  font-size: 13px;
  color: var(--text-tertiary);
}

.frame-body {
  padding: 14px 16px;
}

.frame-stats {
  margin-bottom: 12px;
}

.stat {
  font-size: 13px;
  color: var(--text-tertiary);
}

.frame-image-wrapper {
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.frame-image {
  width: 100%;
  height: auto;
  display: block;
}
</style>
