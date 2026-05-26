"""
摄像头实时检测服务（单例模式）
基于 YOLO 模型，提供线程安全的实时帧检测
"""
import time
import threading
import logging
from typing import Dict, Any, Optional
import numpy as np

from app.services.detect_service import detector

logger = logging.getLogger(__name__)


class CameraDetectionService:
    """摄像头实时检测服务 — 单例模式，全局唯一实例"""

    _instance: Optional['CameraDetectionService'] = None

    # ── 中文类别名映射 ──
    CHINESE_NAMES: Dict[str, str] = {
        "building": "建筑",
        "house": "房屋",
        "car": "汽车",
        "person": "行人",
        "tree": "树木",
        "road": "道路",
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # ── 检测状态 ──
        self._running = False
        self._lock = threading.Lock()

        # ── 统计计数器 ──
        self._frame_count = 0
        self._fps_frame_count = 0
        self._last_fps_time = time.time()
        self._current_fps = 0.0

        # ── 检测配置 ──
        self._confidence_threshold = 0.3
        self._iou_threshold = 0.45
        self._model_image_size = 320       # 降低输入分辨率以提升推理速度

        # ── 并发控制（最多 5 个并发推理请求） ──
        self._max_concurrent_requests = 5
        self._request_semaphore = threading.Semaphore(self._max_concurrent_requests)

        self._initialized = True
        logger.info("CameraDetectionService 单例已初始化")

    # ── 属性 ──────────────────────────────────────

    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._running

    # ── 生命周期管理 ──────────────────────────────

    def start_detection(
        self,
        confidence_threshold: float = 0.3,
        iou_threshold: float = 0.45,
        inference_interval: int = 2,
    ) -> bool:
        """
        启动摄像头检测会话

        Args:
            confidence_threshold: 置信度阈值 (0.0～1.0)
            iou_threshold:        NMS IOU 阈值 (0.0～1.0)
            inference_interval:   推理间隔（预留，前端控制实际频率）
        """
        with self._lock:
            if self._running:
                logger.info("检测已在运行中，将使用新配置重新开始")

            self._confidence_threshold = confidence_threshold
            self._iou_threshold = iou_threshold
            self._frame_count = 0
            self._fps_frame_count = 0
            self._last_fps_time = time.time()
            self._current_fps = 0.0
            self._running = True

            logger.info(
                "摄像头检测已启动 "
                f"(conf={confidence_threshold}, iou={iou_threshold}, "
                f"interval={inference_interval})"
            )
            return True

    def stop_detection(self):
        """停止摄像头检测会话"""
        with self._lock:
            if not self._running:
                return
            self._running = False
            logger.info(
                f"摄像头检测已停止 (共处理 {self._frame_count} 帧)"
            )

    def get_status(self) -> Dict[str, Any]:
        """获取当前检测状态"""
        with self._lock:
            return {
                "is_running": self._running,
                "frame_count": self._frame_count,
                "fps": self._current_fps,
                "confidence_threshold": self._confidence_threshold,
                "iou_threshold": self._iou_threshold,
            }

    # ── 核心推理 ──────────────────────────────────

    def detect_image(self, image: np.ndarray) -> Dict[str, Any]:
        """
        对单帧图像执行目标检测（核心方法）

        Args:
            image: BGR 格式的 numpy 图像数组

        Returns:
            {
                "boxes":         [{x1, y1, x2, y2, confidence, class_id, class_name, chinese_name}, ...],
                "frame_index":   累计帧序号,
                "fps":           实时帧率,
                "detection_time": 本次推理耗时（秒）,
                "total_objects": 检测到的目标数,
            }
        """
        with self._request_semaphore:
            start_time = time.time()

            # 调用 YOLO 模型推理
            results = detector.model.predict(
                source=image,
                conf=self._confidence_threshold,
                iou=self._iou_threshold,
                save=False,
                imgsz=self._model_image_size,
                half=False,
                verbose=False,
                stream=False,
            )

            # 解析检测结果
            boxes = []
            for result in results:
                class_names = result.names if hasattr(result, 'names') else {}
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])

                    class_name = class_names.get(class_id, f"class_{class_id}")
                    chinese_name = self.CHINESE_NAMES.get(class_name, class_name)

                    boxes.append({
                        "x1": round(x1, 2),
                        "y1": round(y1, 2),
                        "x2": round(x2, 2),
                        "y2": round(y2, 2),
                        "confidence": round(confidence, 4),
                        "class_id": class_id,
                        "class_name": class_name,
                        "chinese_name": chinese_name,
                    })

            detection_time = round(time.time() - start_time, 4)

            # 更新统计
            self._frame_count += 1
            self._fps_frame_count += 1
            self._current_fps = self._calculate_fps()

            return {
                "boxes": boxes,
                "frame_index": self._frame_count,
                "fps": self._current_fps,
                "detection_time": detection_time,
                "total_objects": len(boxes),
            }

    # ── 内部方法 ──────────────────────────────────

    def _calculate_fps(self) -> float:
        """实时计算帧率（每秒更新一次）"""
        current_time = time.time()
        elapsed = current_time - self._last_fps_time
        if elapsed >= 1.0:
            fps = self._fps_frame_count / elapsed
            self._fps_frame_count = 0
            self._last_fps_time = current_time
            return round(fps, 2)
        return self._current_fps


# 全局单例（供 API 路由直接导入）
camera_detection_service = CameraDetectionService()
