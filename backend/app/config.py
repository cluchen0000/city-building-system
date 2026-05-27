"""
城市建筑检测系统 - 配置管理
"""
import os


class Settings:
    # 应用
    APP_NAME = "城市建筑检测系统"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "true").lower() in ("true", "1")

    # 服务器
    HOST = "0.0.0.0"
    PORT = 8000

    # 目录
    STATIC_DIR = "static"
    UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
    RESULT_DIR = os.path.join(STATIC_DIR, "results")
    MODEL_DIR = "model_file"

    # YOLO 模型（优先用自训练模型，没有则用 COCO 预训练）
    _custom_model = os.path.join(MODEL_DIR, "building_best.pt")
    MODEL_PATH = _custom_model if os.path.exists(_custom_model) and os.path.getsize(_custom_model) > 1024 else "yolo11n.pt"
    CONFIDENCE = float(os.getenv("CONFIDENCE", "0.3"))
    IOU = float(os.getenv("IOU", "0.45"))

    # 遥感参数：空间分辨率 GSD（米/像素）
    GSD = float(os.getenv("GSD", "0.3"))

    # CORS
    CORS_ORIGINS = ["*"]

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    
    class Config:
        env_file = ".env"



settings = Settings()
