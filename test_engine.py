import numpy as np
from src.memory import MemorySystem  # Updated import path
import uuid

def simulate_test():
    # 1. Initialize Memory
    # The path needs to point to the root qdrant_db
    memory = MemorySystem(path="qdrant_db") 
    print("🧠 Memory System Connected.")

    # 2. Simulate SigLIP 2 Data (768 dimensions)
    fake_siglip_vector = np.random.randn(768)
    fake_siglip_vector /= np.linalg.norm(fake_siglip_vector)
    
    # 3. Save to Offline Lane (Mode 3)
    incident_id = str(uuid.uuid4())
    payload = {
        "id": incident_id,
        "status": "Simulated Rail Test",
        "mode": "offline"
    }
    
    print(f"📥 Saving 768-dim vector to 'offline_lane'...")
    memory.save_incident(fake_siglip_vector.tolist(), mode=3, payload=payload)

    # 4. Test Search (Mode 3)
    print("🔍 Testing Binary-Optimized Search...")
    results = memory.search_similar(fake_siglip_vector.tolist(), mode=3, limit=1)
    
    if results:
        print(f"✅ SUCCESS! Found match with score: {results[0].score:.4f}")
    else:
        print("❌ Search failed.")

if __name__ == "__main__":
    simulate_test()