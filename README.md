# 🏢 城市建筑检测系统

基于 YOLO11 的遥感影像建筑物检测与面积统计系统，支持单图检测、批量检测、视频检测和实时摄像头检测。

## ✨ 功能特性

- 🖼️ **单图检测**：上传单张遥感/航拍影像，自动检测建筑物并计算面积
- 📦 **批量检测**：同时上传多张图片进行批量处理
- 🎬 **视频检测**：上传视频文件，自动抽帧进行建筑检测
- 📹 **摄像头检测**：调用设备摄像头进行实时建筑识别
- 📜 **历史记录**：自动保存检测历史，支持查看、筛选和删除
- 🔐 **用户认证**：登录/注册功能，支持 JWT 令牌认证

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI 0.104+
- **语言**: Python 3.10+
- **数据库**: SQLite（嵌入式，无需独立服务）
- **AI模型**: YOLO11（Ultralytics）
- **认证**: JWT + Passlib

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite 5
- **路由**: Vue Router
- **样式**: CSS3（响应式设计）

## 📁 项目结构

```
city-building-system/
├── backend/                    # 后端代码
│   ├── app/                    # 应用模块
│   │   ├── api/                # REST API接口
│   │   │   ├── building_detect.py    # 建筑检测接口
│   │   │   ├── camera.py             # 摄像头检测接口
│   │   │   ├── auth.py               # 用户认证接口
│   │   │   ├── users.py              # 用户管理接口
│   │   │   └── history.py            # 历史记录接口
│   │   ├── models/             # 数据模型
│   │   │   ├── database.py           # 数据库表定义
│   │   │   └── schemas.py            # 请求响应数据模型
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── detect_service.py     # YOLO检测服务
│   │   │   └── area_calc_service.py  # 面积计算服务
│   │   ├── utils/              # 工具函数
│   │   ├── config.py           # 配置管理
│   │   └── main.py             # 应用入口
│   ├── model_file/             # YOLO模型权重
│   ├── static/                 # 静态文件（上传/结果）
│   └── requirements.txt        # Python依赖
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   │   ├── SingleDetect.vue      # 单图检测
│   │   │   ├── BatchDetect.vue       # 批量检测
│   │   │   ├── VideoDetect.vue       # 视频检测
│   │   │   ├── CameraDetect.vue      # 摄像头检测
│   │   │   ├── History.vue           # 历史记录
│   │   │   ├── login.vue             # 登录页面
│   │   │   └── register.vue          # 注册页面
│   │   ├── components/         # 通用组件
│   │   ├── api/                # API调用封装
│   │   ├── router/             # 路由配置
│   │   └── types/              # TypeScript类型定义
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── docker-compose.yml          # Docker Compose配置
├── start.bat                   # Windows启动脚本
├── stop.bat                    # Windows停止脚本
└── README.md                   # 项目说明文档
```

## 🚀 快速开始

### 方式一：本地开发模式

#### 1. 环境要求
- Python 3.10+
- Node.js 18+

#### 2. 启动后端
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. 启动前端
```bash
cd frontend
npm install
npm run dev
```

#### 4. 访问应用
- 前端页面：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

### 方式二：Docker部署

#### 1. 构建并启动
```bash
docker-compose up -d --build
```

#### 2. 访问应用
- 前端页面：http://localhost
- 后端API：http://localhost:8000

#### 3. 管理命令
```bash
# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart
```

### 方式三：一键启动（Windows）

```bash
# 启动服务
start.bat

# 停止服务
stop.bat
```

## 📡 API接口

### 认证接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 |
| POST | `/api/auth/login` | 用户登录 |
| GET | `/api/auth/verify` | 验证Token |

### 检测接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/detect/single` | 单图检测 |
| POST | `/api/detect/batch` | 批量检测 |
| POST | `/api/detect/video` | 视频检测 |

### 历史记录接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/history/list` | 获取历史记录 |
| DELETE | `/api/history/{id}` | 删除单条记录 |
| DELETE | `/api/history/` | 清空所有记录 |

## 🗄️ 数据库说明

### 数据库类型
- **SQLite**（嵌入式文件数据库）
- 数据库文件：`backend/app.db`
- 自动创建，无需手动配置

### 数据表

#### users（用户表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String | 用户名（唯一） |
| email | String | 邮箱（唯一） |
| hashed_password | String | 加密密码 |
| created_at | DateTime | 创建时间 |

#### detection_histories（检测历史表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user_id | Integer | 关联用户ID |
| detection_type | String | 检测类型 |
| image_url | String | 原始图片路径 |
| result_url | String | 结果图片路径 |
| building_count | Integer | 建筑数量 |
| total_area | Float | 总面积 |
| confidence_avg | Float | 平均置信度 |
| details | Text | 详细信息 |
| created_at | DateTime | 检测时间 |

## 📝 使用说明

1. **注册账号**：访问首页 → 点击"立即注册" → 填写用户名、邮箱、密码
2. **登录系统**：使用注册的账号登录
3. **选择检测模式**：
   - 单图检测：上传单张图片进行检测
   - 批量检测：上传多张图片批量处理
   - 视频检测：上传视频文件进行抽帧检测
   - 摄像头检测：使用设备摄像头实时检测
4. **查看结果**：检测完成后显示标注图和面积统计
5. **查看历史**：点击导航栏"历史记录"查看检测历史

## 🔧 配置说明

### 后端配置（backend/.env）
```env
# 应用配置
APP_NAME=城市建筑检测系统
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8000
DEBUG=true

# CORS配置
CORS_ORIGINS=["http://localhost:5173"]

# 模型配置
MODEL_PATH=model_file/building_best.pt
CONFIDENCE=0.5
IOU=0.7
GSD=0.1

# 静态文件目录
STATIC_DIR=static
UPLOAD_DIR=static/uploads
RESULT_DIR=static/results
```

## 📁 数据持久化

Docker部署时，以下目录会挂载到宿主机：
- `backend/static/` - 上传文件和检测结果
- `backend/model_file/` - YOLO模型权重
- `backend/app.db` - 数据库文件

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/xxx`)
3. 提交修改 (`git commit -am 'Add feature xxx'`)
4. 推送到分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

## 📄 许可证

MIT License

## 📧 联系方式

如有问题或建议，请提交 Issue 或联系开发者。

---

**🏗️ 项目状态**: 开发完成 | **最后更新**: 2026-05-27