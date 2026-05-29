from ultralytics import YOLO
import time
import onnxruntime as ort
# 在加载模型前设置
ort.set_default_logger_severity(3)
sess_options = ort.SessionOptions()
sess_options.intra_op_num_threads = 4   # 根据 CPU 核心数调整
sess_options.inter_op_num_threads = 4
session = ort.InferenceSession("building_best_quantized.onnx", sess_options, providers=['CPUExecutionProvider'])
# 原始模型
model_pt = YOLO("building_best.pt")
# 量化模型
model_onnx = YOLO("building_best_quantized.onnx", task="detect")

# 测试图片（请替换为实际图片路径）
img = "D:\image004.jpg"

# 计时
start = time.time()
res_pt = model_pt(img)
pt_time = (time.time() - start) * 1000

start = time.time()
res_onnx = model_onnx(img)
onnx_time = (time.time() - start) * 1000

print(f"原始 PyTorch 模型耗时: {pt_time:.2f} ms")
print(f"量化 ONNX 模型耗时: {onnx_time:.2f} ms")
print(f"加速比: {pt_time / onnx_time:.2f}x")