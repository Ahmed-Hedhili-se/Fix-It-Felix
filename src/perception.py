from ultralytics import YOLO
import cv2
import os

# --- CONFIGURATION ---
# This points to the brain you just trained
MODEL_PATH = r"runs/detect/rail_defect_model_v11/weights/best.pt"

class VisionSystem:
    def __init__(self):
        print(f"👁️ Loading Vision System from: {MODEL_PATH}")
        if os.path.exists(MODEL_PATH):
            self.model = YOLO(MODEL_PATH)
        else:
            print("❌ Error: Model not found! Did you move the 'runs' folder?")
            self.model = None

    def analyze_image(self, image_path):
        """
        Scans an image for defects.
        Returns: True if defect found, False if safe.
        """
        if not self.model:
            return False, "System Offline"

        # Run the AI on the image
        results = self.model.predict(image_path, save=True, conf=0.25, verbose=False)
        
        # Check if it found anything
        detections = results[0].boxes
        if len(detections) > 0:
            # We found a defect!
            return True, f"⚠️ DEFECT DETECTED: {len(detections)} faults found."
        else:
            return False, "✅ Track Clear"

# --- TEST IT ---
if __name__ == "__main__":
    # Let's test it on a random image from your validation set
    test_system = VisionSystem()
    
    # Grab a random image to test
    test_dir = "datasets/training_vision/images/val"
    if os.path.exists(test_dir):
        files = os.listdir(test_dir)
        if files:
            test_img = os.path.join(test_dir, files[0])
            print(f"🔎 Scanning: {files[0]}")
            is_defect, message = test_system.analyze_image(test_img)
            print(message)
            print("📸 Check the 'runs/detect/predict' folder to see the result!")