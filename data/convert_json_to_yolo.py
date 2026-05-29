"""
JSON 标注转 YOLO TXT 格式脚本
支持 COCO 格式和自定义 JSON 格式
"""
import os
import json
import argparse
from pathlib import Path


def convert_coco_format(json_path: str, output_dir: str, image_dir: str):
    """
    转换 COCO 格式的 JSON 标注
    
    COCO 格式示例:
    {
        "images": [{"id": 1, "file_name": "image.jpg", "width": 640, "height": 480}],
        "annotations": [{"image_id": 1, "category_id": 0, "bbox": [x, y, w, h]}]
    }
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    images = {img['id']: img for img in data['images']}
    annotations = {}
    
    for ann in data['annotations']:
        image_id = ann['image_id']
        if image_id not in annotations:
            annotations[image_id] = []
        annotations[image_id].append(ann)
    
    os.makedirs(output_dir, exist_ok=True)
    converted_count = 0
    
    for image_id, img_info in images.items():
        img_name = img_info['file_name']
        img_width = img_info['width']
        img_height = img_info['height']
        
        txt_name = os.path.splitext(img_name)[0] + '.txt'
        txt_path = os.path.join(output_dir, txt_name)
        
        lines = []
        if image_id in annotations:
            for ann in annotations[image_id]:
                category_id = ann['category_id']
                bbox = ann['bbox']
                x, y, w, h = bbox
                
                x_center = (x + w / 2) / img_width
                y_center = (y + h / 2) / img_height
                width = w / img_width
                height = h / img_height
                
                lines.append(f"{category_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
        
        with open(txt_path, 'w') as f:
            f.write('\n'.join(lines))
        
        converted_count += 1
    
    print(f"COCO 格式: 已转换 {converted_count} 个标注文件")


def convert_custom_format(json_path: str, output_dir: str, image_dir: str):
    """
    转换自定义格式的 JSON 标注
    
    自定义格式示例:
    [
        {
            "image_path": "image.jpg",
            "width": 640,
            "height": 480,
            "annotations": [
                {"label": "building", "bbox": [x1, y1, x2, y2]}
            ]
        }
    ]
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    converted_count = 0
    
    for item in data:
        if isinstance(item, dict):
            img_name = item.get('image_path', item.get('file_name', ''))
            if not img_name:
                continue
            
            img_width = item.get('width', 640)
            img_height = item.get('height', 480)
            annotations = item.get('annotations', [])
            
            txt_name = os.path.splitext(os.path.basename(img_name))[0] + '.txt'
            txt_path = os.path.join(output_dir, txt_name)
            
            lines = []
            for ann in annotations:
                category_id = 0  # 强制使用类别ID 0（建筑物）
                
                bbox = ann.get('bbox', [])
                if len(bbox) == 4:
                    if bbox[2] > 1 and bbox[3] > 1:
                        x1, y1, w, h = bbox
                        x2 = x1 + w
                        y2 = y1 + h
                    else:
                        x1, y1, x2, y2 = bbox
                        w = x2 - x1
                        h = y2 - y1
                    
                    x_center = (x1 + w / 2) / img_width
                    y_center = (y1 + h / 2) / img_height
                    width = w / img_width
                    height = h / img_height
                    
                    lines.append(f"{category_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
            
            with open(txt_path, 'w') as f:
                f.write('\n'.join(lines))
            
            converted_count += 1
    
    print(f"自定义格式: 已转换 {converted_count} 个标注文件")


def auto_detect_format(json_path: str) -> str:
    """自动检测 JSON 格式"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and 'images' in data and 'annotations' in data:
        return 'coco'
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        return 'custom'
    return 'custom'


def main():
    parser = argparse.ArgumentParser(description="JSON 标注转 YOLO TXT 格式")
    parser.add_argument("--json", required=True, help="JSON 标注文件路径")
    parser.add_argument("--output", required=True, help="输出 TXT 目录")
    parser.add_argument("--images", help="图片目录（用于获取图片尺寸）")
    parser.add_argument("--format", choices=['coco', 'custom'], help="标注格式")
    
    args = parser.parse_args()
    
    json_path = args.json
    output_dir = args.output
    image_dir = args.images
    
    if not os.path.exists(json_path):
        print(f"错误: JSON 文件不存在 - {json_path}")
        return
    
    if args.format:
        fmt = args.format
    else:
        fmt = auto_detect_format(json_path)
        print(f"自动检测格式: {fmt}")
    
    if fmt == 'coco':
        convert_coco_format(json_path, output_dir, image_dir)
    else:
        convert_custom_format(json_path, output_dir, image_dir)
    
    print(f"转换完成！TXT 文件保存在: {output_dir}")


if __name__ == "__main__":
    main()
