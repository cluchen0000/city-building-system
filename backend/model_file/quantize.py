from ultralytics import YOLO
from onnxruntime.quantization import quantize_dynamic, QuantType

# 1. 加载原始 .pt 模型
model = YOLO("building_best.pt")

# 2. 导出为 ONNX（使用模型默认的输入尺寸，通常是 640×640）
#    如果你知道训练时的 imgsz 不是 640，请修改下面的 imgsz 参数
model.export(format="onnx", imgsz=640, dynamic=True,opset=17)  # 生成 building_best.onnx

# 3. 动态量化（将 Float32 权重转为 UInt8，适合 CPU）
onnx_model_path = "building_best.onnx"
quantized_model_path = "building_best_quantized.onnx"
quantize_dynamic(
    model_input=onnx_model_path,
    model_output=quantized_model_path,
    per_channel=True,
    weight_type=QuantType.QUInt8
)

print(f"量化完成！量化模型保存为：{quantized_model_path}")