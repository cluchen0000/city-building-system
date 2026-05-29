<template>
  <div class="camera-detect">
    <h1>📹 摄像头实时检测</h1>

    <div class="camera-container">
      <div class="video-wrapper">
        <div v-if="errorMsg" class="error-tip">{{ errorMsg }}</div>

        <div v-if="!isCameraReady && !isRunning" class="camera-placeholder">
          <div class="placeholder-icon">📷</div>
          <p>点击下方按钮启动摄像头</p>
        </div>

        <div v-show="isCameraReady || isRunning" class="video-canvas-container">
          <video
            ref="videoRef"
            class="video-element"
            autoplay
            playsinline
            muted
          ></video>
          <canvas
            ref="canvasRef"
            class="overlay-canvas"
          ></canvas>
        </div>
      </div>

      <div class="control-panel">
        <div class="control-group">
          <label class="control-label">摄像头设备</label>
          <select v-model="cameraId" class="control-select">
            <option :value="0">默认摄像头</option>
          </select>
        </div>

        <div class="control-group">
          <label class="control-label">置信度阈值</label>
          <input
            type="range"
            v-model.number="confidenceThreshold"
            min="0.1"
            max="1"
            step="0.05"
            class="control-slider"
          />
          <span class="slider-value">{{ confidenceThreshold.toFixed(2) }}</span>
        </div>

        <div class="control-group">
          <label class="control-label">IOU 阈值</label>
          <input
            type="range"
            v-model.number="iouThreshold"
            min="0.1"
            max="1"
            step="0.05"
            class="control-slider"
          />
          <span class="slider-value">{{ iouThreshold.toFixed(2) }}</span>
        </div>

        <div class="control-group">
          <label class="control-label">推理间隔 (帧)</label>
          <input
            type="range"
            v-model.number="inferenceInterval"
            min="1"
            max="10"
            step="1"
            class="control-slider"
          />
          <span class="slider-value">每 {{ inferenceInterval }} 帧</span>
        </div>

        <div class="button-group">
          <button
            v-if="!isRunning"
            class="btn btn-primary"
            :disabled="isCameraStarting"
            @click="startCamera"
          >
            {{ isCameraStarting ? '启动中...' : '🚀 启动检测' }}
          </button>
          <button
            v-else
            class="btn btn-danger"
            @click="stopCamera"
          >
            ⏹ 停止检测
          </button>

          <button
            v-if="isRunning"
            class="btn"
            :class="isPaused ? 'btn-success' : 'btn-warning'"
            @click="togglePause"
          >
            {{ isPaused ? '▶ 继续' : '⏸ 暂停' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="isRunning" class="stats-panel">
      <div class="stat-item">
        <span class="stat-label">帧率 (FPS)</span>
        <span class="stat-value">{{ currentFps.toFixed(1) }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">帧索引</span>
        <span class="stat-value">{{ frameIndex }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">检测耗时</span>
        <span class="stat-value">{{ (detectionTime * 1000).toFixed(0) }} ms</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">检测目标数</span>
        <span class="stat-value">{{ totalObjects }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import {
  detectCameraFrame,
  startCameraDetection,
  stopCameraDetection,
  pauseCameraDetection,
  resumeCameraDetection,
} from '../api/detectApi'
import type { CameraDetectionBox, StartDetectionRequest } from '../types'

const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)

const isCameraReady = ref(false)
const isRunning = ref(false)
const isPaused = ref(false)
const isCameraStarting = ref(false)
const errorMsg = ref('')

const cameraId = ref(0)
const confidenceThreshold = ref(0.5)
const iouThreshold = ref(0.7)
const inferenceInterval = ref(2)

const currentBoxes = ref<CameraDetectionBox[]>([])
const frameIndex = ref(0)
const currentFps = ref(0)
const detectionTime = ref(0)
const totalObjects = ref(0)

let videoStream: MediaStream | null = null
let detectionFrameId: number | null = null
let drawFrameId: number | null = null
let lastDetectionTime = 0
let consecutiveErrorCount = 0

const classColors: Record<string, string> = {
  'building': '#ff4d4f',
  'person': '#1890ff',
  'car': '#52c41a',
  'vehicle': '#faad14',
  'default': '#722ed1',
}

function getBoxColor(className: string): string {
  return classColors[className] || classColors['default']
}

function handleCameraError(error: Error) {
  console.error('摄像头错误:', error)

  const errorName = (error as any).name
  switch (errorName) {
    case 'NotAllowedError':
      errorMsg.value = '摄像头权限被拒绝，请在浏览器设置中允许访问'
      break
    case 'NotFoundError':
      errorMsg.value = '未检测到摄像头设备，请检查设备连接'
      break
    case 'NotReadableError':
      errorMsg.value = '摄像头被其他应用占用，请关闭其他应用后重试'
      break
    default:
      errorMsg.value = `无法访问摄像头: ${error.message}`
  }

  cleanupResources()
  resetState()
}

function handleDetectionError(message: string) {
  consecutiveErrorCount++
  console.warn(`检测错误 (${consecutiveErrorCount}):`, message)

  if (consecutiveErrorCount >= 5) {
    errorMsg.value = `连续检测失败: ${message}`
  }
}

function resetState() {
  isCameraReady.value = false
  isRunning.value = false
  isPaused.value = false
  isCameraStarting.value = false
  currentBoxes.value = []
  frameIndex.value = 0
  currentFps.value = 0
  detectionTime.value = 0
  totalObjects.value = 0
  lastDetectionTime = 0
  consecutiveErrorCount = 0
}

function cleanupResources() {
  if (videoStream) {
    videoStream.getTracks().forEach((track) => track.stop())
    videoStream = null
  }

  if (detectionFrameId) {
    cancelAnimationFrame(detectionFrameId)
    detectionFrameId = null
  }

  if (drawFrameId) {
    cancelAnimationFrame(drawFrameId)
    drawFrameId = null
  }

  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
}

function initCanvas() {
  if (!videoRef.value || !canvasRef.value) return

  const video = videoRef.value
  const canvas = canvasRef.value

  canvas.width = video.videoWidth || 640
  canvas.height = video.videoHeight || 480
}

function drawBoxes() {
  if (!canvasRef.value || !videoRef.value) {
    drawFrameId = requestAnimationFrame(drawBoxes)
    return
  }

  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  const video = videoRef.value

  if (!ctx) {
    drawFrameId = requestAnimationFrame(drawBoxes)
    return
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  const scaleX = canvas.width / (video.videoWidth || canvas.width)
  const scaleY = canvas.height / (video.videoHeight || canvas.height)

  currentBoxes.value.forEach((box) => {
    const x1 = box.x1 * scaleX
    const y1 = box.y1 * scaleY
    const x2 = box.x2 * scaleX
    const y2 = box.y2 * scaleY
    const width = x2 - x1
    const height = y2 - y1

    ctx.strokeStyle = getBoxColor(box.class_name)
    ctx.lineWidth = 2
    ctx.strokeRect(x1, y1, width, height)

    ctx.fillStyle = getBoxColor(box.class_name)
    ctx.globalAlpha = 0.1
    ctx.fillRect(x1, y1, width, height)
    ctx.globalAlpha = 1

    const label = `${box.chinese_name || box.class_name} ${(box.confidence * 100).toFixed(0)}%`
    ctx.font = '12px "Segoe UI", Arial'
    ctx.fillStyle = getBoxColor(box.class_name)
    const labelWidth = ctx.measureText(label).width + 8
    const labelHeight = 16

    if (y1 >= labelHeight) {
      ctx.fillRect(x1, y1 - labelHeight, labelWidth, labelHeight)
      ctx.fillStyle = '#ffffff'
      ctx.fillText(label, x1 + 4, y1 - 4)
    } else {
      ctx.fillRect(x1, y1 + height, labelWidth, labelHeight)
      ctx.fillStyle = '#ffffff'
      ctx.fillText(label, x1 + 4, y1 + height + 12)
    }
  })

  drawFrameId = requestAnimationFrame(drawBoxes)
}

async function sendFrameForDetection() {
  if (!isRunning.value) return

  const currentTime = performance.now()
  const timeSinceLastDetection = currentTime - lastDetectionTime
  const targetInterval = (inferenceInterval.value * 1000) / 30

  if (!videoRef.value) {
    detectionFrameId = requestAnimationFrame(sendFrameForDetection)
    return
  }

  if (!isPaused.value && timeSinceLastDetection >= targetInterval) {
    try {
      const video = videoRef.value
      const captureCanvas = document.createElement('canvas')
      const captureCtx = captureCanvas.getContext('2d')

      if (!captureCtx) {
        throw new Error('无法创建画布上下文')
      }

      captureCanvas.width = video.videoWidth || 640
      captureCanvas.height = video.videoHeight || 480

      captureCtx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height)

      const imageData = captureCanvas.toDataURL('image/jpeg', 0.7)

      const result = await detectCameraFrame(imageData)

      currentBoxes.value = result.boxes || []
      frameIndex.value = result.frame_index || frameIndex.value
      currentFps.value = result.fps || currentFps.value
      detectionTime.value = result.detection_time || 0
      totalObjects.value = result.total_objects || 0
      consecutiveErrorCount = 0
      lastDetectionTime = currentTime

      errorMsg.value = ''
    } catch (err: any) {
      handleDetectionError(err.message || '网络请求失败')
    }
  }

  detectionFrameId = requestAnimationFrame(sendFrameForDetection)
}

async function startCamera() {
  if (isCameraStarting.value || isRunning.value) return

  errorMsg.value = ''
  isCameraStarting.value = true

  try {
    const startParams: StartDetectionRequest = {
      camera_id: cameraId.value,
      confidence_threshold: confidenceThreshold.value,
      iou_threshold: iouThreshold.value,
      inference_interval: inferenceInterval.value,
    }

    const startResult = await startCameraDetection(startParams)
    if (!startResult.success) {
      throw new Error(startResult.message || '启动后端检测服务失败')
    }

    videoStream = await navigator.mediaDevices.getUserMedia({
      video: {
        deviceId: cameraId.value !== 0 ? { exact: `device-id-${cameraId.value}` } : undefined,
        width: { ideal: 640 },
        height: { ideal: 480 },
        frameRate: { ideal: 30 },
      },
      audio: false,
    })

    if (videoRef.value) {
      videoRef.value.srcObject = videoStream
      videoRef.value.onloadedmetadata = () => {
        initCanvas()
        drawFrameId = requestAnimationFrame(drawBoxes)
        detectionFrameId = requestAnimationFrame(sendFrameForDetection)

        isCameraReady.value = true
        isRunning.value = true
        isCameraStarting.value = false
      }
    }
  } catch (err: any) {
    isCameraStarting.value = false
    handleCameraError(err)
  }
}

async function stopCamera() {
  cleanupResources()
  resetState()

  try {
    await stopCameraDetection()
  } catch (err: any) {
    console.warn('停止后端检测服务失败:', err.message)
  }
}

async function togglePause() {
  try {
    if (isPaused.value) {
      await resumeCameraDetection()
    } else {
      await pauseCameraDetection()
    }
    isPaused.value = !isPaused.value
  } catch (err: any) {
    console.warn(`${isPaused.value ? '恢复' : '暂停'}检测失败:`, err.message)
  }
}

onUnmounted(() => {
  cleanupResources()
})
</script>

<style scoped>
.camera-detect {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.camera-detect h1 {
  color: #262626;
  margin: 0 0 20px 0;
}

.camera-container {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
  margin-bottom: 20px;
}

.video-wrapper {
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  min-height: 400px;
}

.camera-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #8c8c8c;
}

.placeholder-icon {
  font-size: 80px;
  margin-bottom: 16px;
}

.camera-placeholder p {
  margin: 0;
  font-size: 16px;
}

.video-canvas-container {
  position: relative;
  width: 100%;
  min-height: 400px;
}

.video-element {
  width: 100%;
  height: auto;
  display: block;
  background: #000;
}

.overlay-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.control-panel {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.control-group {
  margin-bottom: 20px;
}

.control-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 8px;
}

.control-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
  background: #fff;
}

.control-slider {
  width: calc(100% - 60px);
  margin-right: 10px;
}

.slider-value {
  font-size: 14px;
  color: #1890ff;
  font-weight: 500;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 4px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.btn-danger {
  background: linear-gradient(135deg, #ff4d4f 0%, #cf1322 100%);
  color: white;
}

.btn-danger:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 77, 79, 0.3);
}

.btn-warning {
  background: linear-gradient(135deg, #faad14 0%, #d48806 100%);
  color: white;
}

.btn-warning:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(250, 173, 20, 0.3);
}

.btn-success {
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
  color: white;
}

.btn-success:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.3);
}

.stats-panel {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
}

.error-tip {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  color: #ff4d4f;
  padding: 12px 16px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 4px;
  font-size: 14px;
}

@media (max-width: 900px) {
  .camera-container {
    grid-template-columns: 1fr;
  }

  .stats-panel {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
