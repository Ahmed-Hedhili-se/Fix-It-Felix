import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.memory import MemorySystem
import uuid
def simulate_test():
    memory = MemorySystem(path="qdrant_db")
    print(" Memory System Connected.")
    fake_siglip_vector = np.random.randn(768)
    fake_siglip_vector /= np.linalg.norm(fake_siglip_vector)
    incident_id = str(uuid.uuid4())
    payload = {
        "id": incident_id,
        "status": "Simulated Rail Test",
        "mode": "offline"
    }
    print(f" Saving 768-dim vector to 'offline_lane'...")
    memory.save_incident(fake_siglip_vector.tolist(), mode=3, payload=payload)
    print(" Testing Binary-Optimized Search...")
    results = memory.search_similar(fake_siglip_vector.tolist(), mode=3, limit=1)
    if results:
        print(f" SUCCESS! Found match with score: {results[0].score:.4f}")
    else:
        print(" Search failed.")
if __name__ == "__main__":
    simulate_test()