# 城市建筑检测系统

基于遥感影像的建筑物检测与面积统计系统。

## 功能特性

- **单图检测**: 上传单张遥感影像进行建筑物检测
- **多图检测**: 批量上传多张遥感影像进行检测
- **摄像头检测**: 使用摄像头实时拍照检测
- **视频检测**: 上传视频文件进行帧级检测

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- OpenCV
- NumPy

### 前端
- Vue 3
- Bootstrap 5
- Axios

## 项目结构

```
city-building-system/
├── backend/                 # 后端代码
│   ├── app/                 # 应用模块
│   │   ├── __init__.py
│   │   ├── config.py        # 配置管理
│   │   └── detector.py      # 建筑检测核心逻辑
│   ├── main.py              # FastAPI入口
│   └── requirements.txt     # 依赖列表
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── main.js          # Vue入口
│   │   └── App.vue          # 主应用组件
│   ├── index.html           # HTML模板
│   └── package.json         # 前端依赖
├── data/                    # 数据目录
│   ├── model_config.yaml    # 模型配置
│   └── test_data/           # 测试数据
├── deploy/                  # 部署配置
│   ├── Dockerfile.backend   # 后端Dockerfile
│   └── Dockerfile.frontend  # 前端Dockerfile
├── docker-compose.yml       # Docker Compose配置
└── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+
- Docker (可选)

### 后端运行

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 前端运行

```bash
cd frontend
npm install
npm run dev
```

### Docker部署

```bash
docker-compose up -d
```

## API接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/detect/single` | POST | 单图检测 |
| `/api/detect/multiple` | POST | 多图检测 |
| `/api/detect/video` | POST | 视频检测 |
| `/api/stats` | GET | 获取统计信息 |

## 团队分工

- **前端开发**: 负责Vue界面开发、文件上传、结果展示
- **后端开发**: 负责FastAPI接口、建筑检测算法
- **数据处理**: 负责模型配置、测试数据管理
- **部署运维**: 负责Docker配置、系统部署

## 许可证

MIT License