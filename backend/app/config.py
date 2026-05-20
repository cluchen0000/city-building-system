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

    # YOLO 模型
    MODEL_PATH = os.path.join(MODEL_DIR, "building_best.pt")
    CONFIDENCE = float(os.getenv("CONFIDENCE", "0.3"))
    IOU = float(os.getenv("IOU", "0.45"))

    # 遥感参数：空间分辨率 GSD（米/像素）
    GSD = float(os.getenv("GSD", "0.3"))

    # CORS
    CORS_ORIGINS = ["*"]


settings = Settings()
