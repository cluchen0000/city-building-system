# 数据目录说明

## 目录结构

```
data/
├── sample_images/          # 示例遥感影像
├── annotations/            # 标注数据（可选）
└── processed/              # 处理后的数据（可选）
```

## 数据格式

### 示例图片
- 支持格式: JPG, PNG, WebP
- 建议大小: 不超过 10MB
- 建议分辨率: 1024x1024 或更高

### 标注数据（预留）
- 格式: COCO 格式 JSON
- 包含: bounding box, 类别信息

## 数据来源
- 遥感影像可从以下平台获取:
  - Google Earth
  - Sentinel Hub
  - USGS Earth Explorer
  - 天地图

## 注意事项
1. 确保上传的图片包含清晰的建筑物特征
2. 建议使用正射影像以获得最佳检测效果
3. 图片应具有足够的分辨率（建议 GSD <= 1 米）
