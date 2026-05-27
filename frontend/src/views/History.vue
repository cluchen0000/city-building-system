<template>
  <div class="history-page">
    <div class="page-header">
      <h1 class="page-title">📜 检测历史记录</h1>
      <div class="header-actions">
        <select v-model="filterType" @change="loadHistories" class="filter-select">
          <option value="">全部类型</option>
          <option value="single">单图检测</option>
          <option value="batch">批量检测</option>
          <option value="video">视频检测</option>
          <option value="camera">摄像头检测</option>
        </select>
        <button @click="confirmDeleteAll" class="btn btn-danger">
          <span>🗑️</span>
          <span>清空全部</span>
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="histories.length === 0" class="empty-container">
      <div class="empty-icon">📭</div>
      <p class="empty-text">暂无检测历史记录</p>
      <p class="empty-hint">开始一次检测，记录将自动保存</p>
    </div>

    <div v-else class="history-list">
      <div v-for="history in histories" :key="history.id" class="history-card">
        <div class="card-header">
          <div class="card-type">
            <span class="type-icon">{{ getTypeIcon(history.detection_type) }}</span>
            <span class="type-text">{{ getTypeText(history.detection_type) }}</span>
          </div>
          <div class="card-time">{{ formatDate(history.created_at) }}</div>
        </div>

        <div class="card-body">
          <div v-if="history.image_url" class="card-image">
            <img :src="history.image_url" alt="检测图片" class="preview-img" />
          </div>
          <div v-if="history.result_url" class="card-image">
            <img :src="history.result_url" alt="检测结果" class="preview-img" />
          </div>

          <div class="card-stats">
            <div class="stat-item">
              <span class="stat-label">建筑数量</span>
              <span class="stat-value">{{ history.building_count }}</span>
            </div>
            <div v-if="history.total_area > 0" class="stat-item">
              <span class="stat-label">总面积</span>
              <span class="stat-value">{{ formatArea(history.total_area) }}</span>
            </div>
            <div v-if="history.confidence_avg > 0" class="stat-item">
              <span class="stat-label">平均置信度</span>
              <span class="stat-value">{{ (history.confidence_avg * 100).toFixed(1) }}%</span>
            </div>
          </div>

          <div v-if="history.details" class="card-details">
            <details>
              <summary>查看详细信息</summary>
              <pre>{{ formatDetails(history.details) }}</pre>
            </details>
          </div>
        </div>

        <div class="card-footer">
          <button @click="confirmDelete(history.id)" class="btn-delete">
            <span>🗑️</span>
            <span>删除</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="total > 0 && !loading" class="pagination">
      <button
        @click="changePage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="pagination-btn"
      >
        上一页
      </button>
      <span class="pagination-info">
        第 {{ currentPage }} 页 / 共 {{ totalPages }} 页 (共 {{ total }} 条)
      </span>
      <button
        @click="changePage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="pagination-btn"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getHistoryList, deleteHistory, deleteAllHistory } from '../api/detectApi'
import type { DetectionHistory } from '../types'

const histories = ref<DetectionHistory[]>([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filterType = ref('')

const totalPages = computed(() => {
  return Math.ceil(total.value / pageSize.value)
})

async function loadHistories() {
  loading.value = true
  try {
    const result = await getHistoryList(
      currentPage.value,
      pageSize.value,
      filterType.value || undefined,
    )
    histories.value = result.histories
    total.value = result.total
  } catch (error) {
    console.error('加载历史记录失败:', error)
    alert('加载失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

function changePage(page: number) {
  if (page < 1 || page > totalPages.value) {
    return
  }
  currentPage.value = page
  loadHistories()
}

function confirmDelete(historyId: number) {
  if (confirm('确定要删除这条记录吗？')) {
    handleDelete(historyId)
  }
}

async function handleDelete(historyId: number) {
  try {
    await deleteHistory(historyId)
    alert('删除成功')
    loadHistories()
  } catch (error) {
    console.error('删除失败:', error)
    alert('删除失败，请重试')
  }
}

function confirmDeleteAll() {
  if (confirm('确定要清空全部历史记录吗？此操作不可恢复！')) {
    handleDeleteAll()
  }
}

async function handleDeleteAll() {
  try {
    await deleteAllHistory()
    alert('清空成功')
    currentPage.value = 1
    loadHistories()
  } catch (error) {
    console.error('清空失败:', error)
    alert('清空失败，请重试')
  }
}

function getTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    single: '🖼️',
    batch: '📦',
    video: '🎬',
    camera: '📹',
  }
  return icons[type] || '📋'
}

function getTypeText(type: string): string {
  const texts: Record<string, string> = {
    single: '单图检测',
    batch: '批量检测',
    video: '视频检测',
    camera: '摄像头检测',
  }
  return texts[type] || type
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function formatArea(area: number): string {
  if (area >= 1000000) {
    return (area / 1000000).toFixed(2) + ' km²'
  } else if (area >= 1000) {
    return (area / 1000).toFixed(2) + ' 千㎡'
  }
  return area.toFixed(2) + ' ㎡'
}

function formatDetails(details: string): string {
  try {
    const obj = JSON.parse(details)
    return JSON.stringify(obj, null, 2)
  } catch {
    return details
  }
}

onMounted(() => {
  loadHistories()
})
</script>

<style scoped>
.history-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #262626;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-select {
  padding: 10px 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-select:hover {
  border-color: #1890ff;
}

.filter-select:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-danger {
  background: #ff4d4f;
  color: white;
}

.btn-danger:hover {
  background: #ff7875;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #8c8c8c;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f0f0f0;
  border-top-color: #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  text-align: center;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
  color: #595959;
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: #8c8c8c;
  margin: 0;
}

.history-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.history-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
}

.history-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #f0f2f5 100%);
  border-bottom: 1px solid #e8e8e8;
}

.card-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  font-size: 20px;
}

.type-text {
  font-weight: 600;
  color: #262626;
  font-size: 15px;
}

.card-time {
  font-size: 13px;
  color: #8c8c8c;
}

.card-body {
  padding: 20px;
}

.card-image {
  margin-bottom: 16px;
}

.preview-img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
}

.card-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #1890ff;
}

.card-details {
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

.card-details details {
  cursor: pointer;
}

.card-details summary {
  font-size: 13px;
  color: #595959;
  padding: 8px 0;
}

.card-details pre {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #595959;
  overflow-x: auto;
  margin: 8px 0 0 0;
}

.card-footer {
  padding: 12px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
}

.btn-delete {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #ff4d4f;
  background: white;
  color: #ff4d4f;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-delete:hover {
  background: #fff1f0;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 32px;
  padding: 20px 0;
}

.pagination-btn {
  padding: 10px 20px;
  border: 1px solid #d9d9d9;
  background: white;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #1890ff;
  color: #1890ff;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 14px;
  color: #595959;
}

@media (max-width: 768px) {
  .history-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-title {
    font-size: 22px;
  }

  .history-list {
    grid-template-columns: 1fr;
  }

  .pagination {
    flex-wrap: wrap;
  }
}
</style>
