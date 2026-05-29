"""
摄像头检测 API 路由
"""
import base64
import cv2
import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.services.camera_detection_service import camera_detection_service
from app.utils.auth import get_current_user
from app.models.database import User
from app.models.schemas import (
    CameraDetectResponse,
    CameraDetectionData,
    CameraDetectionBox,
    StartDetectionRequest,
)

router = APIRouter(prefix="/api/camera", tags=["摄像头检测"])


class CameraStatusResponse(BaseModel):
    success: bool = True
    message: str = "获取状态成功"
    data: dict = {}


class SimpleResponse(BaseModel):
    success: bool
    message: str


class DetectFrameRequest(BaseModel):
    image: str


@router.post("/start", response_model=SimpleResponse)
async def start_camera_detection(
    request: StartDetectionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    启动摄像头检测服务
    """
    success = camera_detection_service.start_detection(
        camera_id=request.camera_id,
        confidence_threshold=request.confidence_threshold,
        iou_threshold=request.iou_threshold,
        inference_interval=request.inference_interval,
    )

    if success:
        return SimpleResponse(
            success=True,
            message="摄像头检测服务启动成功",
        )
    else:
        raise HTTPException(500, "启动摄像头检测服务失败")


@router.post("/stop", response_model=SimpleResponse)
async def stop_camera_detection(current_user: User = Depends(get_current_user)):
    """
    停止摄像头检测服务
    """
    camera_detection_service.stop_detection()
    return SimpleResponse(
        success=True,
        message="摄像头检测服务已停止",
    )


@router.post("/pause", response_model=SimpleResponse)
async def pause_camera_detection(current_user: User = Depends(get_current_user)):
    """
    暂停摄像头检测
    """
    camera_detection_service.pause_detection()
    return SimpleResponse(
        success=True,
        message="检测已暂停",
    )


@router.post("/resume", response_model=SimpleResponse)
async def resume_camera_detection(current_user: User = Depends(get_current_user)):
    """
    恢复摄像头检测
    """
    camera_detection_service.resume_detection()
    return SimpleResponse(
        success=True,
        message="检测已恢复",
    )


@router.get("/status", response_model=CameraStatusResponse)
async def get_camera_status(current_user: User = Depends(get_current_user)):
    """
    获取摄像头检测服务当前状态
    """
    return CameraStatusResponse(
        success=True,
        message="获取状态成功",
        data={
            "is_running": camera_detection_service.is_running,
            "status": camera_detection_service.status,
        },
    )


@router.post("/detect", response_model=CameraDetectResponse)
async def detect_frame(
    request: DetectFrameRequest,
    current_user: User = Depends(get_current_user)
):
    """
    接收前端发送的图像并返回检测结果

    请求体：
        image: base64编码的图像数据

    返回：
        检测结果（框坐标、类别、置信度）
    """
    try:
        if not camera_detection_service.is_running:
            return CameraDetectResponse(
                success=False,
                message="摄像头检测未启动，请先调用 /api/camera/start 启动检测",
            )

        image_data = request.image
        if not image_data:
            return CameraDetectResponse(
                success=False,
                message="缺少图像数据",
            )

        if "," in image_data:
            image_data = image_data.split(",")[1]

        try:
            image_bytes = base64.b64decode(image_data)
        except Exception:
            return CameraDetectResponse(
                success=False,
                message="Base64 解码失败",
            )

        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image is None:
            return CameraDetectResponse(
                success=False,
                message="图像解码失败",
            )

        result = camera_detection_service.detect_image(image)

        boxes = [
            CameraDetectionBox(**box)
            for box in result.get("boxes", [])
        ]

        return CameraDetectResponse(
            success=True,
            message="检测成功",
            data=CameraDetectionData(
                boxes=boxes,
                frame_index=result.get("frame_index", 0),
                fps=result.get("fps", 0.0),
                detection_time=result.get("detection_time", 0.0),
                total_objects=result.get("total_objects", 0),
            ),
        )

    except Exception as e:
        print(f"图像检测异常: {str(e)}")
        return CameraDetectResponse(
            success=False,
            message=f"图像检测失败: {str(e)}",
        )
