from qdrant_client import QdrantClient, models

class MemorySystem:
    def __init__(self, path="qdrant_db"):
        self.client = QdrantClient(path=path)
        self.collection = "rail_safety_logs"
        
        # Ensure collection exists
        if not self.client.collection_exists(self.collection):
            print(f"🔨 Creating collection '{self.collection}'...")
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config={
                    "fast_lane": models.VectorParams(size=1536, distance=models.Distance.COSINE),
                    "offline_lane": models.VectorParams(size=768, distance=models.Distance.COSINE),
                }
            )
            print(f"✅ Collection '{self.collection}' created successfully.")

    
    def _pad_vector(self, vector, target_dim):
        """Pads vector with zeros to reach target_dim."""
        current = len(vector)
        if current < target_dim:
            return vector + [0.0] * (target_dim - current)
        return vector[:target_dim]

    def save_incident(self, vector, mode, payload):
        """Saves data into the correct lane based on the Mode."""
        lane = "offline_lane" if mode == 3 else "fast_lane"
        target_dim = 768 if mode == 3 else 1536
        
        # Pad vector to match the lane configuration
        final_vector = self._pad_vector(vector, target_dim)
        
        self.client.upsert(
            collection_name=self.collection,
            points=[
                models.PointStruct(
                    id=payload.get("id"),
                    vector={lane: final_vector},
                    payload=payload
                )
            ]
        )

    def search_similar(self, query_vector, mode, limit=5):
        """Searches using Binary Optimization + Rescoring."""
        lane = "offline_lane" if mode == 3 else "fast_lane"
        target_dim = 768 if mode == 3 else 1536
        
        final_query = self._pad_vector(query_vector, target_dim)
        
        # Use query_points for compatibility
        return self.client.query_points(
            collection_name=self.collection,
            query=final_query,
            using=lane,
            limit=limit,
            search_params=models.SearchParams(
                quantization=models.QuantizationSearchParams(
                    rescore=True
                )
            )
        ).points