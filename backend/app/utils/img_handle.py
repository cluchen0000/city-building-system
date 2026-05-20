"""
图片处理工具
"""
import os
import uuid
import cv2
from fastapi import UploadFile


def ensure_dir(*dirs: str):
    """确保目录存在"""
    for d in dirs:
        os.makedirs(d, exist_ok=True)


async def save_upload(file: UploadFile, upload_dir: str) -> tuple:
    """
    保存上传文件，返回 (保存路径, 文件名)
    """
    ensure_dir(upload_dir)
    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    return filepath, filename


def save_result_image(annotated_image, result_dir: str) -> str:
    """
    保存标注后的图片，返回保存路径
    """
    ensure_dir(result_dir)
    filename = f"result_{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(result_dir, filename)
    cv2.imwrite(filepath, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))
    return filepath


def get_image_size(image_path: str) -> tuple:
    """获取图片宽高"""
    img = cv2.imread(image_path)
    if img is None:
        return 0, 0
    return img.shape[1], img.shape[0]
