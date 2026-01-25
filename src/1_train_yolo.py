from ultralytics import YOLO
import os
MODEL_PATH = "yolo11n.pt"  
DATA_YAML = "datasets/training_vision/data.yaml"
EPOCHS = 5  
def train_vision_model():
    if os.path.exists(MODEL_PATH):
        print(f" Loading local model: {MODEL_PATH}...")
        model = YOLO(MODEL_PATH)
    else:
        print(f" Local model not found. Downloading YOLO11n...")
        model = YOLO("yolo11n.pt")
    if not os.path.exists(DATA_YAML):
        print(f" Critical Error: {DATA_YAML} not found.")
        print("   Did you create the data.yaml file earlier?")
        return
    print(" Starting Training Loop with YOLO11...")
    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        imgsz=640,
        batch=8,       
        name='rail_defect_model_v11'
    )
    print(" Training Complete!")
    print(f" Your new AI brain is saved at: {results.save_dir}/weights/best.pt")
if __name__ == "__main__":
    train_vision_model()