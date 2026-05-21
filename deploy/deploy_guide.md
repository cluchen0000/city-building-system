# 部署指南

## 环境要求

- Docker >= 20.10
- Docker Compose >= 2.0
- Python >= 3.11 (开发模式)
- Node.js >= 20 (开发模式)

## 快速启动

### 方式一：使用 Docker Compose（推荐）

```bash
# 进入项目目录
cd city-building-system

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务启动后:
- 前端: http://localhost
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 方式二：开发模式运行

#### 后端
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### 前端
```bash
cd frontend
npm install
npm run dev
```

## 配置说明

### 环境变量

后端配置文件: `backend/.env`

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DEBUG | 调试模式 | true |
| PORT | 服务端口 | 8000 |
| CONFIDENCE | 置信度阈值 | 0.3 |
| IOU | IoU 阈值 | 0.45 |
| GSD | 空间分辨率(米/像素) | 0.3 |

### 模型配置

- 模型文件位置: `backend/model_file/building_best.pt`
- 如果自定义模型不存在，将自动使用 YOLO11n 预训练模型

## 部署架构

```
┌─────────────────────────────────────────────────────┐
│                    Nginx (Frontend)                │
│                     Port: 80                       │
└───────────────────────────┬─────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────┐
│                    FastAPI (Backend)               │
│                   Port: 8000                       │
│  ┌─────────────────────────────────────────────┐   │
│  │           YOLO11 Building Detector          │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────┐
│              Static Files (uploads/results)         │
└─────────────────────────────────────────────────────┘
```

## 性能优化建议

1. **模型选择**: 生产环境建议使用自定义训练的建筑检测模型
2. **图片大小限制**: 限制上传图片大小，建议 <= 10MB
3. **异步处理**: 对于大型图片，考虑使用异步任务队列
4. **缓存策略**: 可添加 Redis 缓存检测结果
