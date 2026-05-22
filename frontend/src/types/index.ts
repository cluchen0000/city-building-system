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
