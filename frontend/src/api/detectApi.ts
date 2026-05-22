import type { DetectResult, DetectResponse } from '../types'

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
