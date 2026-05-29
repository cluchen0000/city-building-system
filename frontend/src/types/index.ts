export interface DetectionBox {
  x1: number
  y1: number
  x2: number
  y2: number
  confidence: number
  class_name: string
  area_pixel: number
  area_sqm?: number
}

export interface BuildingStats {
  total: number
  total_area_sqm?: number
  avg_area_sqm?: number
  min_conf: number
  max_conf: number
}

export interface DetectResult {
  detect_id: string
  image_url: string
  result_url: string
  boxes: DetectionBox[]
  total_objects: number
  cost_time: number
  model_name: string
  created_at: string
  stats?: BuildingStats
}

export interface DetectResponse {
  code: number
  message: string
  data?: DetectResult
}

export interface BatchImageResult {
  filename: string
  success: boolean
  total_objects: number
  cost_time: number
  result_url?: string
  error?: string
}

export interface BatchSummary {
  total_images: number
  success_count: number
  failed_count: number
  total_objects: number
  total_cost_time: number
}

export interface BatchDetectResponse {
  code: number
  message: string
  results: BatchImageResult[]
  summary: BatchSummary
}

export interface VideoFrameResult {
  frame_index: number
  timestamp: number
  total_objects: number
  result_url?: string
}

export interface VideoInfo {
  duration: number
  fps: number
  total_frames: number
  frame_interval: number
}

export interface VideoSummary {
  processed_frames: number
  total_objects: number
  avg_objects_per_frame: number
  total_cost_time: number
}

export interface VideoDetectResponse {
  code: number
  message: string
  video_info: VideoInfo
  summary: VideoSummary
  frames: VideoFrameResult[]
}

export interface CameraDetectionBox {
  x1: number
  y1: number
  x2: number
  y2: number
  confidence: number
  class_id: number
  class_name: string
  chinese_name: string
}

export interface CameraDetectionData {
  boxes: CameraDetectionBox[]
  frame_index: number
  fps: number
  detection_time: number
  total_objects: number
}

export interface CameraDetectResponse {
  success: boolean
  message: string
  data?: CameraDetectionData
}

export interface StartDetectionRequest {
  camera_id: number
  confidence_threshold: number
  iou_threshold: number
  inference_interval: number
}

// 历史记录相关类型
export interface DetectionHistory {
  id: number
  user_id: number
  detection_type: string
  image_url?: string
  result_url?: string
  building_count: number
  total_area: number
  confidence_avg: number
  details?: string
  created_at: string
}

export interface HistoryListResponse {
  code: number
  message: string
  total: number
  data: DetectionHistory[]
}

export interface HistoryDeleteResponse {
  code: number
  message: string
}
