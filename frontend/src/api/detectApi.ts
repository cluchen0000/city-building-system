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
  DetectionHistory,
  HistoryListResponse,
  HistoryDeleteResponse,
} from '../types'

const API_BASE = ''

function getAuthHeaders(): Headers {
  const token = localStorage.getItem('token')
  const headers = new Headers()
  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  return headers
}

export interface CameraApiResponse {
  success: boolean
  message: string
}

export async function detectSingleImage(file: File): Promise<DetectResult> {
  const formData = new FormData()
  formData.append('file', file)

  const headers = getAuthHeaders()

  const response = await fetch(`${API_BASE}/api/detect/single`, {
    method: 'POST',
    headers,
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

  const headers = getAuthHeaders()

  const response = await fetch(`${API_BASE}/api/detect/batch`, {
    method: 'POST',
    headers,
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

  const headers = getAuthHeaders()

  const response = await fetch(`${API_BASE}/api/detect/video`, {
    method: 'POST',
    headers,
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
  const headers = getAuthHeaders()
  headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE}/api/camera/detect`, {
    method: 'POST',
    headers,
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
  const headers = getAuthHeaders()
  headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE}/api/camera/start`, {
    method: 'POST',
    headers,
    body: JSON.stringify(params),
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}

export async function stopCameraDetection(): Promise<CameraApiResponse> {
  const headers = getAuthHeaders()
  headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE}/api/camera/stop`, {
    method: 'POST',
    headers,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}

export async function pauseCameraDetection(): Promise<CameraApiResponse> {
  const headers = getAuthHeaders()
  headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE}/api/camera/pause`, {
    method: 'POST',
    headers,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}

export async function resumeCameraDetection(): Promise<CameraApiResponse> {
  const headers = getAuthHeaders()
  headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE}/api/camera/resume`, {
    method: 'POST',
    headers,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}

// 历史记录相关API
export interface HistoryListResult {
  histories: DetectionHistory[]
  total: number
}

export async function getHistoryList(
  page: number = 1,
  pageSize: number = 10,
  detectionType?: string,
): Promise<HistoryListResult> {
  const headers = getAuthHeaders()

  let url = `${API_BASE}/api/history/list?page=${page}&page_size=${pageSize}`
  if (detectionType) {
    url += `&detection_type=${detectionType}`
  }

  const response = await fetch(url, {
    method: 'GET',
    headers,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const json: HistoryListResponse = await response.json()

  if (json.code !== 200) {
    throw new Error(json.message || '获取历史记录失败')
  }

  return {
    histories: json.data,
    total: json.total,
  }
}

export async function deleteHistory(historyId: number): Promise<HistoryDeleteResponse> {
  const headers = getAuthHeaders()

  const response = await fetch(`${API_BASE}/api/history/${historyId}`, {
    method: 'DELETE',
    headers,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}

export async function deleteAllHistory(): Promise<HistoryDeleteResponse> {
  const headers = getAuthHeaders()

  const response = await fetch(`${API_BASE}/api/history/`, {
    method: 'DELETE',
    headers,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  return await response.json()
}
