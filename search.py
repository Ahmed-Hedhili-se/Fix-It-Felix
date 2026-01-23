import torch
from transformers import AutoProcessor, AutoModel
from qdrant_client import QdrantClient

MODEL_ID = "google/siglip-base-patch16-224"
COLLECTION_NAME = "railway_knowledge"

print(">> Starting Retrieval Engine...")

client = QdrantClient(path="rail_db")

processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModel.from_pretrained(MODEL_ID)

def run_search(query_text):
    print(f"\n>> ANALYZING QUERY: '{query_text}'")
    
    inputs = processor(text=[query_text], images=None, return_tensors="pt", padding="max_length")
    with torch.no_grad():
        outputs = model.get_text_features(**inputs)
    
    text_vector = outputs / outputs.norm(p=2, dim=-1, keepdim=True)
    vector_list = text_vector[0].tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector_list,
        limit=1
    ).points

    if results:
        best_match = results[0]
        status = best_match.payload['status']
        filename = best_match.payload['filename']
        score = best_match.score

        print(f"   MATCH FOUND!")
        print(f"   Image File: {filename}")
        print(f"   Confidence: {score:.4f}")
        print(f"   SYSTEM STATUS: {status}")
        
        if status == "CRITICAL":
            print("   ACTION: STOP THE TRAIN IMMEDIATELY!")
        elif status == "WARNING":
            print("   ACTION: SLOW DOWN AND INSPECT.")
        else:
            print("   ACTION: CONTINUE NORMAL SPEED.")
    else:
        print("   No memory found.")

run_search("a broken railway track")
run_search("heavy snow on tracks")
run_search("clear sunny day railway")