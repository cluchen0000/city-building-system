import type {
  DetectResult,
  DetectResponse,
  BatchImageResult,
  BatchSummary,
  BatchDetectResponse,
  VideoFrameResult,
  VideoInfo,
  VideoSummary,
  VideoDetectResponse,
} from '../types'

const API_BASE = ''

export async function detectSingleImage(file: File): Promise<DetectResult> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/api/detect/single`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const json: DetectResponse = await response.json()

  if (json.code !== 200 || !json.data) {
    throw new Error(json.message || '检测失败')
  }

  return json.data
}

export interface BatchDetectResult {
  results: BatchImageResult[]
  summary: BatchSummary
}

export async function detectBatchImages(files: File[]): Promise<BatchDetectResult> {
  const formData = new FormData()
  files.forEach((file) => {
    formData.append('files', file)
  })

  const response = await fetch(`${API_BASE}/api/detect/batch`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const json: BatchDetectResponse = await response.json()

  if (json.code !== 200) {
    throw new Error(json.message || '批量检测失败')
  }

  return {
    results: json.results,
    summary: json.summary,
  }
}

export interface VideoDetectResult {
  frames: VideoFrameResult[]
  videoInfo: VideoInfo
  summary: VideoSummary
}

export async function detectVideo(file: File): Promise<VideoDetectResult> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/api/detect/video`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const json: VideoDetectResponse = await response.json()

  if (json.code !== 200) {
    throw new Error(json.message || '视频检测失败')
  }

  return {
    frames: json.frames,
    videoInfo: json.video_info,
    summary: json.summary,
  }
}
