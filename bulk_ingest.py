import os
import json
import pandas as pd
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModel
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from pypdf import PdfReader
from fastembed import TextEmbedding

DATASET_PATH = "datasets"
COLLECTION_IMAGES = "rail_safety_logs"
COLLECTION_KNOWLEDGE = "expert_knowledge"
MODEL_IMAGES = "google/siglip2-base-patch16-224"
MODEL_TEXT = "BAAI/bge-small-en-v1.5"

print(" Starting: Multimodal Ingestion Engine...")

client = QdrantClient(path="qdrant_db")

def setup_collections():

    if not client.collection_exists(COLLECTION_IMAGES):
        client.create_collection(
            collection_name=COLLECTION_IMAGES,
            vectors_config={
                "fast_lane": VectorParams(size=1536, distance=Distance.COSINE),
                "offline_lane": VectorParams(size=768, distance=Distance.COSINE)
            }
        )
        print(f" Collection '{COLLECTION_IMAGES}' ready.")

    if not client.collection_exists(COLLECTION_KNOWLEDGE):
        client.create_collection(
            collection_name=COLLECTION_KNOWLEDGE,
            vectors_config={
                "text_vector": VectorParams(size=384, distance=Distance.COSINE)
            }
        )
        print(f" Collection '{COLLECTION_KNOWLEDGE}' ready.")

setup_collections()

print(f" Loading SigLIP (Images): {MODEL_IMAGES}...")
processor = AutoProcessor.from_pretrained(MODEL_IMAGES)
model_img = AutoModel.from_pretrained(MODEL_IMAGES)

print(f" Loading FastEmbed (Text)...")
text_model = TextEmbedding(model_name=MODEL_TEXT)

def get_image_embedding(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model_img.get_image_features(**inputs)
        image_vector = outputs / outputs.norm(p=2, dim=-1, keepdim=True)
        return image_vector[0].tolist()
    except Exception as e:
        print(f"   [!] Error image {image_path}: {e}")
        return None

def ingest_images():
    print(f"  Scanning for images in {DATASET_PATH}...")
    count = 0
    points = []
    for root, _, files in os.walk(DATASET_PATH):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                path = os.path.join(root, file)
                vector = get_image_embedding(path)
                if vector:
                    lower_name = (file + root).lower()
                    status = "OK"
                    action = "PROCEED"
                    if "broken" in lower_name or "crack" in lower_name:
                        status, action = "CRITICAL", "STOP_TRAIN"
                    elif "snow" in lower_name:
                        status, action = "WARNING", "SLOW_DOWN"

                    payload = {
                        "filename": file,
                        "source": "image_dataset",
                        "path": path,
                        "status": status,
                        "recommended_action": action
                    }
                    points.append(PointStruct(id=count, vector={"offline_lane": vector}, payload=payload))
                    count += 1
                if len(points) >= 50:
                    client.upsert(COLLECTION_IMAGES, points)
                    points = []
    if points: client.upsert(COLLECTION_IMAGES, points)
    print(f" {count} images ingested.")

def ingest_documents():
    print(f" Scanning for documents in {DATASET_PATH}...")
    knowledge_points = []
    global_id = 10000

    for root, _, files in os.walk(DATASET_PATH):
        for file in files:
            path = os.path.join(root, file)
            content_list = []

            if file.endswith(".json") and "incident" in file.lower():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        text = f"Incident Type: {item.get('type')}. Description: {item.get('visual_description')}. Recommended Action: {item.get('action_taken')}"
                        content_list.append({"text": text, "metadata": item})

            elif file.endswith(".txt") and "rule" in file.lower():
                with open(path, 'r', encoding='utf-8') as f:
                    rules = [r.strip() for r in f.readlines() if r.strip() and not r.startswith("#")]
                    for r in rules:
                        content_list.append({"text": r, "metadata": {"source": "safety_rules", "type": "Regulation"}})

            elif file.endswith(".csv"):
                try:
                    df = pd.read_csv(path)
                    for _, row in df.iterrows():
                        text = " | ".join([f"{col}: {val}" for col, val in row.items()])
                        content_list.append({"text": text, "metadata": {"source": "csv_logs", "file": file}})
                except Exception as e:
                    print(f"   [!] CSV Error {file}: {e}")

            elif file.endswith(".pdf"):
                try:
                    reader = PdfReader(path)
                    for i, page in enumerate(reader.pages):
                        text = page.extract_text()
                        if text and len(text.strip()) > 20:
                            content_list.append({"text": text[:1500], "metadata": {"source": "pdf_manual", "page": i}})
                except Exception as e:
                    print(f"   [!] PDF Error {file}: {e}")

            if content_list:
                print(f"   [+] Processing {file} ({len(content_list)} entries)")
                texts = [c["text"] for c in content_list]
                vectors = list(text_model.embed(texts))

                for i, v in enumerate(vectors):
                    knowledge_points.append(PointStruct(
                        id=global_id,
                        vector={"text_vector": v.tolist()},
                        payload={
                            "content": content_list[i]["text"],
                            "metadata": content_list[i]["metadata"],
                            "file_source": file
                        }
                    ))
                    global_id += 1

                if len(knowledge_points) >= 100:
                    client.upsert(COLLECTION_KNOWLEDGE, knowledge_points)
                    knowledge_points = []

    if knowledge_points: client.upsert(COLLECTION_KNOWLEDGE, knowledge_points)
    print(f" Documents ingestion complete.")

ingest_images()
ingest_documents()
print("\n MULTIMODAL BRAIN READY!")