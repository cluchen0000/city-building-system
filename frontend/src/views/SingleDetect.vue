<template>
  <div class="detect-page">
    <h1>城市建筑检测</h1>
    <p class="subtitle">上传遥感影像，智能识别建筑物并统计面积</p>

    <!-- 上传区 -->
    <div class="upload-section">
      <label class="upload-btn" :class="{ disabled: loading }">
        <input type="file" accept="image/*" @change="onFileChange" :disabled="loading" />
        <span>{{ selectedFile ? selectedFile.name : '选择遥感影像' }}</span>
      </label>
      <button class="detect-btn" :disabled="!selectedFile || loading" @click="doDetect">
        {{ loading ? '检测中...' : '开始检测' }}
      </button>
    </div>

    <!-- 结果区 -->
    <div v-if="result" class="result-section">
      <!-- 图片对比 -->
      <div class="image-compare">
        <div class="image-box">
          <img :src="originalUrl" alt="原图" />
          <span class="label">原图</span>
        </div>
        <div class="image-box">
          <img :src="resultUrl" alt="检测结果" />
          <span class="label">检测结果</span>
        </div>
      </div>

      <!-- 统计面板 -->
      <div v-if="result.stats" class="stats-panel">
        <div class="stat">
          <span class="num">{{ result.stats.total }}</span>
          <span class="unit">栋建筑</span>
        </div>
        <div class="stat">
          <span class="num">{{ result.stats.total_area_sqm?.toLocaleString() || '-' }}</span>
          <span class="unit">总面积 m²</span>
        </div>
        <div class="stat">
          <span class="num">{{ result.stats.avg_area_sqm?.toLocaleString() || '-' }}</span>
          <span class="unit">平均面积 m²</span>
        </div>
        <div class="stat">
          <span class="num">{{ (result.stats.max_conf * 100).toFixed(1) }}%</span>
          <span class="unit">最高置信度</span>
        </div>
      </div>

      <!-- 建筑清单 -->
      <div v-if="result.boxes.length > 0" class="box-list">
        <h3>识别清单</h3>
        <div class="box-item" v-for="(b, i) in result.boxes" :key="i">
          <span class="idx">#{{ i + 1 }}</span>
          <span class="conf">{{ (b.confidence * 100).toFixed(1) }}%</span>
          <span class="area" v-if="b.area_sqm">{{ b.area_sqm.toLocaleString() }} m²</span>
        </div>
      </div>

      <!-- 元信息 -->
      <div class="meta">
        耗时 {{ result.cost_time }}s · 模型 {{ result.model_name }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { detectSingle, type DetectResult } from '../api/detectApi'

const selectedFile = ref<File | null>(null)
const loading = ref(false)
const result = ref<DetectResult | null>(null)
const originalUrl = ref('')
const resultUrl = ref('')

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) {
    selectedFile.value = input.files[0]
    originalUrl.value = URL.createObjectURL(input.files[0])
  }
}

async function doDetect() {
  if (!selectedFile.value) return
  loading.value = true
  result.value = null
  try {
    const res = await detectSingle(selectedFile.value)
    if (res.code === 200 && res.data) {
      result.value = res.data
      resultUrl.value = 'http://localhost:8000' + res.data.result_url
    } else {
      alert(res.message || '检测失败')
    }
  } catch (e: any) {
    alert('请求失败: ' + (e.message || '服务器错误'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.detect-page { max-width: 1000px; margin: 0 auto; padding: 40px; font-family: sans-serif; }
h1 { font-size: 26px; margin-bottom: 6px; }
.subtitle { color: #888; margin-bottom: 32px; }

.upload-section { display: flex; gap: 16px; margin-bottom: 32px; }
.upload-btn { position: relative; flex: 1; padding: 14px 20px; border: 2px dashed #ccc; border-radius: 10px; text-align: center; cursor: pointer; overflow: hidden; color: #666; }
.upload-btn:hover { border-color: #27ae60; color: #27ae60; }
.upload-btn input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
.upload-btn.disabled { opacity: 0.5; pointer-events: none; }
.detect-btn { padding: 14px 32px; background: #27ae60; color: #fff; border: none; border-radius: 10px; font-size: 15px; cursor: pointer; }
.detect-btn:disabled { background: #ccc; cursor: not-allowed; }

.result-section { display: flex; flex-direction: column; gap: 24px; }
.image-compare { display: flex; gap: 16px; }
.image-box { flex: 1; position: relative; border-radius: 10px; overflow: hidden; background: #f5f5f5; }
.image-box img { width: 100%; max-height: 400px; object-fit: contain; display: block; }
.image-box .label { position: absolute; bottom: 0; left: 0; right: 0; padding: 8px; background: rgba(0,0,0,.5); color: #fff; font-size: 13px; }

.stats-panel { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.stat { background: #f0fdf4; border-radius: 10px; padding: 18px; text-align: center; }
.stat .num { display: block; font-size: 22px; font-weight: 700; color: #27ae60; }
.stat .unit { font-size: 12px; color: #888; margin-top: 4px; }

.box-list { background: #fff; border-radius: 10px; padding: 20px; border: 1px solid #eee; }
.box-list h3 { font-size: 16px; margin-bottom: 12px; }
.box-item { display: flex; align-items: center; gap: 16px; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
.box-item:last-child { border-bottom: none; }
.idx { color: #999; font-size: 13px; width: 40px; }
.conf { font-weight: 600; color: #27ae60; }
.area { color: #666; font-size: 14px; }

.meta { text-align: center; color: #aaa; font-size: 13px; }
</style>
