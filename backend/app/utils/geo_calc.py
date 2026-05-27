"""
地理计算工具 —— 像素面积转实际面积
"""


def pixel_to_real_area(pixel_w: float, pixel_h: float, gsd: float) -> float:
    """
    像素面积 → 实际面积（平方米）
    gsd: 空间分辨率（米/像素）
    """
    w_m = pixel_w * gsd
    h_m = pixel_h * gsd
    return round(w_m * h_m, 2)


def calculate_gsd_from_altitude(altitude_m: float, focal_length_mm: float,
                                  sensor_width_mm: float, image_width_px: int) -> float:
    """
    根据飞行参数计算 GSD（可选，用于已知飞行高度时）
    """
    return (altitude_m * sensor_width_mm) / (focal_length_mm * image_width_px)
