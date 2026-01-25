from ultralytics import YOLO
import cv2
import os
MODEL_PATH = r"runs/detect/rail_defect_model_v11/weights/best.pt"
class VisionSystem:
    def __init__(self):
        print(f" Loading Vision System from: {MODEL_PATH}")
        if os.path.exists(MODEL_PATH):
            self.model = YOLO(MODEL_PATH)
        else:
            print(" Error: Model not found! Did you move the 'runs' folder?")
            self.model = None
    def analyze_image(self, image_path):
        if not self.model:
            return False, "System Offline"
        results = self.model.predict(image_path, save=True, conf=0.25, verbose=False)
        detections = results[0].boxes
        if len(detections) > 0:
            return True, f" DEFECT DETECTED: {len(detections)} faults found."
        else:
            return False, " Track Clear"
if __name__ == "__main__":
    test_system = VisionSystem()
    test_dir = "datasets/training_vision/images/val"
    if os.path.exists(test_dir):
        files = os.listdir(test_dir)
        if files:
            test_img = os.path.join(test_dir, files[0])
            print(f" Scanning: {files[0]}")
            is_defect, message = test_system.analyze_image(test_img)
            print(message)
            print(" Check the 'runs/detect/predict' folder to see the result!")