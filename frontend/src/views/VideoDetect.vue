<template>
  <div class="video-detect">
    <h1>🎬 视频建筑检测</h1>

    <div class="upload-area">
      <label class="upload-btn">
        <input
          type="file"
          accept="video/*"
          @change="onFileChange"
          class="file-input"
        />
        选择视频
      </label>
      <span v-if="selectedVideo" class="file-name">{{ selectedVideo.name }}</span>
      <button
        class="detect-btn"
        @click="detect"
        :disabled="!selectedVideo || loading"
      >
        {{ loading ? '检测中...' : '开始视频检测' }}
      </button>
    </div>

    <div v-if="loading" class="loading-tip">
      ⏳ 正在处理视频，请稍候（视频检测可能需要较长时间）
    </div>

    <div v-if="errorMsg" class="error-tip">{{ errorMsg }}</div>

    <div v-if="selectedVideo && !videoResults.length" class="video-preview">
      <h3>视频预览</h3>
      <video ref="videoRef" controls class="preview-video">
        <source :src="videoUrl" />
      </video>
    </div>

    <div v-if="videoResults.length > 0" class="results-area">
      <h3>视频检测结果</h3>

      <div v-if="videoInfo" class="info-card">
        <h4>视频信息</h4>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">时长</span>
            <span class="info-value">{{ formatDuration(videoInfo.duration) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">帧率</span>
            <span class="info-value">{{ videoInfo.fps }} FPS</span>
          </div>
          <div class="info-item">
            <span class="info-label">总帧数</span>
            <span class="info-value">{{ videoInfo.total_frames }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">抽帧间隔</span>
            <span class="info-value">每 {{ videoInfo.frame_interval }} 帧</span>
          </div>
        </div>
      </div>

      <div v-if="summary" class="summary-card">
        <h4>检测汇总</h4>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-label">处理帧数</span>
            <span class="summary-value">{{ summary.processed_frames }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">总检测目标</span>
            <span class="summary-value highlight">{{ summary.total_objects }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">平均每帧目标</span>
            <span class="summary-value">{{ summary.avg_objects_per_frame.toFixed(2) }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">总耗时</span>
            <span class="summary-value">{{ summary.total_cost_time.toFixed(2) }} 秒</span>
          </div>
        </div>
      </div>

      <div class="frames-header">
        <h4>抽帧检测结果</h4>
        <span class="frame-count">共 {{ videoResults.length }} 帧</span>
      </div>

      <div class="frames-list">
        <div
          v-for="(frame, index) in videoResults"
          :key="index"
          class="frame-card"
        >
          <div class="frame-header">
            <span class="frame-index">第 {{ frame.frame_index }} 帧</span>
            <span class="frame-time">{{ formatDuration(frame.timestamp) }}</span>
          </div>
          <div class="frame-stats">
            <span>检测数: {{ frame.total_objects }}</span>
          </div>
          <div v-if="frame.result_url" class="frame-image">
            <img :src="frame.result_url" class="annotated-img" />
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
  padding: 20px;
}

.video-detect h1 {
  color: #262626;
  margin: 0 0 20px 0;
}

.upload-area {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
}

.upload-btn {
  padding: 10px 20px;
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

.file-name {
  color: #595959;
  font-size: 14px;
}

.detect-btn {
  padding: 10px 24px;
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
  padding: 12px 16px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
}

.error-tip {
  color: #ff4d4f;
  margin: 20px 0;
  padding: 12px 16px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
}

.video-preview h3 {
  margin: 20px 0 12px 0;
  color: #262626;
}

.preview-video {
  max-width: 100%;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: #000;
}

.results-area h3 {
  margin: 24px 0 16px 0;
  color: #262626;
}

.info-card,
.summary-card {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.info-card h4,
.summary-card h4 {
  margin: 0 0 16px 0;
  color: #262626;
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
  padding: 12px;
  background: white;
  border-radius: 6px;
}

.info-label,
.summary-label {
  display: block;
  color: #8c8c8c;
  font-size: 12px;
  margin-bottom: 4px;
}

.info-value,
.summary-value {
  display: block;
  color: #262626;
  font-size: 16px;
  font-weight: 500;
}

.summary-value.highlight {
  color: #1890ff;
  font-size: 20px;
  font-weight: 600;
}

.frames-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0 12px 0;
}

.frames-header h4 {
  margin: 0;
  color: #262626;
}

.frame-count {
  color: #8c8c8c;
  font-size: 13px;
}

.frames-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.frame-card {
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  overflow: hidden;
}

.frame-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.frame-index {
  color: #262626;
  font-weight: 600;
}

.frame-time {
  color: #8c8c8c;
  font-size: 13px;
}

.frame-stats {
  padding: 12px 16px;
  display: flex;
  gap: 20px;
  color: #8c8c8c;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}

.frame-image {
  padding: 12px 16px;
}

.annotated-img {
  max-width: 100%;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}
</style>
