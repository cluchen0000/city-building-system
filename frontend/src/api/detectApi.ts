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
  CameraDetectionData,
  CameraDetectResponse,
  StartDetectionRequest,
} from '../types'

const API_BASE = ''

export interface CameraApiResponse {
  success: boolean
  message: string
}

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

export interface CameraDetectResult {
  data: CameraDetectionData
}

export async function detectCameraFrame(
  imageBase64: string,
): Promise<CameraDetectionData> {
  const response = await fetch(`${API_BASE}/api/camera/detect`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ image: imageBase64 }),
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const json: CameraDetectResponse = await response.json()

  if (!json.success || !json.data) {
    throw new Error(json.message || '摄像头检测失败')
  }

  return json.data
}

export async function startCameraDetection(
  params: StartDetectionRequest,
): Promise<CameraApiResponse> {
  const response = await fetch(`${API_BASE}/api/camera/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}

export async function stopCameraDetection(): Promise<CameraApiResponse> {
  const response = await fetch(`${API_BASE}/api/camera/stop`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}

export async function pauseCameraDetection(): Promise<CameraApiResponse> {
  const response = await fetch(`${API_BASE}/api/camera/pause`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}

export async function resumeCameraDetection(): Promise<CameraApiResponse> {
  const response = await fetch(`${API_BASE}/api/camera/resume`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}
