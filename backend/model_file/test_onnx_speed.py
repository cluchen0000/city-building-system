from ultralytics import YOLO
import time
model_onnx = YOLO("building_best.onnx", task="detect")
img = "D:\image004.jpg"
start = time.time()
_ = model_onnx(img)
print(f"ONNX (fp32) time: {(time.time()-start)*1000:.2f} ms")