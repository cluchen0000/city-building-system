# 城市建筑检测系统

基于遥感影像的建筑物检测与面积统计系统。

## 功能特性

- **单图检测**: 上传单张遥感影像进行建筑物检测与面积统计
- **建筑物识别**: 使用深度学习模型检测遥感影像中的建筑物
- **面积计算**: 根据像素与地理坐标换算实际建筑面积
- **结果可视化**: 展示检测标注图与面积统计数据

## 技术栈

### 后端
- Python 3.10+
- FastAPI
- PyTorch
- OpenCV
- NumPy

### 前端
- Vue 3 + TypeScript
- Vite
- TailwindCSS / Bootstrap
- Axios

## 项目结构

```
city-building-system/
├── backend/                    # 后端代码
│   ├── app/                    # 应用模块
│   │   ├── api/                # REST API接口
│   │   │   ├── __init__.py
│   │   │   └── building_detect.py    # 单图检测专属接口
│   │   ├── models/             # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── database.py           # 数据库连接
│   │   │   └── schemas.py            # 请求响应数据模型
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── detect_service.py     # 模型推理业务
│   │   │   └── area_calc_service.py  # 建筑面积换算计算
│   │   ├── utils/              # 工具函数
│   │   │   ├── __init__.py
│   │   │   ├── img_handle.py         # 遥感图像预处理
│   │   │   └── geo_calc.py           # 地理像素面积换算工具
│   │   ├── __init__.py
│   │   └── config.py           # 全局路径、参数配置
│   ├── model_file/             # 存放训练完成模型权重
│   │   └── building_best.pt
│   ├── uploads/                # 前端上传单张遥感影像存放
│   ├── detect_result/          # 检测标注图、面积结果存储
│   ├── main.py                 # FastAPI后端启动入口
│   ├── requirements.txt        # 后端依赖清单
│   └── .env                    # 环境变量配置
│
├── frontend/                   # 前端代码
│   ├── public/                 # 静态资源
│   │   ├── favicon.ico
│   │   └── index.html
│   ├── src/                    # 源代码
│   │   ├── api/                # API请求封装
│   │   │   └── detectApi.ts    # 单图检测接口请求
│   │   ├── assets/             # 静态资源
│   │   │   └── css/
│   │   │       └── global.css  # 全局样式
│   │   ├── components/         # Vue组件
│   │   │   ├── ImgUpload.vue   # 单张遥感图上传组件
│   │   │   └── ResultShow.vue  # 检测图+面积数据展示组件
│   │   ├── router/             # 路由配置
│   │   │   └── index.ts
│   │   ├── views/              # 页面视图
│   │   │   └── SingleDetect.vue # 单图检测主页面
│   │   ├── App.vue             # 根组件
│   │   └── main.ts             # 入口文件
│   ├── package.json            # 前端依赖配置
│   ├── vite.config.ts          # Vite配置
│   └── tsconfig.json           # TypeScript配置
│
├── data/                       # 数据处理
│   ├── dataset/               # 遥感建筑物数据集存放
│   ├── train.py               # 模型训练脚本
│   ├── convert_data.py        # 数据集格式转换
│   └── single_predict.py      # 单图统一推理脚本
│
├── deploy/                    # 部署配置
│   ├── start_env.sh           # 环境一键搭建脚本
│   ├── Dockerfile             # Docker镜像构建
│   └── run_doc.md             # 基础部署运行文档
│
├── .gitignore
└── README.md
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+
- PyTorch 2.0+

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

## API接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/detect/single` | POST | 单图检测 |

## 数据流转

```
前端上传 → API调用 → 图像预处理 → 模型推理 → 面积计算 → 结果存储 → 前端展示
```

## 团队分工

| 角色 | 职责 | 负责模块 |
|------|------|----------|
| **前端开发** | Vue界面开发、文件上传、结果展示 | `frontend/` |
| **后端开发** | FastAPI接口、模型推理、业务逻辑 | `backend/app/api/`, `backend/app/services/` |
| **数据处理** | 模型训练、数据集管理 | `data/`, `backend/model_file/` |
| **部署运维** | Docker配置、系统部署 | `deploy/` |

## 许可证

MIT License