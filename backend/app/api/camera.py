"""
摄像头实时检测 API 路由

提供以下端点：
- POST /api/camera/start    启动检测会话
- POST /api/camera/stop     停止检测会话
- GET  /api/camera/status   查看检测状态
- POST /api/camera/detect   发送单帧图像进行检测
"""
import base64
import logging

import cv2
import numpy as np
from fastapi import APIRouter, HTTPException

from app.services.camera_detection_service import camera_detection_service
from app.models.schemas import (
    CameraStartRequest,
    CameraStatusResponse,
    CameraDetectResponse,
    CameraDetectData,
    CameraBox,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/camera", tags=["摄像头实时检测"])


@router.post("/start")
async def start_camera_detection(req: CameraStartRequest):
    """
    启动摄像头检测会话

    配置置信度阈值、IOU 阈值等参数，重置帧计数器。
    前端应在打开摄像头前调用。
    """
    try:
        ok = camera_detection_service.start_detection(
            confidence_threshold=req.confidence_threshold,
            iou_threshold=req.iou_threshold,
            inference_interval=req.inference_interval,
        )
        return {
            "success": ok,
            "message": "摄像头检测已启动" if ok else "启动失败",
        }
    except Exception as e:
        logger.error(f"启动摄像头检测失败: {e}")
        raise HTTPException(500, f"启动失败: {str(e)}")


@router.post("/stop")
async def stop_camera_detection():
    """
    停止摄像头检测会话

    前端关闭摄像头时应调用此接口以重置状态。
    """
    try:
        camera_detection_service.stop_detection()
        return {
            "success": True,
            "message": "摄像头检测已停止",
        }
    except Exception as e:
        logger.error(f"停止摄像头检测失败: {e}")
        raise HTTPException(500, f"停止失败: {str(e)}")


@router.get("/status", response_model=CameraStatusResponse)
async def get_camera_status():
    """
    查询当前摄像头检测状态

    返回运行状态、已处理帧数、实时 FPS 等信息。
    """
    try:
        status = camera_detection_service.get_status()
        return CameraStatusResponse(**status)
    except Exception as e:
        logger.error(f"获取摄像头状态失败: {e}")
        raise HTTPException(500, f"获取状态失败: {str(e)}")


@router.post("/detect", response_model=CameraDetectResponse)
async def detect_frame(request: dict):
    """
    摄像头实时检测（核心端点）

    接收前端发送的 Base64 编码图像帧，返回检测到
    的目标框列表（坐标、类别、置信度）及统计信息。

    请求体:
        { "image": "data:image/jpeg;base64,..." }

    响应:
        {
            "success": true,
            "message": "检测成功",
            "data": {
                "boxes": [ { x1, y1, x2, y2, confidence, class_id, class_name, chinese_name }, ... ],
                "frame_index": 123,
                "fps": 25.5,
                "detection_time": 0.032,
                "total_objects": 5
            }
        }
    """
    # ── 1. 检查检测是否已启动 ──
    if not camera_detection_service.is_running:
        return CameraDetectResponse(
            success=False,
            message="摄像头检测未启动，请先调用 /api/camera/start",
            data=None,
        )

    # ── 2. 提取图像数据 ──
    image_data = request.get("image")
    if not image_data:
        return CameraDetectResponse(
            success=False,
            message="缺少图像数据",
            data=None,
        )

    # ── 3. Base64 解码 ──
    try:
        # 剥离 data:image/...;base64, 前缀（如果存在）
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            return CameraDetectResponse(
                success=False,
                message="图像解码失败：无法解析为有效图像",
                data=None,
            )
    except base64.binascii.Error:
        return CameraDetectResponse(
            success=False,
            message="图像解码失败：Base64 格式错误",
            data=None,
        )
    except Exception as e:
        logger.error(f"图像解码异常: {e}")
        return CameraDetectResponse(
            success=False,
            message=f"图像解码失败: {str(e)}",
            data=None,
        )

    # ── 4. 调用检测服务 ──
    try:
        result = camera_detection_service.detect_image(image)

        data = CameraDetectData(
            boxes=[CameraBox(**b) for b in result["boxes"]],
            frame_index=result["frame_index"],
            fps=result["fps"],
            detection_time=result["detection_time"],
            total_objects=result["total_objects"],
        )

        return CameraDetectResponse(
            success=True,
            message="检测成功",
            data=data,
        )
    except Exception as e:
        logger.error(f"图像检测异常: {e}")
        return CameraDetectResponse(
            success=False,
            message=f"图像检测失败: {str(e)}",
            data=None,
        )
