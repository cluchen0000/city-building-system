"""
建筑面积统计服务
"""
from typing import List
from app.models.schemas import DetectionBox, BuildingStats


def calc_areas(boxes: List[DetectionBox], gsd: float) -> BuildingStats:
    """
    根据检测框列表计算建筑统计

    参数:
        boxes: 检测框列表
        gsd: 空间分辨率（米/像素）

    返回:
        BuildingStats: 总数、总面积、平均面积、置信度范围
    """
    confs = [b.confidence for b in boxes]
    areas = [b.area_sqm for b in boxes if b.area_sqm]

    return BuildingStats(
        total=len(boxes),
        total_area_sqm=round(sum(areas), 2) if areas else None,
        avg_area_sqm=round(sum(areas) / len(areas), 2) if areas else None,
        min_conf=round(min(confs), 4),
        max_conf=round(max(confs), 4),
    )
