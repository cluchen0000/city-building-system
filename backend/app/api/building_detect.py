"""
建筑检测 API 路由
"""
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.services.detect_service import get_detector
from app.utils.img_handle import save_upload, ensure_dir
from app.utils.auth import get_current_user
from app.models.database import User, get_db
from app.models.schemas import (
    DetectResponse,
    BatchDetectResponse,
    VideoDetectResponse,
)
from app.api.history import save_detection_history

router = APIRouter(prefix="/api", tags=["建筑检测"])

# 启动时确保目录存在
ensure_dir(settings.UPLOAD_DIR, settings.RESULT_DIR)


@router.post("/detect/single", response_model=DetectResponse)
async def detect_single(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    单图建筑检测

    上传遥感/航拍影像，返回检测到的建筑框和面积统计
    """
    # 校验文件类型
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(400, "仅支持图片文件")

    try:
        # 保存上传文件
        filepath, filename = await save_upload(file, settings.UPLOAD_DIR)

        # 执行检测
        result = get_detector().detect(filepath)

        # 补充图片 URL
        result.image_url = f"/{settings.UPLOAD_DIR}/{filename}"

        # 计算平均置信度
        confidences = [box.confidence for box in result.boxes] if result.boxes else []
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        # 保存历史记录
        save_detection_history(
            db=db,
            user_id=current_user.id,
            detection_type="single",
            image_url=result.image_url,
            result_url=result.result_url,
            building_count=result.total_objects,
            total_area=result.stats.total_area_sqm if result.stats else 0.0,
            confidence_avg=round(avg_conf, 4),
            details={
                "detect_id": result.detect_id,
                "cost_time": result.cost_time,
                "model_name": result.model_name
            }
        )

        return DetectResponse(
            code=200,
            message="检测成功",
            data=result,
        )

    except FileNotFoundError as e:
        raise HTTPException(500, str(e))
    except Exception as e:
        raise HTTPException(500, f"检测失败: {str(e)}")


@router.post("/detect/batch", response_model=BatchDetectResponse)
async def detect_batch(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量建筑检测

    上传多张遥感/航拍影像，返回批量检测结果
    """
    if not files or len(files) == 0:
        raise HTTPException(400, "请至少上传一张图片")

    filepaths = []
    filenames = []
    for file in files:
        if file.content_type and not file.content_type.startswith("image/"):
            raise HTTPException(400, f"文件 {file.filename} 不是有效的图片文件")
        filepath, filename = await save_upload(file, settings.UPLOAD_DIR)
        filepaths.append(filepath)
        filenames.append(filename)

    try:
        results, summary = get_detector().detect_batch(filepaths)

        # 保存历史记录（批量检测保存一条总记录）
        save_detection_history(
            db=db,
            user_id=current_user.id,
            detection_type="batch",
            building_count=summary.total_objects,
            total_area=0.0,
            confidence_avg=0.0,
            details={
                "total_images": summary.total_images,
                "success_count": summary.success_count,
                "failed_count": summary.failed_count,
                "total_cost_time": summary.total_cost_time
            }
        )

        return BatchDetectResponse(
            code=200,
            message="批量检测完成",
            results=results,
            summary=summary,
        )

    except Exception as e:
        raise HTTPException(500, f"批量检测失败: {str(e)}")


@router.post("/detect/video", response_model=VideoDetectResponse)
async def detect_video(
    file: UploadFile = File(...),
    frame_interval: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    视频建筑检测

    上传视频文件，进行抽帧检测
    """
    valid_types = ["video/mp4", "video/avi", "video/mov", "video/webm"]
    if file.content_type and file.content_type not in valid_types:
        raise HTTPException(400, "仅支持 MP4、AVI、MOV、WebM 格式的视频")

    try:
        filepath, filename = await save_upload(file, settings.UPLOAD_DIR)

        frames, video_info, summary = get_detector().detect_video(filepath, frame_interval)

        # 保存历史记录
        save_detection_history(
            db=db,
            user_id=current_user.id,
            detection_type="video",
            image_url=f"/{settings.UPLOAD_DIR}/{filename}",
            building_count=summary.total_objects,
            total_area=0.0,
            confidence_avg=0.0,
            details={
                "duration": video_info.duration,
                "fps": video_info.fps,
                "total_frames": video_info.total_frames,
                "processed_frames": summary.processed_frames,
                "avg_objects_per_frame": summary.avg_objects_per_frame,
                "total_cost_time": summary.total_cost_time
            }
        )

        return VideoDetectResponse(
            code=200,
            message="视频检测完成",
            video_info=video_info,
            summary=summary,
            frames=frames,
        )

    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"视频检测失败: {str(e)}")
