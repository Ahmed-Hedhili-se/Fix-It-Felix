import os
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModel
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

DATASET_PATH = "data"        
COLLECTION_NAME = "rail_lines" 
MODEL_ID = "google/siglip-base-patch16-224"

print("Starting: Bulk Perception Layer...")

print(f"Loading SigLIP model: {MODEL_ID}...")
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModel.from_pretrained(MODEL_ID)
print("   [OK] Model Loaded.")

client = QdrantClient(path="rail_db")
print(f"Connected to '{COLLECTION_NAME}'.")

def get_embedding(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model.get_image_features(**inputs)
        image_vector = outputs / outputs.norm(p=2, dim=-1, keepdim=True)
        return image_vector[0].tolist()
    except Exception as e:
        print(f"   [!] Error reading {image_path}: {e}")
        return None

def determine_metadata(filename, folder_name):
    lower_name = (filename + folder_name).lower()
    
    if "broken" in lower_name or "crack" in lower_name:
        return "CRITICAL", "STOP_TRAIN"
    elif "snow" in lower_name or "ice" in lower_name:
        return "WARNING", "SLOW_DOWN"
    elif "obstruction" in lower_name:
        return "CRITICAL", "EMERGENCY_BRAKE"
    else:
        return "OK", "PROCEED"

points_batch = []
total_counter = 0

print(f"Scanning folder: {DATASET_PATH}...")

for root, dirs, files in os.walk(DATASET_PATH):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(root, file)
            folder_name = os.path.basename(root)
            
            vector = get_embedding(file_path)
            
            if vector:
                status, action = determine_metadata(file, folder_name)
                
                payload = {
                    "filename": file,
                    "folder": folder_name,
                    "status": status,
                    "recommended_action": action
                }
                
                points_batch.append(PointStruct(
                    id=total_counter, 
                    vector=vector, 
                    payload=payload
                ))
                
                print(f"   [+] Processed: {file} ({status})")
                total_counter += 1

            if len(points_batch) >= 50:
                client.upsert(collection_name=COLLECTION_NAME, points=points_batch)
                points_batch = []
                print("Batch saved to Qdrant.")

if points_batch:
    client.upsert(collection_name=COLLECTION_NAME, points=points_batch)
    print("Final batch saved.")

print(f"\nDONE! Ingested {total_counter} images into the optimized brain.")