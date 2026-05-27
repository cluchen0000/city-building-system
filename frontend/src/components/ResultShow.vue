<template>
  <div v-if="result" class="result-show">
    <h3>检测结果</h3>
    
    <div class="stats-card">
      <div class="stat-item">
        <span class="stat-label">检测框数量</span>
        <span class="stat-value">{{ result.total_objects }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">耗时</span>
        <span class="stat-value">{{ result.cost_time }} 秒</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">使用模型</span>
        <span class="stat-value">{{ result.model_name }}</span>
      </div>
    </div>

    <div v-if="result.stats" class="area-stats">
      <h4>面积统计</h4>
      <div class="stat-item">
        <span class="stat-label">总建筑面积</span>
        <span class="stat-value highlight">{{ result.stats.total_area_sqm }} 平方米</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">平均面积</span>
        <span class="stat-value">{{ result.stats.avg_area_sqm }} 平方米</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">置信度范围</span>
        <span class="stat-value">{{ (result.stats.min_conf * 100).toFixed(1) }}% ~ {{ (result.stats.max_conf * 100).toFixed(1) }}%</span>
      </div>
    </div>

    <div v-if="result.result_url" class="result-image">
      <h4>结果标注图</h4>
      <img :src="result.result_url" class="annotated-img" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DetectResult } from '../types'

defineProps<{
  result: DetectResult | null
}>()
</script>

<style scoped>
.result-show {
  margin-top: 24px;
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
}

.result-show h3 {
  margin: 0 0 16px 0;
  color: #262626;
}

.result-show h4 {
  margin: 16px 0 12px 0;
  color: #595959;
  font-size: 14px;
}

.stats-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 6px;
  margin-bottom: 16px;
}

.area-stats {
  background: white;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  color: #8c8c8c;
  font-size: 12px;
}

.stat-value {
  color: #262626;
  font-size: 16px;
  font-weight: 500;
}

.stat-value.highlight {
  color: #1890ff;
  font-size: 18px;
  font-weight: 600;
}

.result-image {
  margin-top: 16px;
}

.annotated-img {
  max-width: 100%;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}
</style>
