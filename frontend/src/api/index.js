import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000
})

api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const detectAPI = {
  detectSingle: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await api.post('/detect/single', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  },
  
  health: async () => {
    const response = await api.get('/health')
    return response.data
  }
}

export default api
