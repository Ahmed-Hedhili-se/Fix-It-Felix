from ultralytics import YOLO
import os

# --- CONFIGURATION ---
# We use the model file sitting in your root directory
MODEL_PATH = "yolo11n.pt"  
DATA_YAML = "datasets/training_vision/data.yaml"
EPOCHS = 5  # Quick training run (increase to 50 later if you want smarter results)

def train_vision_model():
    # 1. Load the YOLO11 model
    if os.path.exists(MODEL_PATH):
        print(f"🚀 Loading local model: {MODEL_PATH}...")
        model = YOLO(MODEL_PATH)
    else:
        print(f"⬇️ Local model not found. Downloading YOLO11n...")
        model = YOLO("yolo11n.pt")
    
    # 2. Check for the data config
    if not os.path.exists(DATA_YAML):
        print(f"❌ Critical Error: {DATA_YAML} not found.")
        print("   Did you create the data.yaml file earlier?")
        return

    print("🚂 Starting Training Loop with YOLO11...")
    
    # 3. Train the model
    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        imgsz=640,
        batch=8,       # Keep batch size low for laptops
        name='rail_defect_model_v11'
    )
    
    print("✅ Training Complete!")
    print(f"💾 Your new AI brain is saved at: {results.save_dir}/weights/best.pt")

if __name__ == "__main__":
    train_vision_model()