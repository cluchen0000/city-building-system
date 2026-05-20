"""
建筑检测 API 路由
"""
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.services.detect_service import detector
from app.utils.img_handle import save_upload, ensure_dir
from app.models.schemas import DetectResponse

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
