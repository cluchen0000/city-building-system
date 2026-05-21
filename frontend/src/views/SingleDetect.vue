<template>
  <div class="space-y-6">
    <div class="card">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">单图建筑检测</h2>
          <p class="text-sm text-gray-500 mt-1">上传遥感或航拍影像，系统将自动检测建筑物并计算面积</p>
        </div>
        <div class="flex items-center space-x-2">
          <span class="flex items-center px-3 py-1 rounded-full text-xs font-medium" :class="isOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
            <span class="w-2 h-2 rounded-full mr-1" :class="isOnline ? 'bg-green-500' : 'bg-red-500'"></span>
            {{ isOnline ? '服务正常' : '服务离线' }}
          </span>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="space-y-4">
          <div 
            class="border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer"
            :class="isDragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'"
            @dragenter.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @dragover.prevent
            @drop.prevent="handleDrop"
            @click="triggerFileInput"
          >
            <input 
              ref="fileInput"
              type="file" 
              accept="image/*" 
              class="hidden" 
              @change="handleFileSelect"
            />
            <div v-if="!selectedImage" class="space-y-3">
              <div class="w-16 h-16 mx-auto rounded-full bg-gray-100 flex items-center justify-center">
                <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
              </div>
              <p class="text-gray-600">点击或拖拽图片到此处上传</p>
              <p class="text-sm text-gray-400">支持 JPG、PNG、WebP 格式</p>
            </div>
            <div v-else class="space-y-3">
              <img :src="selectedImage" class="max-h-48 mx-auto rounded-lg object-contain" />
              <p class="text-gray-600">{{ fileName }}</p>
              <button 
                class="text-sm text-primary-600 hover:text-primary-700 font-medium"
                @click.stop="clearImage"
              >
                重新选择
              </button>
            </div>
          </div>

          <button 
            class="btn-primary w-full"
            :disabled="!selectedImage || isLoading"
            @click="startDetect"
          >
            <span v-if="isLoading" class="flex items-center justify-center space-x-2">
              <span class="w-5 h-5 loading-spinner"></span>
              <span>检测中...</span>
            </span>
            <span v-else>开始检测</span>
          </button>
        </div>

        <div class="space-y-4">
          <div class="p-4 bg-gray-50 rounded-xl">
            <h3 class="text-sm font-medium text-gray-700 mb-3">检测参数</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">置信度阈值</span>
                <span class="text-sm font-medium text-gray-900">0.3</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">IoU 阈值</span>
                <span class="text-sm font-medium text-gray-900">0.45</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">空间分辨率 (GSD)</span>
                <span class="text-sm font-medium text-gray-900">0.3 米/像素</span>
              </div>
            </div>
          </div>

          <div class="p-4 bg-blue-50 rounded-xl">
            <h3 class="text-sm font-medium text-blue-700 mb-2">提示</h3>
            <ul class="text-sm text-blue-600 space-y-1">
              <li>• 建议上传清晰的遥感或航拍影像</li>
              <li>• 图片大小建议不超过 10MB</li>
              <li>• 检测时间取决于图片大小和建筑数量</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div v-if="detectionResult" class="card">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">检测结果</h2>
          <p class="text-sm text-gray-500 mt-1">检测完成，共发现 {{ detectionResult.data.total_objects }} 个建筑物</p>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-sm text-gray-500">耗时: {{ detectionResult.data.cost_time }}s</span>
          <span class="text-sm text-gray-500">|</span>
          <span class="text-sm text-gray-500">模型: {{ detectionResult.data.model_name }}</span>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="space-y-4">
          <div class="aspect-video bg-gray-100 rounded-xl overflow-hidden">
            <img :src="detectionResult.data.result_url" class="w-full h-full object-contain" />
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-gray-500">标注结果图</span>
            <button 
              class="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center space-x-1"
              @click="downloadResult"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
              </svg>
              <span>下载</span>
            </button>
          </div>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div class="p-4 bg-green-50 rounded-xl">
              <p class="text-sm text-green-600">检测到建筑物</p>
              <p class="text-2xl font-bold text-green-700">{{ detectionResult.data.total_objects }} 个</p>
            </div>
            <div class="p-4 bg-blue-50 rounded-xl">
              <p class="text-sm text-blue-600">总面积</p>
              <p class="text-2xl font-bold text-blue-700">{{ detectionResult.data.stats?.total_area_sqm?.toLocaleString() || 0 }} m²</p>
            </div>
            <div class="p-4 bg-purple-50 rounded-xl">
              <p class="text-sm text-purple-600">平均面积</p>
              <p class="text-2xl font-bold text-purple-700">{{ detectionResult.data.stats?.avg_area_sqm?.toFixed(2) || 0 }} m²</p>
            </div>
            <div class="p-4 bg-orange-50 rounded-xl">
              <p class="text-sm text-orange-600">置信度范围</p>
              <p class="text-2xl font-bold text-orange-700">{{ detectionResult.data.stats?.min_conf?.toFixed(2) }} - {{ detectionResult.data.stats?.max_conf?.toFixed(2) }}</p>
            </div>
          </div>

          <div class="max-h-64 overflow-y-auto">
            <h3 class="text-sm font-medium text-gray-700 mb-3">检测框详情</h3>
            <div class="space-y-2">
              <div 
                v-for="(box, index) in detectionResult.data.boxes" 
                :key="index"
                class="p-3 bg-gray-50 rounded-lg text-sm"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="font-medium text-gray-700">建筑物 {{ index + 1 }}</span>
                  <span class="text-xs px-2 py-0.5 rounded-full" :class="getConfidenceClass(box.confidence)">
                    {{ (box.confidence * 100).toFixed(1) }}%
                  </span>
                </div>
                <div class="text-gray-500 space-y-1">
                  <p>位置: ({{ box.x1.toFixed(2) }}, {{ box.y1.toFixed(2) }}) - ({{ box.x2.toFixed(2) }}, {{ box.y2.toFixed(2) }})</p>
                  <p>面积: {{ box.area_sqm?.toFixed(2) || 0 }} m²</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="errorMessage" class="card bg-red-50 border-red-100">
      <div class="flex items-center space-x-3">
        <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
          <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div>
          <p class="font-medium text-red-800">检测失败</p>
          <p class="text-sm text-red-600">{{ errorMessage }}</p>
        </div>
        <button 
          class="ml-auto text-sm text-red-600 hover:text-red-700 font-medium"
          @click="clearError"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { detectAPI } from '../api'

const fileInput = ref(null)
const selectedImage = ref(null)
const fileName = ref('')
const isDragging = ref(false)
const isLoading = ref(false)
const isOnline = ref(false)
const detectionResult = ref(null)
const errorMessage = ref('')

onMounted(() => {
  checkHealth()
})

const checkHealth = async () => {
  try {
    await detectAPI.health()
    isOnline.value = true
  } catch {
    isOnline.value = false
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

const processFile = (file) => {
  fileName.value = file.name
  const reader = new FileReader()
  reader.onload = (e) => {
    selectedImage.value = e.target?.result
    detectionResult.value = null
    errorMessage.value = ''
  }
  reader.readAsDataURL(file)
}

const clearImage = () => {
  selectedImage.value = null
  fileName.value = ''
  detectionResult.value = null
  errorMessage.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const startDetect = async () => {
  if (!fileInput.value?.files?.[0]) return
  
  isLoading.value = true
  errorMessage.value = ''
  detectionResult.value = null
  
  try {
    const file = fileInput.value.files[0]
    const result = await detectAPI.detectSingle(file)
    if (result.code === 200) {
      detectionResult.value = result
    } else {
      errorMessage.value = result.message || '检测失败'
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '网络错误，请检查服务是否运行'
  } finally {
    isLoading.value = false
  }
}

const downloadResult = () => {
  if (!detectionResult.value?.data?.result_url) return
  
  const link = document.createElement('a')
  link.href = detectionResult.value.data.result_url
  link.download = `result_${Date.now()}.jpg`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const getConfidenceClass = (confidence) => {
  if (confidence >= 0.8) return 'bg-green-100 text-green-700'
  if (confidence >= 0.5) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
}

const clearError = () => {
  errorMessage.value = ''
}
</script>
