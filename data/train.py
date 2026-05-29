"""
YOLO 遥感建筑物检测模型训练脚本
"""
import os
import subprocess
import argparse


def train_yolo(epochs=100, batch=8, model="yolo11n.pt", device="", workers=0, cache=False):
    """
    训练 YOLO 模型
    
    参数:
        epochs: 训练轮数，默认100
        batch: 批次大小，默认8
        model: 预训练模型，默认yolo11n.pt
        device: 训练设备，默认自动检测（GPU优先）
        workers: 数据加载线程数，默认0（单进程）
        cache: 是否缓存数据，默认False
    """
    # 数据配置文件路径
    data_yaml = os.path.join(os.path.dirname(__file__), "dataset", "data.yaml")
    
    # 输出目录
    output_dir = os.path.join(os.path.dirname(__file__), "runs")
    
    # 构建训练命令
    cmd = [
        "yolo",
        "train",
        f"data={data_yaml}",
        f"model={model}",
        f"epochs={epochs}",
        f"batch={batch}",
        f"project={output_dir}",
        "name=building_detection",
        "exist_ok=True",
        "save=True",
        "save_period=5",
        "val=True",
        f"cache={cache}",
        f"workers={workers}",
        "patience=10",
    ]
    
    if device:
        cmd.append(f"device={device}")
    
    print(f"训练命令: {' '.join(cmd)}")
    print(f"数据配置: {data_yaml}")
    print(f"输出目录: {output_dir}")
    print(f"训练轮数: {epochs}")
    print(f"批次大小: {batch}")
    print(f"数据加载线程: {workers}")
    print(f"缓存数据: {cache}")
    print("=" * 50)
    
    # 执行训练
    try:
        subprocess.run(cmd, check=True)
        print("\n训练完成！")
        print(f"训练结果保存在: {output_dir}/building_detection")
    except subprocess.CalledProcessError as e:
        print(f"训练失败: {e}")
        exit(1)


def main():
    parser = argparse.ArgumentParser(description="YOLO 遥感建筑物检测训练脚本")
    parser.add_argument("--epochs", type=int, default=100, help="训练轮数")
    parser.add_argument("--batch", type=int, default=8, help="批次大小")
    parser.add_argument("--model", type=str, default="yolo11n.pt", help="预训练模型")
    parser.add_argument("--device", type=str, default="", help="训练设备 (cpu/cuda)")
    parser.add_argument("--workers", type=int, default=0, help="数据加载线程数")
    parser.add_argument("--cache", type=str, default="False", help="是否缓存数据 (True/False)")
    
    args = parser.parse_args()
    
    # 转换为布尔值
    cache_bool = args.cache.lower() == "true"
    
    train_yolo(
        epochs=args.epochs,
        batch=args.batch,
        model=args.model,
        device=args.device,
        workers=args.workers,
        cache=cache_bool
    )


if __name__ == "__main__":
    main()