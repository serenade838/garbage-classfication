import os
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import ultralytics.nn.tasks  # 引入模型类



# 模型路径（根据你的实际位置调整）
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "best.pt")

# 类别名称（按模型训练时的索引，与 garbage.yaml 一致）
CLASS_NAMES = {
    0: "可回收物",   # recycle
    1: "有害垃圾",   # hazardous
    2: "厨余垃圾",   # kitchen
    3: "其他垃圾"    # other
}

# 阈值
CONF_THRESH = 0.3

# 全局模型实例（只加载一次）
_model = None

def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"模型文件不存在: {MODEL_PATH}")
        _model = YOLO(MODEL_PATH)
    return _model

def predict_image(image: Image.Image):
    """
    输入 PIL Image，返回检测结果
    返回格式: List[dict] 包含 x1,y1,x2,y2,confidence,class_id,class_name
    """
    model = load_model()
    # PIL -> OpenCV (BGR)
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    results = model(img_cv, conf=CONF_THRESH)
    detections = []
    for r in results:
        boxes = r.boxes
        if boxes is None:
            continue
        for box in boxes:
            x1, y1, x2, y2 = map(float, box.xyxy[0])
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            detections.append({
                "x1": round(x1, 2),
                "y1": round(y1, 2),
                "x2": round(x2, 2),
                "y2": round(y2, 2),
                "confidence": round(conf, 3),
                "class_id": cls_id,
                "class_name": CLASS_NAMES.get(cls_id, "未知")
            })
    return detections