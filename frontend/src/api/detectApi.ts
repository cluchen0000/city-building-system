import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000,
})

export interface DetectBox {
  x1: number
  y1: number
  x2: number
  y2: number
  confidence: number
  class_name: string
  area_pixel: number
  area_sqm: number | null
}

export interface BuildingStats {
  total: number
  total_area_sqm: number | null
  avg_area_sqm: number | null
  min_conf: number
  max_conf: number
}

export interface DetectResult {
  detect_id: string
  image_url: string
  result_url: string
  boxes: DetectBox[]
  total_objects: number
  cost_time: number
  model_name: string
  created_at: string
  stats: BuildingStats | null
}

export interface DetectResponse {
  code: number
  message: string
  data: DetectResult | null
}

/** 单图建筑检测 */
export async function detectSingle(file: File): Promise<DetectResponse> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<DetectResponse>('/api/detect/single', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
