import numpy as np
from ultralytics import YOLO
from src.strategies.cloud import InferenceStrategy # Import the abstract base class

# 1. LOAD MODEL ONCE
# We load this at the top level so we don't reload it for every single request (slow)
# Ensure 'yolo11n.pt' is in your root folder (fix_it_felix/)
try:
    print("Loading Local YOLO model...")
    model = YOLO("yolo11n.pt") 
except Exception as e:
    print(f"Warning: YOLO model not found. Please ensure 'yolo11n.pt' is in root. {e}")
    model = None

# --- MATH TOOLS ---
def to_binary(vector):
    """
    Mode 4 Helper: Converts a standard float vector to a Binary Vector.
    Logic: Positive numbers become 1, Negative numbers become 0.
    """
    # This turns [0.5, -0.2, 0.1] into [1, 0, 1]
    return (np.array(vector) > 0).astype(int).tolist()

# --- MODE 3: PRIVACY (YOLO + Matryoshka) ---
class PrivateStrategy(InferenceStrategy):
    def process(self, image_path: str, incident_id: str):
        if not model:
            return {"error": "YOLO model not loaded"}

        # A. Vision (Local)
        results = model(image_path)
        
        # Extract class names (e.g., "person", "bicycle")
        detections = []
        for r in results:
            for c in r.boxes.cls:
                detections.append(model.names[int(c)])
        
        # B. Embedding (Local)
        # In a full production app, you would run a local embedding model here (like BERT).
        # For now, we simulate a 768-dim vector based on the detection text hash or random.
        # We simulate a "dense" float vector.
        fake_local_vector = np.random.rand(768).tolist()
        
        # C. Optimization: Matryoshka Slicing
        # We only keep the first 128 dimensions to save speed/storage
        optimized_vector = fake_local_vector[:128]

        return {
            "mode": "3-PrivateLocal",
            "source": "Local CPU/GPU (YOLO)",
            "privacy": "Secure (No data left device)",
            "detections": list(set(detections)), # Remove duplicates
            "vector_preview": optimized_vector[:5],
            "vector_full": optimized_vector # Added for consistency
        }

# --- MODE 4: OFFLINE (YOLO + Binary Quantization) ---
class OfflineStrategy(InferenceStrategy):
    def process(self, image_path: str, incident_id: str):
        if not model:
            return {"error": "YOLO model not loaded"}

        # A. Vision (Local)
        results = model(image_path)
        detections = [model.names[int(c)] for r in results for c in r.boxes.cls]

        # B. Embedding (Local)
        # Simulate local vector generation
        fake_local_vector = np.random.randn(768).tolist() 
        
        # C. Optimization: Binary Quantization
        # Converts heavy floats (4 bytes each) to single bits.
        # This makes the vector 32x smaller in memory.
        binary_vector = to_binary(fake_local_vector)

        return {
            "mode": "4-OfflineBinary",
            "source": "Local (Offline)",
            "storage_type": "Binary (1s and 0s)",
            "detections": list(set(detections)),
            "vector_preview": binary_vector[:10] # Output: [0, 1, 1, 0, ...]
        }