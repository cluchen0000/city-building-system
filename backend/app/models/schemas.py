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


class BatchImageResult(BaseModel):
    """批量检测中单张图片的结果"""
    filename: str
    success: bool
    total_objects: int = 0
    cost_time: float = 0.0
    result_url: Optional[str] = None
    error: Optional[str] = None


class BatchSummary(BaseModel):
    """批量检测汇总"""
    total_images: int
    success_count: int
    failed_count: int
    total_objects: int
    total_cost_time: float


class BatchDetectResponse(BaseModel):
    """批量检测 API 响应"""
    code: int = 200
    message: str = "批量检测完成"
    results: List[BatchImageResult]
    summary: BatchSummary


class VideoFrameResult(BaseModel):
    """视频单帧检测结果"""
    frame_index: int
    timestamp: float
    total_objects: int
    result_url: Optional[str] = None


class VideoInfo(BaseModel):
    """视频信息"""
    duration: float
    fps: float
    total_frames: int
    frame_interval: int


class VideoSummary(BaseModel):
    """视频检测汇总"""
    processed_frames: int
    total_objects: int
    avg_objects_per_frame: float
    total_cost_time: float


class VideoDetectResponse(BaseModel):
    """视频检测 API 响应"""
    code: int = 200
    message: str = "视频检测完成"
    video_info: VideoInfo
    summary: VideoSummary
    frames: List[VideoFrameResult]
