"""
YOLO 建筑检测服务
"""
import os
import time
import uuid
from datetime import datetime
from ultralytics import YOLO

from app.config import settings
from app.utils.img_handle import get_image_size, save_result_image
from app.services.area_calc_service import calc_areas
from app.models.schemas import DetectionBox, BuildingStats, DetectResult


class BuildingDetector:
    """建筑物检测器"""

    def __init__(self):
        self.model = None
        self.model_name = os.path.basename(settings.MODEL_PATH)
        self._load_model()

    def _load_model(self):
        model_path = settings.MODEL_PATH
        # yolo11n.pt 是 COCO 预训练模型，YOLO 会自动从网络下载，不需要本地存在
        if not os.path.exists(model_path) and "yolo11n" not in model_path:
            raise FileNotFoundError(
                f"模型文件不存在: {model_path}\n"
                "请将训练好的 .pt 模型放到 backend/model_file/ 目录"
            )
        self.model = YOLO(model_path)
        print(f"模型已加载: {os.path.basename(model_path)}")

    def detect(self, image_path: str) -> DetectResult:
        """
        单图建筑检测
        返回 DetectResult 包含检测框、面积统计
        """
        t0 = time.time()

        # 图片尺寸
        img_w, img_h = get_image_size(image_path)

        # YOLO 推理
        results = self.model(
            image_path,
            conf=settings.CONFIDENCE,
            iou=settings.IOU,
            save=False,
            verbose=False,
        )

        # 解析检测框
        boxes = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])

                # 像素面积
                pw = (x2 - x1) * img_w
                ph = (y2 - y1) * img_h
                pixel_area = pw * ph

                # 实际面积
                sqm = round(pixel_area * settings.GSD * settings.GSD, 2)

                boxes.append(DetectionBox(
                    x1=round(x1, 2), y1=round(y1, 2),
                    x2=round(x2, 2), y2=round(y2, 2),
                    confidence=round(conf, 4),
                    area_pixel=round(pixel_area, 2),
                    area_sqm=sqm,
                ))

        # 建筑统计
        stats = calc_areas(boxes, settings.GSD) if boxes else None

        # 保存标注图
        annotated = results[0].plot()
        result_path = save_result_image(annotated, settings.RESULT_DIR)
        result_url = f"/{result_path}"

        cost = round(time.time() - t0, 3)
        detect_id = uuid.uuid4().hex[:16]

        return DetectResult(
            detect_id=detect_id,
            image_url="",  # 由路由层补充
            result_url=result_url,
            boxes=boxes,
            total_objects=len(boxes),
            cost_time=cost,
            model_name=self.model_name,
            created_at=datetime.now(),
            stats=stats,
        )


detector = BuildingDetector()
