"""
Pydantic 数据模型 —— API 请求/响应结构
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DetectionBox(BaseModel):
    """单个建筑检测框"""
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_name: str = "building"
    area_pixel: float = 0.0        # 像素面积
    area_sqm: Optional[float] = None  # 实际面积（平方米）


class BuildingStats(BaseModel):
    """建筑统计"""
    total: int = 0
    total_area_sqm: Optional[float] = None
    avg_area_sqm: Optional[float] = None
    min_conf: float = 0.0
    max_conf: float = 0.0


class DetectResult(BaseModel):
    """检测结果"""
    detect_id: str
    image_url: str
    result_url: str
    boxes: List[DetectionBox]
    total_objects: int
    cost_time: float
    model_name: str
    created_at: datetime
    stats: Optional[BuildingStats] = None


class DetectResponse(BaseModel):
    """API 响应"""
    code: int = 200
    message: str = "检测成功"
    data: Optional[DetectResult] = None
