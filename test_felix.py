import sys
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

print("\nWaking up Fix-It Felix...")
client = QdrantClient(location=":memory:") 
print("   [OK] Connection Established (Running in RAM).")

COLLECTION_NAME = "fix_it_felix_memory"
print(f"Creating internal memory bank: '{COLLECTION_NAME}'...")

if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )
    print("   [OK] Memory bank created!")
else:
    print("   [OK] Memory bank found.")

print("Saving test data...")
client.upsert(
    collection_name=COLLECTION_NAME,
    points=[
        PointStruct(
            id=1,
            vector=[0.1] * 768, 
            payload={"status": "ONLINE", "message": "I CAN FIX IT!"}
        )
    ]
)

print("Reading back data...")
result = client.retrieve(collection_name=COLLECTION_NAME, ids=[1])

if result:
    print(f"   [SUCCESS] System Online. Message received: '{result[0].payload['message']}'")
    print("   [DONE] Day 1 Complete. Go to sleep.")
else:
    print("   [FAIL] Memory write error.")