"""
建筑检测 API 路由
"""
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.services.detect_service import detector
from app.utils.img_handle import save_upload, ensure_dir
from app.models.schemas import (
    DetectResponse,
    BatchDetectResponse,
    VideoDetectResponse,
)

router = APIRouter(prefix="/api", tags=["建筑检测"])

# 启动时确保目录存在
ensure_dir(settings.UPLOAD_DIR, settings.RESULT_DIR)


@router.post("/detect/single", response_model=DetectResponse)
async def detect_single(file: UploadFile = File(...)):
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
        result = detector.detect(filepath)

        # 补充图片 URL
        result.image_url = f"/{settings.UPLOAD_DIR}/{filename}"

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
async def detect_batch(files: list[UploadFile] = File(...)):
    """
    批量建筑检测

    上传多张遥感/航拍影像，返回批量检测结果
    """
    if not files or len(files) == 0:
        raise HTTPException(400, "请至少上传一张图片")

    filepaths = []
    for file in files:
        if file.content_type and not file.content_type.startswith("image/"):
            raise HTTPException(400, f"文件 {file.filename} 不是有效的图片文件")
        filepath, _ = await save_upload(file, settings.UPLOAD_DIR)
        filepaths.append(filepath)

    try:
        results, summary = detector.detect_batch(filepaths)

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
    frame_interval: int = 10
):
    """
    视频建筑检测

    上传视频文件，进行抽帧检测
    """
    valid_types = ["video/mp4", "video/avi", "video/mov", "video/webm"]
    if file.content_type and file.content_type not in valid_types:
        raise HTTPException(400, "仅支持 MP4、AVI、MOV、WebM 格式的视频")

    try:
        filepath, _ = await save_upload(file, settings.UPLOAD_DIR)

        frames, video_info, summary = detector.detect_video(filepath, frame_interval)

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
