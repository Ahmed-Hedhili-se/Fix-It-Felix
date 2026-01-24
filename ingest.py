import os
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

DATA_FOLDER = "./data"
COLLECTION_NAME = "railway_knowledge"
MODEL_ID = "google/siglip-base-patch16-224"

print(">>  Starting: The Perception Layer...")

print(f">> 📥 Loading SigLIP model: {MODEL_ID}...")
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModel.from_pretrained(MODEL_ID)
print("   [OK] Model Loaded.")

print(">> 💾 Connecting to Local Storage...")
client = QdrantClient(path="rail_db") 

if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    print(f"   [OK] Created collection '{COLLECTION_NAME}'")
else:
    print(f"   [OK] Collection '{COLLECTION_NAME}' found.")

images = [f for f in os.listdir(DATA_FOLDER) if f.endswith(('.jpg', '.jpeg', '.png'))]
if not images:
    print("   [ERROR] No images found in ./data folder! Please add some.")
    exit()

print(f">> 👁️  Found {len(images)} images. Processing...")

points_to_upload = []

for idx, img_file in enumerate(images):
    img_path = os.path.join(DATA_FOLDER, img_file)
    
    try:
        image = Image.open(img_path).convert("RGB")
        
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model.get_image_features(**inputs)
        
        image_vector = outputs / outputs.norm(p=2, dim=-1, keepdim=True)
        vector_list = image_vector[0].tolist()

        status = "CRITICAL" if "broken" in img_file else ("WARNING" if "snow" in img_file else "OK")
        
        payload = {
            "filename": img_file,
            "status": status,
            "recommended_action": "STOP_TRAIN" if status == "CRITICAL" else "MONITOR"
        }

        points_to_upload.append(
            PointStruct(id=idx+1, vector=vector_list, payload=payload)
        )
        print(f"   [+] Processed: {img_file} -> Status: {status}")

    except Exception as e:
        print(f"   [!] Failed to process {img_file}: {e}")

if points_to_upload:
    print(">> 🧠 Uploading memories to Qdrant...")
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points_to_upload
    )
    print(f"   [SUCCESS] Uploaded {len(points_to_upload)} visual memories.")
    print("   [DONE] Day 2 Complete.")
else:
    print("   [FAIL] Nothing was uploaded.")