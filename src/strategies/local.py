import numpy as np
from ultralytics import YOLO
from src.strategies.cloud import InferenceStrategy 
try:
    print("Loading Local YOLO model...")
    model = YOLO("yolo11n.pt") 
except Exception as e:
    print(f"Warning: YOLO model not found. Please ensure 'yolo11n.pt' is in root. {e}")
    model = None
def to_binary(vector):
    return (np.array(vector) > 0).astype(int).tolist()
class PrivateStrategy(InferenceStrategy):
    def process(self, image_path: str, incident_id: str):
        if not model:
            return {"error": "YOLO model not loaded"}
        results = model(image_path)
        detections = []
        for r in results:
            for c in r.boxes.cls:
                detections.append(model.names[int(c)])
        fake_local_vector = np.random.rand(768).tolist()
        optimized_vector = fake_local_vector[:128]
        return {
            "mode": "3-PrivateLocal",
            "source": "Local CPU/GPU (YOLO)",
            "privacy": "Secure (No data left device)",
            "detections": list(set(detections)), 
            "vector_preview": optimized_vector[:5],
            "vector_full": optimized_vector 
        } 
class OfflineStrategy(InferenceStrategy):
    def process(self, image_path: str, incident_id: str):
        if not model:
            return {"error": "YOLO model not loaded"}
        results = model(image_path)
        detections = [model.names[int(c)] for r in results for c in r.boxes.cls]
        fake_local_vector = np.random.randn(768).tolist() 
        binary_vector = to_binary(fake_local_vector)
        return {
            "mode": "4-OfflineBinary",
            "source": "Local (Offline)",
            "storage_type": "Binary (1s and 0s)",
            "detections": list(set(detections)),
            "vector_preview": binary_vector[:10] 
        }