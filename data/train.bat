@echo off
echo 开始训练 YOLO26 遥感建筑物检测模型...
cd D:\Program Files\Git\city-building-system\data
python train.py --model yolo26s.pt --epochs 60 --batch 8 --device cuda --workers 2 --cache False
echo 训练完成！
pause