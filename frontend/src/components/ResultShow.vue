<template>
  <div v-if="result" class="result-show card">
    <div class="card-header">
      <h3 class="card-title">✅ 检测结果</h3>
      <span class="result-badge">成功</span>
    </div>
    <div class="card-body">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <div class="stat-value">{{ result.total_objects }}</div>
            <div class="stat-label">检测框数量</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⏱️</div>
          <div class="stat-content">
            <div class="stat-value">{{ result.cost_time }}<span class="stat-unit">秒</span></div>
            <div class="stat-label">检测耗时</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🤖</div>
          <div class="stat-content">
            <div class="stat-value">{{ result.model_name }}</div>
            <div class="stat-label">使用模型</div>
          </div>
        </div>
      </div>

      <div v-if="result.stats" class="area-section">
        <h4 class="section-title">📏 面积统计</h4>
        <div class="area-grid">
          <div class="area-item highlight">
            <div class="area-label">总建筑面积</div>
            <div class="area-value">{{ result.stats.total_area_sqm }}<span class="area-unit">m²</span></div>
          </div>
          <div class="area-item">
            <div class="area-label">平均面积</div>
            <div class="area-value">{{ result.stats.avg_area_sqm }}<span class="area-unit">m²</span></div>
          </div>
          <div class="area-item">
            <div class="area-label">置信度范围</div>
            <div class="area-value">{{ (result.stats.min_conf * 100).toFixed(1) }}% ~ {{ (result.stats.max_conf * 100).toFixed(1) }}%</div>
          </div>
        </div>
      </div>

      <div v-if="result.result_url" class="image-section">
        <h4 class="section-title">🖼️ 结果标注图</h4>
        <div class="image-wrapper">
          <img :src="result.result_url" class="result-image" />
          <div class="image-overlay">
            <span class="overlay-text">检测完成</span>
          </div>
        </div>
      </div>
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
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-secondary);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.result-badge {
  background: linear-gradient(135deg, var(--success-color) 0%, var(--success-dark) 100%);
  color: #ffffff;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.card-body {
  padding: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  transition: var(--transition-normal);
}

.stat-card:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
}

.stat-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.1) 0%, rgba(9, 109, 217, 0.1) 100%);
  border-radius: var(--radius-sm);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-unit {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-tertiary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.area-section {
  background: var(--bg-secondary);
  padding: 18px;
  border-radius: var(--radius-md);
  margin-bottom: 24px;
}

.area-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 16px;
}

.area-item {
  text-align: center;
  padding: 14px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
}

.area-item.highlight {
  background: linear-gradient(135deg, rgba(24, 144, 255, 0.08) 0%, rgba(9, 109, 217, 0.08) 100%);
  border: 1px solid rgba(24, 144, 255, 0.2);
}

.area-label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 6px;
}

.area-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 3px;
}

.area-item.highlight .area-value {
  color: var(--primary-color);
  font-size: 22px;
}

.area-unit {
  font-size: 12px;
  font-weight: 400;
  color: var(--text-tertiary);
}

.image-section {
  margin-top: 16px;
}

.image-wrapper {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.result-image {
  display: block;
  max-width: 100%;
  height: auto;
}

.image-overlay {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.6);
  color: #ffffff;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
}

.overlay-text {
  display: flex;
  align-items: center;
  gap: 6px;
}

.overlay-text::before {
  content: '✓';
  color: var(--success-color);
}
</style>
